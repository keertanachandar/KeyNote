"""
Chord progression generation endpoint
"""

from fastapi import APIRouter, HTTPException
from api.models.request import GenerateRequest
from api.models.response import GenerateResponse
from core.orchestrator import get_orchestrator

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate_progressions(request: GenerateRequest):
    """
    Generate chord progressions based on user input
    
    - **description**: Song description (optional)
    - **lyrics**: Song lyrics (optional)
    - **reference_artists**: Reference artists for web search (optional)
    - **preferred_key**: Key to transpose progressions to
    - **vocal_range**: Vocal range for key suggestions (optional)
    
    Returns chord progressions, lyrics analysis, theory context, and web results
    """
    try:
        # Get orchestrator instance
        orchestrator = get_orchestrator()
        
        # Create query from description or default
        if not request.description and not request.lyrics:
            raise HTTPException(
                status_code=400,
                detail="Either description or lyrics must be provided"
            )
        
        query = request.description if request.description else "chord progressions for songwriting"
        
        # Generate recommendations
        results = orchestrator.generate_recommendations(
            query=query,
            lyrics=request.lyrics,
            reference_artists=request.reference_artists
        )
        
        # Transpose progressions to preferred key
        from core.transposer_wrapper import transpose_progressions
        transposed_results = transpose_progressions(
            results,
            request.preferred_key
        )
        
        # Format response
        response_data = {
            "progressions": transposed_results['progressions'],
            "lyrics_analysis": transposed_results.get('lyrics_analysis'),
            "theory_context": transposed_results.get('theory_context', []),
            "current_examples": transposed_results.get('current_examples', []),
            "synthesis": transposed_results.get('synthesis')
        }
        
        return GenerateResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating progressions: {str(e)}"
        )

