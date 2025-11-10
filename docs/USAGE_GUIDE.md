# KeyNote Enhanced PDF Loader & RAG System - Usage Guide

## 🎯 What's New

### PDF Loader Updates (`src/utils/pdf_loader.py`)

1. ✅ **Vision Processing** - Uses GPT-4 Vision to analyze images, diagrams, tables
2. ✅ **Smart Chunking** - Larger chunks (1000 chars) for vision-enhanced content
3. ✅ **Local Caching** - Saves processed PDFs to `./cache/processed_pdfs/`
4. ✅ **Hash Validation** - Detects when PDFs change and invalidates cache

### RAG System Updates (`src/utils/rag_system.py`)

1. ✅ **Persistent Storage** - Qdrant collections saved to `./vectorstore/`
2. ✅ **Unified Search** - New `search_all()` method to search both PDFs and progressions
3. ✅ **Scored Search** - `search_all_with_scores()` ranks results across both stores
4. ✅ **Collection Management** - `clear_vectorstores()` to rebuild when needed

---

## 📦 Dependencies

All dependencies are in `requirements.txt`. Key additions:
- `pdf2image==1.17.0` - PDF to image conversion
- `qdrant-client==1.7.3` - Persistent vector storage

**System Dependency:**
```bash
# Install poppler for PDF to image conversion
# Mac:
brew install poppler

# Linux:
sudo apt-get install poppler-utils

# Windows:
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
```

---

## 🚀 Basic Usage

### First Time Setup (with Vision Processing)

```python
from src.utils.pdf_loader import load_music_theory_pdfs, chunk_documents
from src.utils.rag_system import ChordProgressionRAG

# Step 1: Load & process PDFs with vision (takes time first run, then cached)
print("Loading PDFs with vision processing...")
documents = load_music_theory_pdfs(
    pdf_directory="data/pdfs",
    use_cache=True,      # Use cache if available
    use_vision=True      # Enable GPT-4 Vision for images/diagrams
)

# Step 2: Smart chunking (different sizes for vision vs text-only)
pdf_chunks = chunk_documents(
    documents,
    chunk_size=500,              # For text-only pages
    chunk_overlap=50,
    vision_chunk_size=1000,      # For vision-enhanced pages
    vision_chunk_overlap=100
)

# Step 3: Initialize RAG with persistent storage
rag = ChordProgressionRAG(
    pdf_chunks=pdf_chunks,
    progressions_csv_path="data/theorytab/progressions.csv",
    use_persistent_storage=True   # Save Qdrant collections to disk
)
```

### Subsequent Runs (Lightning Fast!)

```python
from src.utils.pdf_loader import load_music_theory_pdfs, chunk_documents
from src.utils.rag_system import ChordProgressionRAG

# PDFs load from cache instantly (no reprocessing!)
documents = load_music_theory_pdfs("data/pdfs", use_cache=True, use_vision=True)
pdf_chunks = chunk_documents(documents)

# Qdrant loads from disk instantly (no re-embedding!)
rag = ChordProgressionRAG(pdf_chunks, "data/theorytab/progressions.csv", use_persistent_storage=True)
```

---

## 🔍 Search Methods

### 1. Search Only Progressions
```python
results = rag.search_progressions("sad indie folk", k=5)
```

### 2. Search Only PDFs (Music Theory)
```python
theory_results = rag.get_theory_context("circle of fifths", k=3)
```

### 3. NEW: Unified Search (Both PDFs + Progressions)
```python
# Search across everything
all_results = rag.search_all(
    query="melancholic chord progressions in minor keys",
    k=6,              # Total results
    pdf_k=3,          # From PDFs
    progression_k=3   # From progressions
)

print("PDF Results:", all_results['pdf_results'])
print("Progression Results:", all_results['progression_results'])
print("Combined:", all_results['combined_results'])
```

