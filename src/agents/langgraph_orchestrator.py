from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from agents.lyrics_analyzer import LyricsAnalyzer
from agents.tavily_searcher import TavilySearcher
import operator
import os
from dotenv import load_dotenv

load_dotenv()

# Define the state that flows through the graph
class GraphState(TypedDict):
    """State for the LangGraph agent pipeline"""
    user_input: str
    lyrics: str
    reference_artists: str
    lyrics_analysis: dict
    progressions: list
    current_examples: list
    web_search_details: dict  # NEW: Structured web search results
    theory_context: list
    final_synthesis: str
    messages: Annotated[Sequence[BaseMessage], operator.add]

class LangGraphOrchestrator:
    """
    LangGraph-based orchestrator for multi-agent chord progression system
    
    Graph flow:
    START → lyrics_analysis → progression_search → web_search → theory_retrieval → synthesis → END
    """
    
    def __init__(self, rag_system):
        self.rag = rag_system
        self.lyrics_analyzer = LyricsAnalyzer()
        self.tavily = TavilySearcher()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph state graph"""
        workflow = StateGraph(GraphState)
        
        # Add nodes (each node is an agent)
        workflow.add_node("lyrics_analysis", self.lyrics_analysis_node)
        workflow.add_node("progression_search", self.progression_search_node)
        workflow.add_node("web_search", self.web_search_node)
        workflow.add_node("theory_retrieval", self.theory_retrieval_node)
        workflow.add_node("synthesis", self.synthesis_node)
        
        # Define the flow
        workflow.set_entry_point("lyrics_analysis")
        workflow.add_edge("lyrics_analysis", "progression_search")
        workflow.add_edge("progression_search", "web_search")
        workflow.add_edge("web_search", "theory_retrieval")
        workflow.add_edge("theory_retrieval", "synthesis")
        workflow.add_edge("synthesis", END)
        
        return workflow.compile()
    
    def lyrics_analysis_node(self, state: GraphState) -> GraphState:
        """Node 1: Analyze lyrics if provided - Enhanced with emotional arc"""
        print("🎵 Node 1: Analyzing lyrics...")
        
        if state.get("lyrics"):
            analysis = self.lyrics_analyzer.analyze(state["lyrics"])
            state["lyrics_analysis"] = analysis or {}
            if analysis:
                mood = analysis.get('overall_mood', 'unknown')
                arc = analysis.get('emotional_arc', 'N/A')
                print(f"   ✓ Mood: {mood}")
                print(f"   ✓ Emotional arc: {arc}")
        else:
            state["lyrics_analysis"] = {}
            print("   → No lyrics provided, skipping analysis")
        
        return state
    
    def _score_progression_match(self, progression, lyrics_analysis):
        """Score how well a progression matches the lyrics analysis (0-100)"""
        if not lyrics_analysis:
            return 75  # Default score without analysis
        
        score = 0
        max_score = 0
        
        # Mood match (40 points)
        max_score += 40
        prog_mood = progression.metadata.get('mood', '').lower()
        lyric_mood = lyrics_analysis.get('overall_mood', '').lower()
        if lyric_mood in prog_mood or prog_mood in lyric_mood:
            score += 40
        elif any(word in prog_mood for word in lyric_mood.split()[:3]):
            score += 25
        
        # Genre match (30 points)
        max_score += 30
        prog_genres = progression.metadata.get('genres', '').lower()
        lyric_genre = lyrics_analysis.get('overall_genre', '').lower()
        if lyric_genre in prog_genres:
            score += 30
        elif any(word in prog_genres for word in lyric_genre.split()[:2]):
            score += 15
        
        # Energy level match (20 points)
        max_score += 20
        energy = lyrics_analysis.get('overall_energy', 'medium').lower()
        if 'high' in energy and ('uplifting' in prog_mood or 'energetic' in prog_mood):
            score += 20
        elif 'low' in energy and ('melancholic' in prog_mood or 'somber' in prog_mood):
            score += 20
        elif 'medium' in energy:
            score += 10
        
        # Popularity/Frequency (10 points)
        max_score += 10
        frequency = progression.metadata.get('frequency', 'medium').lower()
        if 'very common' in frequency or 'common' in frequency:
            score += 10
        elif 'moderate' in frequency:
            score += 5
        
        # Convert to percentage
        percentage = int((score / max_score) * 100) if max_score > 0 else 75
        return min(100, max(50, percentage))  # Clamp between 50-100
    
    def progression_search_node(self, state: GraphState) -> GraphState:
        """Node 2: Search for relevant chord progressions - Enhanced with emotional arc"""
        print("📚 Node 2: Searching progressions...")
        
        # Build enriched search query using emotional arc
        query = state["user_input"]
        if state["lyrics_analysis"]:
            mood = state["lyrics_analysis"].get("overall_mood", "")
            genre = state["lyrics_analysis"].get("overall_genre", "")
            arc = state["lyrics_analysis"].get("emotional_arc", "")
            
            # Include emotional arc in search for better storytelling matches
            query += f" {mood} {genre} {arc}"
            print(f"   → Searching with emotional context: {mood} - {arc[:50]}...")
        
        # Search progressions with enriched query
        results = self.rag.search_progressions(query, k=8)  # Get more options
        
        # Score each progression
        scored_progressions = []
        for prog in results:
            match_score = self._score_progression_match(prog, state["lyrics_analysis"])
            scored_progressions.append({
                'progression': prog,
                'match_score': match_score
            })
        
        # Sort by score (highest first)
        scored_progressions.sort(key=lambda x: x['match_score'], reverse=True)
        
        state["progressions"] = scored_progressions
        print(f"   ✓ Found {len(scored_progressions)} progressions (scored)")
        
        return state
    
    def web_search_node(self, state: GraphState) -> GraphState:
        """Node 3: Enhanced multi-faceted web search with Tavily"""
        print("🔍 Node 3: Enhanced web search...")
        
        if not self.tavily.is_available():
            print("   ⚠️  Tavily not configured, skipping web search")
            state["current_examples"] = []
            state["web_search_details"] = {}
            return state
        
        # Parse artist references
        artist_list = None
        if state.get("reference_artists"):
            artist_str = state["reference_artists"].strip()
            if artist_str:
                # Split by comma and clean up
                artist_list = [a.strip() for a in artist_str.split(",") if a.strip()]
        
        # Use comprehensive search with all available context
        try:
            results = self.tavily.comprehensive_search(
                user_query=state["user_input"],
                lyrics_analysis=state.get("lyrics_analysis"),
                artist_references=artist_list
            )
            
            # Flatten and prioritize results
            all_results = []
            
            # Priority 1: Artist-specific insights (most relevant)
            all_results.extend(results.get("artist_styles", []))
            
            # Priority 2: Genre trends (current and relevant)
            all_results.extend(results.get("trends", []))
            
            # Priority 3: Production techniques (actionable)
            all_results.extend(results.get("production", []))
            
            # Priority 4: Theory and similar songs
            all_results.extend(results.get("theory", []))
            all_results.extend(results.get("similar_songs", []))
            
            # Store top 5 for synthesis (avoid overwhelming the LLM)
            state["current_examples"] = all_results[:5]
            
            # Store structured results for advanced use
            state["web_search_details"] = results
            
            # Detailed logging
            print(f"   ✓ Found web results:")
            print(f"     - Artist styles: {len(results.get('artist_styles', []))}")
            print(f"     - Genre trends: {len(results.get('trends', []))}")
            print(f"     - Production tips: {len(results.get('production', []))}")
            print(f"     - Theory: {len(results.get('theory', []))}")
            print(f"     - Similar songs: {len(results.get('similar_songs', []))}")
            print(f"   → Using top {len(state['current_examples'])} for synthesis")
            
        except Exception as e:
            print(f"   ⚠️  Web search error: {e}")
            state["current_examples"] = []
            state["web_search_details"] = {}
        
        return state
    
    def theory_retrieval_node(self, state: GraphState) -> GraphState:
        """Node 4: Retrieve music theory context - Enhanced with section needs"""
        print("🎓 Node 4: Retrieving theory...")
        
        # Build query with emotional arc and section needs
        query = state["user_input"]
        if state["lyrics_analysis"]:
            mood = state['lyrics_analysis'].get('overall_mood', '')
            query += f" {mood}"
            
            # Add section-specific needs to query
            section_recs = state['lyrics_analysis'].get('section_specific_recommendations', {})
            if section_recs:
                chorus_needs = section_recs.get('chorus', '')
                if chorus_needs:
                    query += f" {chorus_needs[:50]}"  # Add chorus needs for better theory retrieval
        
        # Retrieve theory
        results = self.rag.get_theory_context(query, k=2)
        state["theory_context"] = results
        print(f"   ✓ Retrieved {len(results)} theory excerpts")
        
        return state
    
    def synthesis_node(self, state: GraphState) -> GraphState:
        """Node 5: Synthesize final recommendations - Enhanced with section-specific guidance"""
        print("✨ Node 5: Synthesizing recommendations...")
        
        # Build enriched context
        context = f"User request: {state['user_input']}\n\n"
        
        # Enhanced lyrics analysis with emotional arc and sections
        if state["lyrics_analysis"]:
            analysis = state["lyrics_analysis"]
            context += f"=== LYRICS ANALYSIS ===\n"
            context += f"Mood: {analysis.get('overall_mood', 'N/A')}\n"
            context += f"Energy: {analysis.get('overall_energy', 'N/A')}\n"
            context += f"Themes: {', '.join(analysis.get('overall_themes', []))}\n"
            context += f"Genre: {analysis.get('overall_genre', 'N/A')}\n"
            context += f"Emotional Arc: {analysis.get('emotional_arc', 'N/A')}\n\n"
            
            # Include emotional peaks
            peaks = analysis.get('emotional_peaks', [])
            if peaks:
                context += f"Emotional Peaks:\n"
                for peak in peaks:
                    context += f"- [{peak.get('section', 'N/A')}] \"{peak.get('line_text', '')[:80]}\"\n"
                    context += f"  Intensity: {peak.get('intensity', 'N/A')}/10\n"
                    context += f"  Suggestion: {peak.get('harmonic_suggestion', '')}\n"
                context += "\n"
            
            # Include section-specific recommendations
            section_recs = analysis.get('section_specific_recommendations', {})
            if section_recs:
                context += f"Section-Specific Needs:\n"
                for section, rec in section_recs.items():
                    if rec:
                        context += f"- {section.capitalize()}: {rec}\n"
                context += "\n"
        
        context += "=== HISTORICAL PROGRESSIONS (with match scores) ===\n"
        for i, scored_prog in enumerate(state["progressions"][:5], 1):  # Top 5 for synthesis
            prog = scored_prog['progression']
            score = scored_prog['match_score']
            context += f"{i}. {prog.metadata['progression_roman']} "
            context += f"({prog.metadata['chords_example']}) - Match: {score}%\n"
            context += f"   Mood: {prog.metadata['mood']}\n"
            context += f"   Examples: {prog.metadata.get('example_songs', '')[:100]}\n\n"
        
        # Enhanced web insights section
        if state.get("web_search_details"):
            web_details = state["web_search_details"]
            context += "=== WEB INSIGHTS ===\n"
            
            # Artist-specific insights
            if web_details.get("artist_styles"):
                context += "\nArtist Songwriting Styles:\n"
                for result in web_details["artist_styles"][:2]:
                    context += f"- {result.get('title', 'N/A')}\n"
                    context += f"  {result.get('content', '')[:200]}...\n"
                context += "\n"
            
            # Genre trends
            if web_details.get("trends"):
                context += "Current Genre Trends (2024):\n"
                for result in web_details["trends"][:2]:
                    context += f"- {result.get('title', 'N/A')}\n"
                    context += f"  {result.get('content', '')[:150]}...\n"
                context += "\n"
            
            # Production techniques
            if web_details.get("production"):
                context += "Production Techniques:\n"
                for result in web_details["production"][:1]:
                    context += f"- {result.get('title', 'N/A')}\n"
                    context += f"  {result.get('content', '')[:150]}...\n"
                context += "\n"
        elif state.get("current_examples"):
            # Fallback to flattened results if structured not available
            context += "=== CURRENT TRENDS ===\n"
            for ex in state["current_examples"][:2]:
                context += f"- {ex.get('title', 'N/A')}: {ex.get('content', '')[:150]}\n\n"
        
        if state["theory_context"]:
            context += "=== MUSIC THEORY CONTEXT ===\n"
            for t in state["theory_context"]:
                context += f"{t.page_content[:300]}\n\n"
        
        # Generate enhanced synthesis with section-specific guidance and web insights
        prompt = f"""Based on this comprehensive context, provide personalized chord progression recommendations.

