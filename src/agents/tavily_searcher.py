from tavily import TavilyClient
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

class EnhancedTavilySearcher:
    """
    Enhanced Tavily search agent with specialized methods for music discovery
    """
    
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            print("⚠️  TAVILY_API_KEY not found - web search disabled")
            self.client = None
        else:
            self.client = TavilyClient(api_key=api_key)
    
    def is_available(self) -> bool:
        """Check if Tavily is configured"""
        return self.client is not None
    
    # ==================== CORE SEARCH ====================
    
    def search(self, query: str, max_results: int = 3, search_depth: str = "basic", 
               include_domains: Optional[List[str]] = None) -> List[Dict]:
        """
        Base search method with configurable parameters
        
        Args:
            query: Search query
            max_results: Number of results to return
            search_depth: "basic" or "advanced" (advanced costs more but better quality)
            include_domains: Whitelist of domains to search
        """
        if not self.is_available():
            return []
        
        try:
            params = {
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth
            }
            
            if include_domains:
                params["include_domains"] = include_domains
            
            response = self.client.search(**params)
            return response.get("results", [])
        
        except Exception as e:
            print(f"⚠️  Tavily search error: {e}")
            return []
    
    # ==================== ARTIST & STYLE DISCOVERY ====================
    
    def search_artist_progression_style(self, artist_name: str, k: int = 5) -> List[Dict]:
        """
        Search for specific artist's chord progression patterns and songwriting style
        
        Use Case: User mentions "like Phoebe Bridgers" → fetch her actual style
        """
        query = f'"{artist_name}" chord progressions songwriting techniques musical style harmony'
        
        return self.search(
            query,
            max_results=k,
            search_depth="advanced",
            include_domains=[
                "pitchfork.com",
                "musicradar.com",
                "soundonsound.com",
                "songwritingmagazine.co.uk",
                "hooktheory.com"
            ]
        )
    
    def search_artist_influences(self, artist_name: str, k: int = 3) -> List[Dict]:
        """
        Find who influenced an artist's sound (useful for discovering similar progressions)
        """
        query = f'"{artist_name}" musical influences inspired by artists similar to'
        
        return self.search(
            query,
            max_results=k,
            search_depth="basic"
        )
    
    # ==================== TREND DISCOVERY ====================
    
    def search_genre_trends(self, genre: str, year: int = 2024, k: int = 5) -> List[Dict]:
        """
        Find current trends and popular progressions in a specific genre
        
        Use Case: "What chord progressions are trending in indie folk right now?"
        """
        query = f"{genre} music trends {year} popular chord progressions songwriting production"
        
        return self.search(
            query,
            max_results=k,
            search_depth="advanced",
            include_domains=[
                "pitchfork.com",
                "billboard.com",
                "musicradar.com",
                "soundonsound.com"
            ]
        )
    
    def search_current_hits(self, genre: str, mood: str, k: int = 5) -> List[Dict]:
        """
        Find current popular songs matching genre + mood
        
        Use Case: Enhance recommendations with what's actually popular right now
        """
        query = f"{genre} {mood} songs 2024 2025 popular hits chord progressions"
        
        return self.search(
            query,
            max_results=k,
            search_depth="basic"
        )
    
    # ==================== SONG ANALYSIS ====================
    
    def search_song_breakdown(self, song_title: str, artist: str, k: int = 3) -> List[Dict]:
        """
        Find detailed breakdowns/analyses of specific songs
        
        Use Case: User says "I want something like Motion Sickness by Phoebe Bridgers"
        """
        query = f'"{song_title}" "{artist}" chord progression analysis breakdown theory'
        
        return self.search(
            query,
            max_results=k,
            search_depth="advanced",
            include_domains=[
                "hooktheory.com",
                "youtube.com",
                "ultimate-guitar.com",
                "songsterr.com",
                "musicnotes.com"
            ]
        )
    
    def search_similar_songs(self, reference_song: str, artist: str, k: int = 5) -> List[Dict]:
        """
        Find songs similar to a reference track
        
        Use Case: Collaborative filtering for progression discovery
        """
        query = f'songs similar to "{reference_song}" by {artist} chord progression style'
        
        return self.search(
            query,
            max_results=k,
            search_depth="basic"
        )
    
    # ==================== MUSIC THEORY ====================
    
    def search_theory_explanation(self, concept: str, k: int = 3) -> List[Dict]:
        """
        Search for modern explanations of music theory concepts
        
        Use Case: When PDFs don't have enough context, supplement with web
        """
        query = f"music theory {concept} explained tutorial songwriting chord progression"
        
        return self.search(
            query,
            max_results=k,
            search_depth="advanced",
            include_domains=[
                "musictheory.net",
                "musicradar.com",
                "soundonsound.com",
                "hooktheory.com",
                "youtube.com"
            ]
        )
    
    def search_theory_in_practice(self, concept: str, genre: str, k: int = 3) -> List[Dict]:
        """
        Find real-world examples of theory concepts in specific genres
        
        Use Case: Show how theory applies to user's target genre
        """
        query = f"{concept} music theory examples {genre} songs chord progressions"
        
        return self.search(
            query,
            max_results=k,
            search_depth="advanced"
        )
    
    # ==================== PRODUCTION & ARRANGEMENT ====================
    
    def search_production_techniques(self, genre: str, mood: str, k: int = 3) -> List[Dict]:
        """
        Find production techniques and instrumentation for chord progressions
        
        Use Case: Not just WHAT chords, but HOW to play them
        """
        query = f"{genre} {mood} production techniques instrumentation chord voicing arrangement"
        
        return self.search(
            query,
            max_results=k,
            search_depth="advanced",
            include_domains=[
                "soundonsound.com",
                "musicradar.com",
                "reddit.com"  # r/WeAreTheMusicMakers, r/audioengineering
            ]
        )
    
    def search_instrumentation(self, progression: str, genre: str, k: int = 3) -> List[Dict]:
        """
        Find how to instrument/voice a specific progression
        
        Use Case: User gets I-V-vi-IV, now learn how to actually play it
        """
        query = f"{progression} chord progression {genre} instrumentation voicing arrangement"
        
        return self.search(
            query,
            max_results=k,
            search_depth="basic"
        )
    
    # ==================== EMOTIONAL CONTEXT ====================
    
    def search_emotional_examples(self, mood: str, emotional_arc: str, k: int = 5) -> List[Dict]:
        """
        Find songs with similar emotional characteristics
        
        Use Case: Match emotional arc from lyrics analysis
        """
        query = f"{mood} {emotional_arc} songs emotional chord progressions examples"
        
        return self.search(
            query,
            max_results=k,
            search_depth="basic"
        )
    
    def search_mood_to_chords(self, mood_keywords: List[str], k: int = 5) -> List[Dict]:
        """
        Search for chord progressions associated with specific moods
        
        Use Case: Direct mood → chord mapping from web sources
        """
        mood_str = " ".join(mood_keywords)
        query = f"{mood_str} mood chord progressions emotional music theory"
        
        return self.search(
            query,
            max_results=k,
            search_depth="advanced"
        )
    
    # ==================== COMPREHENSIVE SEARCH ====================
    
    def comprehensive_search(self, user_query: str, lyrics_analysis: Optional[Dict] = None,
                           artist_references: Optional[List[str]] = None) -> Dict:
        """
        Perform multiple targeted searches and combine results
        
        Returns comprehensive web context for synthesis node
        Enhanced to work well even without artist references
        """
        results = {
            "trends": [],
            "artist_styles": [],
            "theory": [],
            "similar_songs": [],
            "production": []
        }
        
        if not self.is_available():
            return results
        
        # Extract info from lyrics analysis
        genre = ""
        mood = ""
        emotional_arc = ""
        
        if lyrics_analysis:
            genre = lyrics_analysis.get("overall_genre", "")
            mood = lyrics_analysis.get("overall_mood", "")
            themes = lyrics_analysis.get("overall_themes", [])
            emotional_arc = lyrics_analysis.get("emotional_arc", "")
            
            # Search genre trends (ALWAYS if genre detected)
            if genre:
                results["trends"] = self.search_genre_trends(genre, k=4)
            
            # Search mood-specific progressions (ENHANCED)
            if mood:
                mood_words = mood.split(",")[:2]  # Take first 2 mood descriptors
                results["theory"] = self.search_mood_to_chords(mood_words, k=4)
            
            # Search production techniques (ALWAYS if we have genre/mood)
            if genre and mood:
                results["production"] = self.search_production_techniques(genre, mood, k=3)
            elif genre:  # Even without mood
                results["production"] = self.search_production_techniques(genre, "emotional", k=2)
            elif mood:  # Even without genre
                results["production"] = self.search_production_techniques("indie", mood, k=2)
            
            # Search emotional examples (NEW - works without artist)
            if emotional_arc and mood:
                emotional_results = self.search_emotional_examples(mood, emotional_arc, k=3)
                results["similar_songs"].extend(emotional_results)
        
        # Search artist styles (if provided)
        if artist_references:
            for artist in artist_references[:2]:  # Limit to 2 artists
                artist_results = self.search_artist_progression_style(artist, k=2)
                results["artist_styles"].extend(artist_results)
        
        # ENHANCED: Better generic/fallback search
        if user_query:
            # Build enriched query even without artist
            enriched_query = user_query
            if genre:
                enriched_query += f" {genre}"
            if mood:
                enriched_query += f" {mood}"
            enriched_query += " chord progressions songwriting techniques 2024"
            
            generic_results = self.search(
                enriched_query, 
                max_results=4, 
                search_depth="advanced"  # Use advanced for better quality
            )
            
            # Add to similar_songs if not already populated
            if not results["similar_songs"]:
                results["similar_songs"] = generic_results
            else:
                results["similar_songs"].extend(generic_results[:2])
        
        # FALLBACK: If we have NO results at all, do broad music search
        total_results = sum(len(v) for v in results.values())
        if total_results == 0 and user_query:
            fallback = self.search(
                f"chord progressions songwriting {user_query} 2024",
                max_results=5,
                search_depth="advanced"
            )
            results["similar_songs"] = fallback
        
        return results
    
    # ==================== VALIDATION & CROSS-REFERENCE ====================
    
    def validate_theory_with_web(self, theory_concept: str, pdf_explanation: str, k: int = 3) -> Dict:
        """
        Cross-reference PDF theory content with web sources
        
        Use Case: Validate your music theory PDFs are teaching current best practices
        """
        web_results = self.search_theory_explanation(theory_concept, k=k)
        
        return {
            "theory_concept": theory_concept,
            "pdf_context": pdf_explanation,
            "web_sources": web_results,
            "validation_status": "aligned"  # Could add actual validation logic
        }


# ==================== BACKWARD COMPATIBILITY ====================

class TavilySearcher(EnhancedTavilySearcher):
    """
    Backward-compatible wrapper - keeps your existing code working
    """
    
    def search_current_trends(self, query: str, k: int = 3) -> List[Dict]:
        """
        Legacy method name for existing KeyNote code
        
        Maps to the new comprehensive_search with basic parameters
        """
        return self.search(query, max_results=k, search_depth="basic")