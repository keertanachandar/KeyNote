# KeyNote 🎵

**AI-powered chord progression assistant for songwriters** using Retrieval-Augmented Generation (RAG), multi-agent orchestration (LangGraph), and advanced evaluation metrics (RAGAS).

> 📖 **[Read the Full Documentation](CERTIFICATION_CHALLENGE.md)** - Problem statement, technical architecture, evaluation results, and future roadmap.

> **[LOOM RECORDING](https://www.loom.com/share/b10c6797c2074e44b138c564405e64fa?sid=9a823227-2175-4c63-8ee9-522caddbff89)**

## What KeyNote Does

KeyNote helps independent musicians overcome the creative bottleneck of selecting chord progressions by:

1. **Analyzing lyrics** to extract mood, themes, emotional arc, and section-specific needs (verse/chorus/bridge)
2. **Tracking emotional journey** from beginning to end (e.g., "grief to acceptance," "nostalgia to celebration")
3. **Identifying emotional peaks** and providing specific harmonic suggestions for climactic moments
4. **Retrieving relevant progressions** from a curated database of 69 progressions, matched to emotional storytelling
5. **Providing section-specific recommendations** with different progressions for verses vs. choruses vs. bridges
6. **Searching current trends** via Tavily to find contemporary artists using similar progressions
7. **Retrieving music theory** explanations from PDF textbooks to explain *why* progressions work
8. **Synthesizing personalized recommendations** that combine emotional arc, section needs, historical patterns, and educational context

### Key Features

- 🎵 **Multi-Agent LangGraph Pipeline**: 5-node sequential workflow (lyrics analysis → progression search → web search → theory retrieval → synthesis)
- 🎭 **Enhanced Emotional Arc Analysis**: Tracks emotional journey (e.g., "heartbreak to hope"), provides section-specific recommendations (verse/chorus/bridge), works with full songs or snippets
- 🔍 **Advanced Retrieval**: Metadata filtering, query expansion, contextual reranking, hybrid search, dynamic k-value, emotional arc matching
- 📊 **RAGAS Evaluation**: Faithfulness (0.773), Answer Relevancy (0.922), Context Precision (0.734), Context Recall (0.646)
- 🎸 **Interactive Streamlit UI**: User-friendly interface with comprehensive lyrics analysis display (structure, peaks, section recommendations)
- 📚 **Music Theory Integration**: Retrieves explanations from 10 PDF documents (theory books, chord guides)

## Project Structure

```
KeyNote/
├── maintenance.py                 # 🔧 Maintenance utility (clear caches, status)
├── test_enhanced_analysis.py      # 🧪 Test script for enhanced lyrics analysis
├── test_snippet_analysis.py       # 🧪 Test script for snippet handling
├── src/                           # Source code
│   ├── app.py                     # 🎸 Main Streamlit application (ENTRY POINT)
│   ├── agents/                    # Multi-agent components
│   │   ├── langgraph_orchestrator.py  # LangGraph 5-node pipeline
│   │   ├── lyrics_analyzer.py         # GPT-4o-mini lyrics analysis agent
│   │   └── tavily_searcher.py         # Tavily web search agent
│   ├── utils/                     # Core utilities
│   │   ├── rag_system.py              # RAG retrieval (Qdrant + OpenAI embeddings)
│   │   ├── pdf_loader.py              # PDF extraction and chunking
│   │   ├── generate_progressions.py   # GPT-4o progression generator
│   │   └── loadTabTheory.py           # Data loading helper
│   ├── evaluation/                # RAGAS evaluation scripts
│   │   ├── advanced_ragas_evaluation.py    # Advanced retrieval comparison
│   │   ├── manual_ragas_evaluation.py      # Manual test cases
│   │   ├── baseline_results.csv            # Baseline RAGAS scores
│   │   ├── advanced_retrieval_comparison.csv  # Technique comparison
│   │   └── baseline_summary.txt            # Human-readable summary
│   └── config.py                  # Configuration (if needed)
├── data/                          # Data storage
│   ├── pdfs/                      # Music theory PDFs (10 documents)
│   │   ├── chord-progression1-4.pdf
│   │   ├── music-theory-book1-5.pdf
│   │   └── harmony1.pdf
│   └── theorytab/                 # Chord progression database
│       ├── progressions.csv       # 69 progressions with metadata
│       └── generated_progressions.csv
├── pyproject.toml                 # Dependencies (LangChain, LangGraph, RAGAS, etc.)
├── uv.lock                        # Lock file (uv package manager)
├── LICENSE                        # Proprietary license
├── CERTIFICATION_CHALLENGE.md     # 📖 Full documentation
├── ENHANCED_LYRICS_ANALYSIS_UPDATE.md  # 📖 Enhanced lyrics analysis feature docs
├── SNIPPET_HANDLING.md            # 📖 How the system handles single lines and partial lyrics
├── USAGE_GUIDE.md                 # 📖 Enhanced PDF loader & RAG usage guide
├── CHANGES_SUMMARY.md             # 📖 Summary of recent updates
└── README.md                      # This file
```

## Quick Start

### Prerequisites

- **Python 3.13** (required for dependencies)
- **uv** package manager (recommended) or pip
- **Poppler** (required for PDF vision processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/keynote.git
   cd KeyNote
   ```

2. **Install Poppler (for PDF vision processing)**
   ```bash
   # macOS:
   brew install poppler

   # Ubuntu/Debian:
   sudo apt-get install poppler-utils

   # Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases
   # and add to PATH
   ```

3. **Install dependencies with uv (recommended)**
   ```bash
   # uv will auto-create virtual environment
   uv sync
   ```

   **OR with pip:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -e .
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file in project root
   touch .env
   ```

   Add the following to `.env`:
   ```bash
   # Required
   OPENAI_API_KEY=sk-your-openai-api-key-here
   
   # Optional (for web search)
   TAVILY_API_KEY=tvly-your-tavily-api-key-here
   
   # Optional (for monitoring)
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your-langsmith-api-key-here
   ```

5. **Verify data files exist**
   ```bash
   ls data/theorytab/progressions.csv  # Should exist
   ls data/pdfs/                        # Should contain 10 PDFs
   ```

## Performance Optimizations 🚀

KeyNote includes intelligent caching and persistent storage to dramatically reduce initialization time and API costs:

### PDF Processing Cache

**First Run:**
- PDFs processed with GPT-4 Vision (~2-5 minutes)
- Extracts text + analyzes diagrams, chord charts, and musical notation
- Cached to `./cache/processed_pdfs/`

**Subsequent Runs:**
- Loads from cache instantly (<5 seconds)
- Cache auto-invalidates when PDFs change (MD5 hash validation)

```bash
# Clear PDF cache to force reprocessing
python -c "from src.utils.pdf_loader import clear_cache; clear_cache()"
```

### Persistent Vector Storage

**First Run:**
- Embeds all documents with OpenAI API (~30-60 seconds)
- Creates Qdrant collections stored in `./vectorstore/`

**Subsequent Runs:**
- Loads vectorstores from disk (<5 seconds)
- No re-embedding needed, no API calls

```bash
# To rebuild vectorstores (e.g., after data changes):
python -c "from src.utils.rag_system import ChordProgressionRAG; rag = ChordProgressionRAG([], 'data/theorytab/progressions.csv', use_persistent_storage=True); rag.clear_vectorstores()"
```

### Vision Processing for PDFs

KeyNote uses **GPT-4 Vision** to extract content from:
- Chord diagrams and tablature
- Musical notation and sheet music
- Theory diagrams (circle of fifths, key relationships)
- Tables and charts

You can disable vision processing for faster (text-only) loading:
```python
# In src/app.py or evaluation scripts
docs = load_music_theory_pdfs("data/pdfs", use_cache=True, use_vision=False)
```

### Storage Structure
```
KeyNote/
├── cache/
│   └── processed_pdfs/
│       ├── processed_documents.json  # Cached PDF content
│       └── pdf_hashes.json          # File change detection
└── vectorstore/                     # Persistent Qdrant storage
    ├── collection/
    ├── keynote_pdfs/                # PDF embeddings
    └── keynote_progressions/        # Progression embeddings
```

## Running KeyNote

### 🎸 Run the Main Application (Streamlit UI)

```bash
streamlit run src/app.py
```

Then open your browser to **http://localhost:8501**

**What you'll see:**
1. Input form for song description, reference artists, and lyrics
2. Click "Generate Chord Progressions"
3. View:
   - Lyrics analysis (mood, energy, themes, suggested genre)
   - 3-5 personalized chord progression recommendations
   - Historical examples from famous songs
   - Current trends from Tavily search
   - Music theory explanations

**Example Usage:**
- **Song Description:** "melancholic indie folk, slow tempo"
- **Reference Artists:** "Phoebe Bridgers, Bon Iver"
- **Lyrics:** 
  ```
  Walking through the empty streets at dawn
  Everything reminds me that you're gone
  The coffee shop where we used to meet
  Now just echoes of memory
  ```

### 📊 Run Evaluation Scripts

**Baseline RAGAS Evaluation:**
```bash
python src/evaluation/manual_ragas_evaluation.py
```
Output: `src/evaluation/baseline_results.csv`, `src/evaluation/baseline_summary.txt`

**Advanced Retrieval Comparison:**
```bash
python src/evaluation/advanced_ragas_evaluation.py
```
Output: `src/evaluation/advanced_retrieval_comparison.csv`

This evaluates 5 retrieval techniques (baseline, metadata filtering, query expansion, reranking, hybrid, dynamic-k) using RAGAS metrics.

### 🔧 Utility Scripts

**Generate additional progressions with GPT-4o:**
```bash
python src/utils/generate_progressions.py
```
Output: `data/theorytab/generated_progressions.csv`

**Manage caches and vectorstores:**
```bash
# Show current storage status
python maintenance.py status

# Clear PDF processing cache
python maintenance.py clear-cache

# Clear Qdrant vectorstores
python maintenance.py clear-vectors

# Clear everything
python maintenance.py clear-all
```

### Development

**Format code:**
```bash
black src/
ruff check src/
```

**Run with debug logging:**
```bash
# Set in .env
LOG_LEVEL=DEBUG
streamlit run src/app.py
```

## Implementation Details

### Architecture

**Multi-Agent Pipeline (LangGraph):**

KeyNote uses a sequential 5-node pipeline orchestrated by LangGraph:

1. **Lyrics Analysis Node** (GPT-4o-mini)
   - Extracts mood, energy, themes, style indicators, suggested genre
   - Output: Structured JSON analysis

2. **Progression Search Node** (Qdrant + OpenAI embeddings)
   - Combines user query + lyrics analysis for semantic search
   - Retrieves top-5 progressions from database

3. **Web Search Node** (Tavily API)
   - Searches current music trends (2024-2025 examples)
   - Returns top-3 results with contemporary artists

4. **Theory Retrieval Node** (Qdrant PDF vectorstore)
   - Retrieves relevant music theory explanations
   - Provides educational context

5. **Synthesis Node** (GPT-4o)
   - Combines all context into personalized recommendations
   - Generates 3-5 progressions with examples, theory, and variations

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | OpenAI GPT-4o, GPT-4o-mini | Lyrics analysis, synthesis, query expansion |
| **Embeddings** | OpenAI text-embedding-3-small | Semantic search (1536d vectors) |
| **Orchestration** | LangGraph | Multi-agent workflow coordination |
| **Vector DB** | Qdrant (persistent) | Fast vector similarity search with disk storage |
| **Web Search** | Tavily API | Real-time music trend discovery |
| **Frontend** | Streamlit | Interactive Python UI |
| **Evaluation** | RAGAS | RAG quality metrics (faithfulness, relevancy, precision, recall) |
| **Data** | Pandas, PyMuPDF | CSV processing, PDF extraction |

### Data Sources

1. **Chord Progression Database**: 69 progressions with metadata (genre, mood, frequency, example songs)
2. **Music Theory PDFs**: 10 documents (5 textbooks, 4 chord guides, 1 harmony reference)
3. **Tavily Web Search**: Real-time contemporary music trends
4. **OpenAI API**: Embeddings and LLM generation

### Advanced Retrieval Techniques (Implemented)

- **Metadata Filtering**: Pre-filter by genre/mood before semantic search
- **Query Expansion**: LLM expands queries with related musical terms
- **Contextual Reranking**: LLM reranks results based on full context
- **Hybrid Search**: Combines BM25 (40%) + semantic (60%)
- **Dynamic k-value**: Adjusts retrieval count based on query specificity

## Evaluation Results

### RAGAS Baseline Metrics

| Metric | Score | Interpretation |
|--------|-------|----------------|
| **Faithfulness** | 0.773 | Good - Minimal hallucination, answers grounded in retrieved context |
| **Answer Relevancy** | 0.922 | Excellent - LangGraph synthesis directly addresses user queries |
| **Context Precision** | 0.734 | Decent - Some irrelevant results in top-k retrieval |
| **Context Recall** | 0.646 | Moderate - Occasionally misses relevant progressions |

### Advanced Retrieval Comparison

| Technique | Context Precision | Context Recall | Combined Score | Winner |
|-----------|------------------|---------------|---------------|--------|
| **Baseline** | **0.810** | **0.750** | **0.780** | ✅ **BEST** |
| Reranking | 0.782 | 0.750 | 0.766 | Close 2nd |
| Metadata Filter | 0.706 | 0.750 | 0.728 | Maintains recall |
| Query Expansion | 0.823 | 0.500 | 0.662 | High precision, low recall |
| Hybrid | 0.417 | 0.571 | 0.494 | ❌ Worst |
| Dynamic k | N/A | 0.571 | N/A | Evaluation error |

**Key Finding:** Simple baseline semantic search outperforms complex retrieval techniques due to:
- High-quality curated data (69 progressions with rich metadata)
- Small dataset where semantic embeddings work well
- OpenAI embeddings naturally capture musical concepts

Full results: `src/evaluation/advanced_retrieval_comparison.csv`

## Troubleshooting

**Issue: ModuleNotFoundError**
```bash
# Make sure you're in the project root and dependencies are installed
cd /path/to/KeyNote
uv sync  # or pip install -e .
```

**Issue: "Unable to get page count. Is poppler installed?"**
```bash
# Poppler is required for PDF-to-image conversion (vision processing)

# macOS:
brew install poppler

# Ubuntu/Debian:
sudo apt-get install poppler-utils

# Windows:
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
# Add to PATH
```

**Issue: Slow first load (2-5 minutes)**
This is normal! First run processes PDFs with GPT-4 Vision. Subsequent loads are <5 seconds thanks to caching.

**Issue: Cache/vectorstore out of sync**
```bash
# Clear all caches and rebuild
python -c "from src.utils.pdf_loader import clear_cache; clear_cache()"
rm -rf vectorstore/
# Then restart the app - everything will rebuild
```

**Issue: OpenAI API key not found**
```bash
# Check .env file exists and has OPENAI_API_KEY
cat .env
# Should contain: OPENAI_API_KEY=sk-...
```

**Issue: Streamlit won't start**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # or activate.bat on Windows
which streamlit  # Should point to project venv
streamlit run src/app.py
```

**Issue: No progressions loaded**
```bash
# Verify CSV exists
ls data/theorytab/progressions.csv
wc -l data/theorytab/progressions.csv  # Should show 70 lines (69 + header)
```

## Future Improvements

See [CERTIFICATION_CHALLENGE.md](CERTIFICATION_CHALLENGE.md) for detailed roadmap, including:
- Data expansion (69 → 200+ progressions)
- Section-specific recommendations (verse/chorus/bridge)
- Line-by-line lyric-to-chord mapping
- Enhanced lyrics analyzer with emotional peak detection
- User-configurable Tavily search
- Music theory concept extraction

## License

**Proprietary** - All Rights Reserved. See [LICENSE](LICENSE) for details.

Unauthorized copying, modification, or distribution is strictly prohibited.
