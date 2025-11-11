"""
Orchestrator wrapper for backend API
Uses existing LangGraph orchestrator from src/
"""

import sys
import os
from pathlib import Path

# Add parent src directory to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

from utils.pdf_loader import load_music_theory_pdfs, chunk_documents
from utils.rag_system import ChordProgressionRAG
from agents.langgraph_orchestrator import LangGraphOrchestrator

# Global orchestrator instance (initialized once)
_orchestrator = None

def initialize_orchestrator():
    """
    Initialize the LangGraph orchestrator
    Called once on backend startup
    """
    global _orchestrator
    
    print("=" * 60)
    print("INITIALIZING KEYNOTE BACKEND")
    print("=" * 60)
    
    # Load PDFs with caching
    data_dir = project_root / "data" / "pdfs"
    docs = load_music_theory_pdfs(str(data_dir), use_cache=True, use_vision=False)
    chunks = chunk_documents(docs) if docs else []
    
    # Initialize RAG system
    progressions_path = project_root / "data" / "theorytab" / "progressions.json"
    rag = ChordProgressionRAG(
        chunks,
        str(progressions_path),
        use_persistent_storage=False
    )
    
    # Initialize orchestrator
    _orchestrator = LangGraphOrchestrator(rag)
    
    print("=" * 60)
    print("KEYNOTE BACKEND READY")
    print("=" * 60)
    
    return _orchestrator


def get_orchestrator():
    """
    Get the orchestrator instance
    Initializes if not already initialized
    """
    global _orchestrator
    
    if _orchestrator is None:
        _orchestrator = initialize_orchestrator()
    
    return _orchestrator

