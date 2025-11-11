"""
Request models for API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class GenerateRequest(BaseModel):
    """Request model for chord progression generation"""
    description: Optional[str] = Field(None, description="Song description")
    lyrics: Optional[str] = Field(None, description="Song lyrics")
    reference_artists: Optional[str] = Field(None, description="Reference artists")
    preferred_key: str = Field("C", description="Preferred key for transposition")
    vocal_range: Optional[str] = Field(None, description="Vocal range")
    
    class Config:
        schema_extra = {
            "example": {
                "description": "melancholic indie folk, slow tempo",
                "lyrics": "Verse 1:\nI remember the days...",
                "reference_artists": "Bon Iver, Phoebe Bridgers",
                "preferred_key": "C",
                "vocal_range": "Medium (Tenor/Mezzo)"
            }
        }


class TransposeRequest(BaseModel):
    """Request model for chord transposition"""
    progression_data: dict = Field(..., description="Progression metadata")
    target_key: str = Field(..., description="Target key")
    use_theory: bool = Field(False, description="Use theory for transposition")
    
    class Config:
        schema_extra = {
            "example": {
                "progression_data": {
                    "progression_roman": "I - V - vi - IV",
                    "chords_example": "C - G - Am - F",
                    "frequency": "very_common",
                    "genres": "pop, rock"
                },
                "target_key": "D",
                "use_theory": False
            }
        }