### 4. NEW: Scored Unified Search (Ranked by Relevance)
```python
# Get best results across both stores, sorted by score
scored_results = rag.search_all_with_scores(
    query="uplifting pop chord progressions",
    k=5
)

for doc, score in zip(scored_results['results'], scored_results['scores']):
    source = doc.metadata.get('source_type', 'unknown')
    print(f"Score: {score:.3f} | Source: {source}")
    print(f"Content: {doc.page_content[:100]}...")
    print()
```

### 5. Advanced Retrieval Techniques (Existing Methods)
```python
# Metadata filtering
results = rag.search_progressions_with_metadata_filter(
    query="energetic",
    genre="pop",
    mood="happy",
    k=5
)

# Query expansion
results = rag.search_progressions_with_query_expansion("sad ballad", k=5)

# Contextual reranking
results = rag.search_progressions_with_reranking(
    query="emotional indie",
    lyrics_analysis={'mood': 'melancholic', 'energy': 'low'},
    k=5
)

# Hybrid search (semantic + keyword)
results = rag.search_progressions_hybrid("upbeat pop rock", k=5)

# Dynamic k-value
results = rag.search_progressions_dynamic_k("I-IV-V progression", min_k=3, max_k=8)
```

---

## 🛠️ Maintenance & Utilities

### Using the Maintenance Script

```bash
# Show current storage status
python maintenance.py status

# Clear PDF cache to force reprocessing
python maintenance.py clear-cache

# Clear Qdrant vectorstores to force re-embedding
python maintenance.py clear-vectors

# Clear everything
python maintenance.py clear-all
```

### Manual Cache Management

```python
# Clear PDF cache programmatically
from src.utils.pdf_loader import clear_cache
clear_cache()

# Clear vectorstores programmatically
from src.utils.rag_system import ChordProgressionRAG
rag = ChordProgressionRAG([], "data/theorytab/progressions.csv", use_persistent_storage=True)
rag.clear_vectorstores()
```

### Skip Vision Processing (Faster, Text-Only)

```python
# Use this if you don't need vision analysis (faster)
documents = load_music_theory_pdfs(
    pdf_directory="data/pdfs",
    use_cache=True,
    use_vision=False  # Skip vision API calls
)
```

### Use In-Memory Storage (No Persistence)

```python
# Use this for testing or temporary sessions
rag = ChordProgressionRAG(
    pdf_chunks=pdf_chunks,
    progressions_csv_path="data/theorytab/progressions.csv",
    use_persistent_storage=False  # Back to in-memory
)
```

---

## 📊 Understanding the Output

### Vision-Enhanced Chunks

Chunks with vision processing will have special metadata:
```python
for chunk in pdf_chunks:
    if chunk.metadata.get('processing_method') == 'vision_enhanced':
        print(f"Page {chunk.metadata['page']} has visual content!")
        print(f"Source: {chunk.metadata['source_file']}")
        # Content includes both original text + vision analysis
```

### Search Result Metadata

```python
results = rag.search_all_with_scores("chord diagrams", k=5)

for doc in results['results']:
    print(f"Source Type: {doc.metadata.get('source_type')}")  # 'pdf' or 'progression'
    print(f"Relevance Score: {doc.metadata.get('relevance_score')}")
    
    # PDF-specific metadata
    if doc.metadata.get('source_type') == 'pdf':
        print(f"  File: {doc.metadata.get('source_file')}")
        print(f"  Page: {doc.metadata.get('page')}")
        print(f"  Has Visual: {doc.metadata.get('has_visual_content')}")
    
    # Progression-specific metadata
    elif doc.metadata.get('source_type') == 'progression':
        print(f"  Roman: {doc.metadata.get('progression_roman')}")
        print(f"  Mood: {doc.metadata.get('mood')}")
        print(f"  Genre: {doc.metadata.get('genres')}")
```

---

## 💡 Best Practices

