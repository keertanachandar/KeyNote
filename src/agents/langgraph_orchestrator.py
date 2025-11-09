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
        results = self.rag.search_progressions(query, k=5)
        state["progressions"] = results
        print(f"   ✓ Found {len(results)} progressions")
        
        return state
    
    def web_search_node(self, state: GraphState) -> GraphState:
        """Node 3: Search current trends with Tavily"""
        print("🔍 Node 3: Searching current trends...")
        
        # Build Tavily query
        query = state["user_input"]
        if state.get("reference_artists"):
            query = f"{state['reference_artists']} {query}"
        query += " chord progressions 2025"
        
        # Search
        results = self.tavily.search_current_examples(query, max_results=3)
        state["current_examples"] = results
        print(f"   ✓ Found {len(results)} current examples")
        
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
        
        context += "=== HISTORICAL PROGRESSIONS ===\n"
        for i, prog in enumerate(state["progressions"], 1):
            context += f"{i}. {prog.metadata['progression_roman']} "
            context += f"({prog.metadata['chords_example']})\n"
            context += f"   Mood: {prog.metadata['mood']}\n"
            context += f"   Examples: {prog.metadata.get('example_songs', '')[:100]}\n\n"
        
        if state["current_examples"]:
            context += "=== CURRENT TRENDS ===\n"
            for ex in state["current_examples"][:2]:
                context += f"- {ex['title']}: {ex['content'][:150]}\n\n"
        
        if state["theory_context"]:
            context += "=== MUSIC THEORY CONTEXT ===\n"
            for t in state["theory_context"]:
                context += f"{t.page_content[:300]}\n\n"
        
        # Generate enhanced synthesis with section-specific guidance
        prompt = f"""Based on this comprehensive context, provide personalized chord progression recommendations.

{context}

IMPORTANT: The lyrics analysis includes an emotional arc and section-specific needs. Use this to provide:
1. **Overall Progressions** that match the emotional journey
2. **Section-Specific Suggestions** (different progressions for verse vs chorus vs bridge if applicable)
3. **Emotional Peak Moments** - special chord treatments for high-intensity lines

For each recommendation:
1. Progression name & chords (Roman numerals and actual chords in a key like C major)
2. Which section(s) it works best for (verse/chorus/bridge) and why
3. How it supports the emotional arc and storytelling
4. Historical examples from famous songs
5. Current artists using similar progressions
6. Brief music theory explanation
7. Variations for different sections

If lyrics were analyzed, explicitly reference:
- The emotional arc journey
- Section-specific needs
- Emotional peak moments and how to harmonize them

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