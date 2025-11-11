"""
Chord transposition endpoint
"""

from fastapi import APIRouter, HTTPException
from api.models.request import TransposeRequest
from api.models.response import TransposeResponse
from core.transposer_wrapper import transpose_single_progression

router = APIRouter()

@router.post("/transpose", response_model=TransposeResponse)
async def transpose_progression(request: TransposeRequest):
    """
    Transpose a chord progression to a different key
    
    - **progression_data**: Progression metadata with chords
    - **target_key**: Target key to transpose to
    - **use_theory**: Whether to use theory context for transposition
    
    Returns transposed progression with original and new chords
    """
    try:
        result = transpose_single_progression(
            request.progression_data,
            request.target_key,
            request.use_theory
        )
        
        return TransposeResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error transposing progression: {str(e)}"
        )

