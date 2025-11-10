"""
Proposed Enhanced Tavily Integration for LangGraph Orchestrator
Copy this into langgraph_orchestrator.py if you like the enhanced search
"""

def web_search_node_enhanced(self, state: GraphState) -> GraphState:
    """
    Node 3: Enhanced multi-faceted web search with Tavily
    
    Uses comprehensive_search() to get:
    - Artist-specific chord progression styles
    - Genre trends (2024/2025)
    - Emotional arc matching
    - Production techniques
    - Theory explanations
    """
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
        
        # Store structured results for potential advanced use
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


# ===================================================================
# ALTERNATIVE: Lighter Integration (if comprehensive is too much)
# ===================================================================

def web_search_node_light_enhanced(self, state: GraphState) -> GraphState:
    """
    Lighter version: Just artist + genre trends
    """
    print("🔍 Node 3: Web search (artist + trends)...")
    
    if not self.tavily.is_available():
        state["current_examples"] = []
        return state
    
    all_results = []
    
    try:
        # 1. Artist-specific search (if provided)
        if state.get("reference_artists"):
            artists = [a.strip() for a in state["reference_artists"].split(",") if a.strip()]
            for artist in artists[:2]:  # Limit to 2 artists
                artist_results = self.tavily.search_artist_progression_style(artist, k=2)
                all_results.extend(artist_results)
        
        # 2. Genre trends (if lyrics analyzed)
        if state.get("lyrics_analysis"):
            genre = state["lyrics_analysis"].get("overall_genre", "")
            if genre:
                trend_results = self.tavily.search_genre_trends(genre, year=2024, k=2)
                all_results.extend(trend_results)
        
        # 3. Generic search as fallback
        if not all_results:
            query = state["user_input"] + " chord progressions 2025"
            all_results = self.tavily.search(query, max_results=3)
        
        state["current_examples"] = all_results[:5]
        print(f"   ✓ Found {len(state['current_examples'])} web results")
        
    except Exception as e:
        print(f"   ⚠️  Web search error: {e}")
        state["current_examples"] = []
    
    return state


# ===================================================================
# UPDATE THE SYNTHESIS NODE to leverage enhanced results
# ===================================================================

def synthesis_node_enhanced_web(self, state: GraphState) -> GraphState:
    """
    Enhanced synthesis that better uses the structured web results
    """
    print("✨ Node 5: Synthesizing recommendations...")
    
    # Build context (existing code...)
    context = f"User request: {state['user_input']}\n\n"
    
    # ... (include lyrics analysis as before) ...
    
    # Enhanced web context section
    if state.get("web_search_details"):
        web_details = state["web_search_details"]
        
        context += "=== WEB INSIGHTS ===\n"
        
        # Artist-specific insights
        if web_details.get("artist_styles"):
            context += "\nArtist Styles:\n"
            for result in web_details["artist_styles"][:2]:
                context += f"- {result.get('title', 'N/A')}\n"
                context += f"  {result.get('content', '')[:200]}\n"
        
        # Genre trends
        if web_details.get("trends"):
            context += "\nCurrent Trends:\n"
            for result in web_details["trends"][:2]:
                context += f"- {result.get('title', 'N/A')}\n"
                context += f"  {result.get('content', '')[:150]}\n"
        
        # Production techniques
        if web_details.get("production"):
            context += "\nProduction Techniques:\n"
            for result in web_details["production"][:1]:
                context += f"- {result.get('title', 'N/A')}\n"
                context += f"  {result.get('content', '')[:150]}\n"
        
        context += "\n"
    
    # ... (rest of synthesis prompt) ...
    
    # Enhanced prompt can now reference web insights
    prompt = f"""Based on this comprehensive context, provide personalized recommendations.

{context}

IMPORTANT: 
- Use the artist-specific insights to match their actual songwriting style
- Reference current trends to keep recommendations modern
- Incorporate production techniques for actionable advice
- Connect everything to the user's emotional arc

[... rest of prompt ...]
"""
    
    response = self.llm.invoke(prompt)
    state["final_synthesis"] = response.content
    return state

