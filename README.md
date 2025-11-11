# MUSEic 🎵

**The AI tool that turns your lyrical into a miracle**

An AI-powered chord progression assistant for songwriters using Retrieval-Augmented Generation (RAG), multi-agent orchestration (LangGraph), and advanced evaluation metrics (RAGAS).

> 📖 **[Read the Full Documentation](CERTIFICATION_CHALLENGE.md)** - Problem statement, technical architecture, evaluation results, and future roadmap.

> **[LOOM RECORDING](https://www.loom.com/share/b10c6797c2074e44b138c564405e64fa?sid=9a823227-2175-4c63-8ee9-522caddbff89)**

## What MUSEic Does

MUSEic helps independent musicians overcome the creative bottleneck of selecting chord progressions by:

1. **Analyzing lyrics** to extract mood, themes, emotional arc, and section-specific needs (verse/chorus/bridge)
2. **Tracking emotional journey** from beginning to end (e.g., "grief to acceptance," "nostalgia to celebration")
3. **Identifying emotional peaks** and providing specific harmonic suggestions for climactic moments
4. **Retrieving relevant progressions** from a curated database of 138 progressions, matched to emotional storytelling
5. **Providing section-specific recommendations** with different progressions for verses vs. choruses vs. bridges
6. **Searching current trends** via Tavily to find contemporary artists using similar progressions
7. **Retrieving music theory** explanations from PDF textbooks to explain *why* progressions work
8. **Synthesizing personalized recommendations** that combine emotional arc, section needs, historical patterns, and educational context

### Key Features

- 🎵 **Multi-Agent LangGraph Pipeline**: 5-node sequential workflow (lyrics analysis → progression search → web search → theory retrieval → synthesis)
- 🎭 **Enhanced Emotional Arc Analysis**: Tracks emotional journey (e.g., "heartbreak to hope"), provides section-specific recommendations (verse/chorus/bridge), works with full songs or snippets
- 🎯 **Smart Match Scoring**: Each progression option shows a percentage match (50-100%) based on mood, genre, energy, and lyrical analysis
- 📑 **Multiple Options**: Browse 6+ chord progression alternatives with interactive tabs - click through to find your perfect match
- 🎹 **Interactive Chord Player**: Listen to progressions with 4 instruments (piano, guitar, synth, pad), select specific chords, loop continuously, adjust tempo - perfect for finding your ideal sound
- 🎼 **Key Transposition**: Automatically transpose all progressions to your preferred singing key with real-time adjustment - no more struggling with uncomfortable vocal ranges
- 🔍 **Enhanced Web Search (Tavily)**: Multi-faceted search including artist-specific songwriting styles, current genre trends (2024), emotional arc matching, and production techniques
- 🔍 **Advanced Retrieval**: Metadata filtering, query expansion, contextual reranking, hybrid search, dynamic k-value, emotional arc matching
- 📊 **RAGAS Evaluation**: Faithfulness (0.773), Answer Relevancy (0.922), Context Precision (0.734), Context Recall (0.646)
- 🎸 **Interactive Streamlit UI**: User-friendly interface with comprehensive lyrics analysis display (structure, peaks, section recommendations)
- 📚 **Music Theory Integration**: Retrieves explanations from 10 PDF documents (theory books, chord guides)

## Project Structure

```
MUSEic/
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
│       ├── progressions.json      # 138 progressions with metadata (JSON format)
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

- **Python 3.10+** (Python 3.11 or 3.13 recommended)
- **pip** or **uv** package manager
- **Poppler** (required for PDF vision processing)

### Installation

#### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/keynote.git
cd MUSEic
```

#### Step 2: Install Poppler (Required for PDF Vision Processing)

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

**Windows:**
1. Download from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to `C:\Program Files\poppler`
3. Add `C:\Program Files\poppler\Library\bin` to your PATH

#### Step 3: Set Up Python Environment

**Option A: Using pip (Recommended for most users)**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Option B: Using uv (Faster alternative)**
```bash
# Install uv if you don't have it
pip install uv

# uv will auto-create virtual environment and install dependencies
uv sync
```

#### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# On macOS/Linux:
touch .env

# On Windows:
type nul > .env
```

Add your API keys to `.env`:
```bash
# REQUIRED - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-api-key-here

# OPTIONAL - For web search (get from https://tavily.com/)
TAVILY_API_KEY=tvly-your-tavily-api-key-here

# OPTIONAL - For LangSmith monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key-here
```

**Important:** Never commit your `.env` file to git (it's already in `.gitignore`)

#### Step 5: Verify Installation

Check that data files exist:
```bash
# Should show progressions.csv
ls data/theorytab/

# Should show 10 PDF files
ls data/pdfs/
```

## Performance Optimizations 🚀

MUSEic includes intelligent caching and persistent storage to dramatically reduce initialization time and API costs:

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

MUSEic uses **GPT-4 Vision** to extract content from:
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
MUSEic/
├── cache/
│   └── processed_pdfs/
│       ├── processed_documents.json  # Cached PDF content
│       └── pdf_hashes.json          # File change detection
└── vectorstore/                     # Persistent Qdrant storage
    ├── collection/
    ├── museic_pdfs/                 # PDF embeddings
    └── museic_progressions/         # Progression embeddings
```

## 🚀 Running MUSEic

### Run the Streamlit App

Make sure your virtual environment is activated, then run:

```bash
# Ensure you're in the MUSEic directory
cd /path/to/MUSEic

# Activate virtual environment if not already active
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Run the Streamlit app
streamlit run src/app.py
```

**The app will automatically:**
1. Start a local web server
2. Open your browser to `http://localhost:8501`
3. Load PDFs (first run: 2-5 min with vision API, subsequent: <5 sec from cache)
4. Initialize the RAG system with persistent vectorstores

**Troubleshooting:**
- If `streamlit` command not found: `pip install streamlit`
- If port 8501 is busy: `streamlit run src/app.py --server.port 8502`
- If browser doesn't open: manually navigate to `http://localhost:8501`

---

### Using the App

**Provide Either Description OR Lyrics (or both for best results):**

**Option 1: Description Only**
- Mood/genre: "melancholic indie folk, slow tempo"
- Reference artists (optional): "Phoebe Bridgers, Bon Iver"

**Option 2: Lyrics Only**
```
Walking through the empty streets at dawn
Everything reminds me that you're gone
The coffee shop where we used to meet
Now just echoes of memory
```

**Option 3: Both Description + Lyrics (Recommended)**
- Description helps with genre/mood
- Lyrics enable emotional arc analysis

**Tips:**
- ✅ Works with any amount of lyrics (single line, verse, or full song)
- ✅ More lyrics = better emotional arc analysis
- ✅ Section-specific recommendations if you provide multiple verses
- ✅ Lyrics-only input automatically analyzed for mood and genre

**Click "Generate Chord Progressions" to get:**
- 📝 **Lyrics Analysis** - Emotional arc, song structure, peaks
- 🎯 **Multiple Progression Options** - 6+ alternatives with match scores (75-95%)
- 📑 **Interactive Tabs** - Click through each option to explore
- 💡 **Match Explanations** - See why each progression fits your song
- 📚 **Famous Examples** - Songs that used these progressions
- 🎓 **Music Theory** - Detailed AI analysis of why progressions work

---

### First Run vs. Subsequent Runs

**First Run (~2-5 minutes):**
- Processes PDFs with GPT-4 Vision (extracts diagrams, chord charts)
- Embeds documents with OpenAI API
- Saves everything to cache/vectorstore for future use

**Subsequent Runs (<10 seconds):**
- Loads from cache (no PDF processing)
- Loads from vectorstore (no re-embedding)
- Ready to use immediately!

---

### Example Sessions

**Example 1: Description + Lyrics (Best Results)**
```
📝 Input:
Description: "melancholic indie folk building to hope"
Artists: "Phoebe Bridgers, Bon Iver"
Lyrics: [Full verse or song]

✓ Results:
📊 Emotional Arc: "grief transitioning to acceptance and hope"

🎵 6 Progression Options (click through tabs):
   Option 1 (92% match) 🎯 Excellent Match
   ├─ vi-IV-I-V (Am-F-C-G)
   ├─ ✓ Matches your melancholic mood
   ├─ ✓ Perfect for indie folk genre
   └─ ✓ Supports your emotional journey
   
   Option 2 (88% match) ✨ Great Match
   ├─ I-V-vi-IV (C-G-Am-F)
   └─ Popular in emotional indie songs
   
   Option 3 (85% match) ✨ Great Match
   Option 4 (78% match) 👍 Good Match
   [... and 2 more options]

📚 Famous Examples: Bon Iver, Fleet Foxes, The National
🎓 Detailed AI analysis with music theory explanations
```

**Example 2: Lyrics Only (Automatically Analyzed)**
```
📝 Input:
Lyrics:
"Walking through the empty streets at dawn
Everything reminds me that you're gone
But somewhere in the silence I can hear
A whisper telling me you're still near"

✓ Results:
📊 Detected Mood: melancholic, reflective, hopeful
📊 Emotional Arc: "loss moving toward comfort"
🎵 Recommended Progressions automatically matched to lyrical themes
```

**Example 3: Description Only (Quick Genre-Based)**
```
📝 Input:
Description: "upbeat summer pop anthem"
Artists: "Taylor Swift, Olivia Rodrigo"

✓ Results:
🎵 Pop-focused progressions (I-V-vi-IV, I-IV-V, etc.)
📚 Historical Examples from pop hits
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

MUSEic uses a sequential 5-node pipeline orchestrated by LangGraph:

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

1. **Chord Progression Database**: 138 progressions with metadata (genre, mood, frequency, example songs)
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
- High-quality curated data (138 progressions with rich metadata)
- Small dataset where semantic embeddings work well
- OpenAI embeddings naturally capture musical concepts

Full results: `src/evaluation/advanced_retrieval_comparison.csv`

## Troubleshooting

**Issue: ModuleNotFoundError**
```bash
# Make sure you're in the project root and dependencies are installed
cd /path/to/MUSEic
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