{context}

IMPORTANT: 
- The lyrics analysis includes an emotional arc and section-specific needs
- Use the web insights to match actual artist styles and current trends
- Incorporate production techniques for actionable advice

Provide:
1. **Overall Progressions** that match the emotional journey
2. **Section-Specific Suggestions** (different progressions for verse vs chorus vs bridge if applicable)
3. **Emotional Peak Moments** - special chord treatments for high-intensity lines
4. **Artist Style Connections** - how recommendations match reference artists' actual techniques
5. **Production Tips** - how to voice and play these progressions

For each recommendation:
1. Progression name & chords (Roman numerals and actual chords in a key like C major)
2. Which section(s) it works best for (verse/chorus/bridge) and why
3. How it supports the emotional arc and storytelling
4. Historical examples from famous songs
5. Current artists using similar progressions (reference the web insights!)
6. Brief music theory explanation
7. Production/voicing suggestions
8. Variations for different sections

If artist-specific insights are available, explicitly connect recommendations to those artists' songwriting techniques.

Be conversational, actionable, and encouraging. Format with clear headers and sections."""
        
        response = self.llm.invoke(prompt)
        state["final_synthesis"] = response.content
        print("   ✓ Enhanced synthesis complete!")
        
        return state
    
    def generate_recommendations(self, user_input, lyrics=None, reference_artists=None):
        """
        Main entry point - runs the full LangGraph pipeline
        """
        print("\n" + "="*60)
        print("LANGGRAPH PIPELINE STARTING")
        print("="*60 + "\n")
        
        # Initialize state
        initial_state = {
            "user_input": user_input,
            "lyrics": lyrics or "",
            "reference_artists": reference_artists or "",
            "lyrics_analysis": {},
            "progressions": [],
            "current_examples": [],
            "web_search_details": {},  # NEW: Structured web search results
            "theory_context": [],
            "final_synthesis": "",
            "messages": []
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        print("\n" + "="*60)
        print("LANGGRAPH PIPELINE COMPLETE")
        print("="*60 + "\n")
        
        # Return results in expected format
        return {
            'lyrics_analysis': final_state.get('lyrics_analysis'),
            'progressions': final_state.get('progressions', []),
            'current_examples': final_state.get('current_examples', []),
            'synthesis': final_state.get('final_synthesis', '')
        }