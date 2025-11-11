"""
Response models for API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field("healthy", description="API status")
    version: str = Field("1.0.0", description="API version")


class ProgressionResponse(BaseModel):
    """Single chord progression response"""
    progression_roman: str
    chords_example: str
    original_key: Optional[str] = None
    genres: Optional[str] = None
    frequency: Optional[str] = None
    example_songs: Optional[str] = None
    match_score: Optional[int] = 75


class LyricsAnalysisResponse(BaseModel):
    """Lyrics analysis response"""
    overall_mood: Optional[str] = None
    overall_genre: Optional[str] = None
    overall_energy: Optional[str] = None
    overall_themes: Optional[List[str]] = None
    emotional_arc: Optional[str] = None
    song_structure: Optional[List[Dict[str, Any]]] = None
    emotional_peaks: Optional[List[Dict[str, Any]]] = None
    section_specific_recommendations: Optional[Dict[str, str]] = None
    is_partial: bool = False
    snippet_type: str = "full_song"


class GenerateResponse(BaseModel):
    """Response model for chord progression generation"""
    progressions: List[Dict[str, Any]] = Field(..., description="Generated chord progressions")
    lyrics_analysis: Optional[Dict[str, Any]] = Field(None, description="Lyrics analysis")
    theory_context: Optional[List[str]] = Field(None, description="Music theory context")
    current_examples: Optional[List[Dict[str, str]]] = Field(None, description="Web search results")
    synthesis: Optional[str] = Field(None, description="AI synthesis")
    
    class Config:
        schema_extra = {
            "example": {
                "progressions": [
                    {
                        "progression": {
                            "progression_roman": "I - V - vi - IV",
                            "chords_example": "C - G - Am - F",
                            "genres": "pop, rock",
                            "frequency": "very_common"
                        },
                        "match_score": 85
                    }
                ],
                "lyrics_analysis": {
                    "overall_mood": "melancholic",
                    "overall_genre": "indie folk"
                }
            }
        }


class TransposeResponse(BaseModel):
    """Response model for chord transposition"""
    progression_roman: str
    chords_example: str
    original_chords: str
    original_key: str
    target_key: str
    
    class Config:
        schema_extra = {
            "example": {
                "progression_roman": "I - V - vi - IV",
                "chords_example": "D - A - Bm - G",
                "original_chords": "C - G - Am - F",
                "original_key": "C",
                "target_key": "D"
            }
        }

