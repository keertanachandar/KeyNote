"""
Transposer wrapper for backend API
Uses existing ChordTransposer from src/
"""

import sys
from pathlib import Path

# Add parent src directory to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

from utils.transposer import ChordTransposer
from core.orchestrator import get_orchestrator


def transpose_progressions(results, preferred_key):
    """
    Transpose all progressions in results to preferred key
    
    Args:
        results: Results dict from orchestrator
        preferred_key: Target key
    
    Returns:
        Updated results dict with transposed progressions
    """
    # Get orchestrator for RAG system
    orchestrator = get_orchestrator()
    transposer = ChordTransposer(rag_system=orchestrator.rag)
    
    # Transpose all progressions
    transposed_progressions = []
    for item in results['progressions']:
        # Handle both old format (Document) and new format (dict)
        if isinstance(item, dict) and 'progression' in item:
            prog = item['progression']
            match_score = item.get('match_score', 75)
        else:
            prog = item
            match_score = 75
        
        # Get metadata
        metadata = prog.metadata if hasattr(prog, 'metadata') else prog
        
        # Transpose the progression
        transposed_data = transposer.transpose_progression_smart(
            metadata,
            preferred_key,
            use_theory=False
        )
        
        # Update metadata
        if hasattr(prog, 'metadata'):
            prog.metadata.update(transposed_data)
        else:
            prog.update(transposed_data)
        
        transposed_progressions.append({
            'progression': metadata if not hasattr(prog, 'metadata') else prog.metadata,
            'match_score': match_score
        })
    
    # Update results
    results['progressions'] = transposed_progressions
    return results


def transpose_single_progression(progression_data, target_key, use_theory=False):
    """
    Transpose a single progression
    
    Args:
        progression_data: Progression metadata dict
        target_key: Target key
        use_theory: Whether to use theory context
    
    Returns:
        Dict with transposed progression data
    """
    # Get orchestrator for RAG system
    orchestrator = get_orchestrator()
    transposer = ChordTransposer(rag_system=orchestrator.rag)
    
    # Transpose
    result = transposer.transpose_progression_smart(
        progression_data,
        target_key,
        use_theory=use_theory
    )
    
    return result