1. **First Run**: Enable vision processing, let it build cache (takes time)
2. **Subsequent Runs**: Use cached data for instant loading
3. **When PDFs Change**: Cache auto-invalidates based on file hash
4. **When Progressions Change**: Rebuild vectorstores with `maintenance.py clear-vectors`
5. **Production**: Always use `use_persistent_storage=True` to avoid re-embedding
6. **Testing**: Use in-memory storage for faster iteration

---

## 🎵 Example: Complete Workflow

```python
from src.utils.pdf_loader import load_music_theory_pdfs, chunk_documents, clear_cache
from src.utils.rag_system import ChordProgressionRAG

# === FIRST TIME SETUP ===
print("🎵 KeyNote Setup - First Time")

# Load PDFs with vision (cached after first run)
documents = load_music_theory_pdfs("data/pdfs", use_cache=True, use_vision=True)

# Smart chunking
pdf_chunks = chunk_documents(documents)

# Initialize RAG with persistence
rag = ChordProgressionRAG(pdf_chunks, "data/theorytab/progressions.csv", use_persistent_storage=True)

# === USAGE ===
# Search for chord progressions
prog_results = rag.search_progressions("melancholic indie", k=5)

# Learn music theory
theory_results = rag.get_theory_context("what is a cadence?", k=3)

# Search everything at once
all_results = rag.search_all("minor key progressions with jazz influence", k=6)

print(f"Found {len(all_results['pdf_results'])} theory concepts")
print(f"Found {len(all_results['progression_results'])} chord progressions")

# === SUBSEQUENT RUNS (INSTANT!) ===
# Everything loads from cache/disk - no API calls needed
documents = load_music_theory_pdfs("data/pdfs", use_cache=True, use_vision=True)
pdf_chunks = chunk_documents(documents)
rag = ChordProgressionRAG(pdf_chunks, "data/theorytab/progressions.csv", use_persistent_storage=True)

# Ready to search immediately!
results = rag.search_all("your query here", k=5)
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'pdf2image'"
```bash
pip install pdf2image
```

### "Unable to get page count. Is poppler installed?"
Install poppler (see Dependencies section above)

### PDFs not reprocessing after edits
```bash
python maintenance.py clear-cache
```

### Qdrant collections out of sync
```bash
python maintenance.py clear-vectors
```

### Vision API errors
- Check `OPENAI_API_KEY` is set
- Ensure you have GPT-4 Vision access
- Try reducing image resolution in code (lower `dpi` in `convert_from_path`)

---

## 📁 File Structure

```
KeyNote/
├── src/
│   └── utils/
│       ├── pdf_loader.py       # Enhanced PDF loader
│       └── rag_system.py       # Enhanced RAG system
├── data/
│   ├── pdfs/                   # Your music theory PDFs
│   └── theorytab/
│       └── progressions.csv    # Your chord progressions
├── cache/
│   └── processed_pdfs/
│       ├── processed_documents.json
│       └── pdf_hashes.json
├── vectorstore/                # Persistent Qdrant storage
│   ├── collection/
│   └── ...
└── maintenance.py              # Maintenance utility script
```

---

## 🔗 Integration

The enhanced system is already integrated into:

✅ **Main App** (`src/app.py`) - Streamlit UI with caching & persistence  
✅ **Evaluations** (`src/evaluation/*.py`) - All RAGAS scripts updated  
✅ **Orchestrator** (`src/agents/langgraph_orchestrator.py`) - Multi-agent pipeline  

All files now use:
- `load_music_theory_pdfs(..., use_cache=True, use_vision=True)`
- `ChordProgressionRAG(..., use_persistent_storage=True)`

---

**Performance Summary:**
- **First Load:** 2-5 minutes (vision processing + embedding)
- **Subsequent Loads:** <5 seconds (cached + persisted)
- **Cache Size:** ~5-20 MB (depends on PDF content)
- **Vectorstore Size:** ~10-50 MB (depends on document count)

