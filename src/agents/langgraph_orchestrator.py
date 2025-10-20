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
        """Node 1: Analyze lyrics if provided"""
        print("🎵 Node 1: Analyzing lyrics...")
        
        if state.get("lyrics"):
            analysis = self.lyrics_analyzer.analyze(state["lyrics"])
            state["lyrics_analysis"] = analysis or {}
            if analysis:
                print(f"   ✓ Detected mood: {analysis.get('mood')}")
        else:
            state["lyrics_analysis"] = {}
            print("   → No lyrics provided, skipping analysis")
        
        return state
    
    def progression_search_node(self, state: GraphState) -> GraphState:
        """Node 2: Search for relevant chord progressions"""
        print("📚 Node 2: Searching progressions...")
        
        # Build search query
        query = state["user_input"]
        if state["lyrics_analysis"]:
            mood = state["lyrics_analysis"].get("mood", "")
            genre = state["lyrics_analysis"].get("suggested_genre", "")
            query += f" {mood} {genre}"
        
        # Search progressions
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
        """Node 4: Retrieve music theory context"""
        print("🎓 Node 4: Retrieving theory...")
        
        # Build query
        query = state["user_input"]
        if state["lyrics_analysis"]:
            query += f" {state['lyrics_analysis'].get('mood', '')}"
        
        # Retrieve theory
        results = self.rag.get_theory_context(query, k=2)
        state["theory_context"] = results
        print(f"   ✓ Retrieved {len(results)} theory excerpts")
        
        return state
    
    def synthesis_node(self, state: GraphState) -> GraphState:
        """Node 5: Synthesize final recommendations"""
        print("✨ Node 5: Synthesizing recommendations...")
        
        # Build context
        context = f"User request: {state['user_input']}\n\n"
        
        if state["lyrics_analysis"]:
            context += f"Lyrics Analysis:\n"
            context += f"- Mood: {state['lyrics_analysis'].get('mood')}\n"
            context += f"- Energy: {state['lyrics_analysis'].get('energy')}\n"
            context += f"- Themes: {', '.join(state['lyrics_analysis'].get('themes', []))}\n\n"
        
        context += "Historical Progressions:\n"
        for i, prog in enumerate(state["progressions"], 1):
            context += f"{i}. {prog.metadata['progression_roman']} "
            context += f"({prog.metadata['chords_example']})\n"
            context += f"   Mood: {prog.metadata['mood']}\n"
            context += f"   Examples: {prog.metadata.get('example_songs', '')[:100]}\n\n"
        
        if state["current_examples"]:
            context += "Current Trends:\n"
            for ex in state["current_examples"][:2]:
                context += f"- {ex['title']}: {ex['content'][:150]}\n\n"
        
        if state["theory_context"]:
            context += "Music Theory Context:\n"
            for t in state["theory_context"]:
                context += f"{t.page_content[:300]}\n\n"
        
        # Generate synthesis
        prompt = f"""Based on this context, provide 3-5 chord progression recommendations for the songwriter.

{context}

For each progression:
1. Progression name & chords (Roman numerals and actual chords)
2. Why it fits the user's request (reference lyrics analysis if provided)
3. Historical examples from famous songs
4. Current artists using similar progressions
5. Brief music theory explanation
6. 1-2 suggested variations

Be conversational, actionable, and encouraging. Format with clear headers."""
        
        response = self.llm.invoke(prompt)
        state["final_synthesis"] = response.content
        print("   ✓ Synthesis complete!")
        
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