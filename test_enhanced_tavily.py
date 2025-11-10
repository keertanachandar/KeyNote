"""
Test Enhanced Tavily Searcher
Shows the different capabilities of the new search methods
"""

from src.agents.tavily_searcher import TavilySearcher
from dotenv import load_dotenv

load_dotenv()

def print_results(title, results, max_display=2):
    """Pretty print search results"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)
    
    if not results:
        print("  ⚠️  No results found")
        return
    
    for i, result in enumerate(results[:max_display], 1):
        print(f"\n  [{i}] {result.get('title', 'N/A')}")
        print(f"      URL: {result.get('url', 'N/A')}")
        content = result.get('content', '')[:200]
        print(f"      {content}...")
        print()
    
    if len(results) > max_display:
        print(f"  ... and {len(results) - max_display} more results\n")

def test_basic_vs_enhanced():
    """Compare basic search vs enhanced methods"""
    searcher = TavilySearcher()
    
    if not searcher.is_available():
        print("❌ TAVILY_API_KEY not found. Please set it in .env")
        return
    
    print("\n" + "🎵 TESTING ENHANCED TAVILY SEARCHER".center(70) + "\n")
    
    # Test scenario: User wants melancholic indie folk like Phoebe Bridgers
    test_query = "melancholic indie folk chord progressions"
    test_artist = "Phoebe Bridgers"
    test_genre = "indie folk"
    test_mood = "melancholic"
    
    # 1. OLD WAY - Basic generic search
    print("\n" + "OLD METHOD".center(70, '='))
    basic_results = searcher.search(test_query, max_results=3)
    print_results("🔍 Basic Generic Search", basic_results)
    
    # 2. NEW WAY - Artist-specific search
    print("\n" + "NEW METHODS".center(70, '='))
    artist_results = searcher.search_artist_progression_style(test_artist, k=3)
    print_results(f"🎸 Artist-Specific: {test_artist}'s Chord Style", artist_results)
    
    # 3. Genre trends
    trend_results = searcher.search_genre_trends(test_genre, year=2024, k=3)
    print_results(f"📈 Genre Trends: {test_genre} in 2024", trend_results)
    
    # 4. Emotional context
    emotional_results = searcher.search_emotional_examples(
        test_mood, 
        "heartbreak to acceptance",
        k=3
    )
    print_results("💔 Emotional Arc: Heartbreak to Acceptance", emotional_results)
    
    # 5. Production techniques
    production_results = searcher.search_production_techniques(test_genre, test_mood, k=3)
    print_results(f"🎚️  Production: How to Play {test_mood} {test_genre}", production_results)
    
    # 6. COMPREHENSIVE SEARCH - Uses multiple methods
    print("\n" + "COMPREHENSIVE MULTI-SEARCH".center(70, '='))
    
    lyrics_analysis = {
        "overall_genre": "indie folk",
        "overall_mood": "melancholic, reflective",
        "overall_themes": ["loss", "memory", "hope"],
        "emotional_arc": "grief transitioning to acceptance"
    }
    
    comprehensive = searcher.comprehensive_search(
        user_query=test_query,
        lyrics_analysis=lyrics_analysis,
        artist_references=["Phoebe Bridgers", "Bon Iver"]
    )
    
    print("\n📊 COMPREHENSIVE RESULTS BREAKDOWN:")
    print(f"  - Trends: {len(comprehensive['trends'])} results")
    print(f"  - Artist Styles: {len(comprehensive['artist_styles'])} results")
    print(f"  - Theory: {len(comprehensive['theory'])} results")
    print(f"  - Similar Songs: {len(comprehensive['similar_songs'])} results")
    print(f"  - Production: {len(comprehensive['production'])} results")
    
    print_results("📈 Trend Results", comprehensive['trends'], max_display=2)
    print_results("🎸 Artist Style Results", comprehensive['artist_styles'], max_display=2)
    print_results("🎓 Theory Results", comprehensive['theory'], max_display=2)
    
    # 7. Song breakdown example
    print("\n" + "SONG-SPECIFIC ANALYSIS".center(70, '='))
    song_results = searcher.search_song_breakdown("Motion Sickness", "Phoebe Bridgers", k=2)
    print_results("🎵 Specific Song Analysis", song_results)
    
    print("\n" + "="*70)
    print("\n✅ TEST COMPLETE\n")
    print("📊 SUMMARY:")
    print("  The enhanced searcher provides:")
    print("  ✓ Artist-specific chord progression insights")
    print("  ✓ Genre-specific trends and patterns")
    print("  ✓ Emotional arc matching")
    print("  ✓ Production technique recommendations")
    print("  ✓ Song-specific breakdowns")
    print("  ✓ Multi-faceted comprehensive search")
    print("\n  This gives much more relevant and actionable results than generic search!")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_basic_vs_enhanced()

