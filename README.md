# KeyNote 🎵

AI-powered app that helps songwriters create hit songs using Retrieval-Augmented Generation (RAG), graph-based musical analysis, and advanced evaluation metrics.

> 📖 **[Read the Problem Statement](CERTIFICATION_CHALLENGE.md)** - Learn about the creative bottleneck independent musicians face and how KeyNote solves it.

## Features

- **RAG-Powered Retrieval**: Find and analyze chord progressions and patterns from a curated database of successful songs.
- **Advanced Retrieval Techniques**: Supports baseline retrieval, metadata filtering, query expansion, reranking, hybrid search, and dynamic-K search with side-by-side evaluation.
- **Graph Analysis**: Visualize song structure and relationships (chords, progressions, artists) using graph algorithms and tools.
- **Evaluation Framework**: Analyze faithfulness, answer relevancy, context precision, and context recall of AI-generated responses, with automated and manual test cases.
- **AI Collaboration**: Generate melody, lyrics, and progressions collaboratively with the AI.
- **Interactive UI**: Easy-to-use frontend for searching, generating, and visualizing musical concepts.

## Project Structure

```
KeyNote/
├── keynote/                       # Main application package
│   ├── backend/                   # Backend API (FastAPI)
│   │   ├── api/                   # API endpoints
│   │   ├── models/                # Database models
│   │   └── services/              # Business logic
│   ├── frontend/                  # Frontend UI (Streamlit/Gradio)
│   ├── rag/                       # RAG components: retrieval, embeddings, vector dbs
│   ├── graph/                     # Graph analytics and visualization
│   ├── ai/                        # LLM chains and prompts
│   ├── data/                      # Data cleaning and processing logic
│   └── config.py                  # App configuration
├── scripts/                       # Utility scripts (e.g., setup_db.py)
├── tests/                         # Test suite for backend, RAG, and graph
├── data/                          # Music data storage (gitignored)
├── docs/                          # Documentation
├── evaluation/                    # Evaluation scripts and result artifacts
│   ├── baseline_results.csv
│   ├── advanced_retrieval_comparison.csv
│   ├── baseline_summary.txt
│   └── advanced_ragas_evaluation.py
├── .env.example                   # Environment variables template
├── .gitignore
├── pyproject.toml                 # Project configuration
└── README.md
```

## Setup

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/keynote.git
   cd keynote
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Basic installation
   pip install -e .

   # With development dependencies
   pip install -e ".[dev]"

   # With all features (including audio processing)
   pip install -e ".[all]"
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Initialize the database** (optional)
   ```bash
   python scripts/setup_db.py
   ```

## Usage

### Run the Backend (API)

```bash
uvicorn keynote.backend.main:app --reload --host 0.0.0.0 --port 8000
```

- API available at [http://localhost:8000](http://localhost:8000)
- Docs at [http://localhost:8000/docs](http://localhost:8000/docs)

### Run the Frontend

```bash
streamlit run keynote/frontend/app.py
```

- UI available at [http://localhost:8501](http://localhost:8501)

### Run Evaluation

To compare retrieval strategies and compute metrics:
```bash
python src/evaluation/advanced_ragas_evaluation.py
# Results: src/evaluation/advanced_retrieval_comparison.csv
```
See `src/evaluation/` for metrics, test cases, and evaluation summaries.

### Development

#### Running Tests

```bash
pytest
```

#### Code Formatting

```bash
black keynote tests
ruff check keynote tests
```

#### Type Checking

```bash
mypy keynote
```

## Technologies

- **AI/LLM**: OpenAI, Anthropic, LangChain
- **Retrieval (RAG)**: ChromaDB, FAISS, Sentence Transformers
- **Graph Analysis**: Neo4j, NetworkX, PyVis
- **Backend**: FastAPI, SQLAlchemy
- **Frontend**: Streamlit, Gradio
- **Data/Evaluation**: Pandas, NumPy

## Evaluation Results (Summary)

| Technique         | Context Precision | Context Recall | Combined Score |
|-------------------|------------------|---------------|---------------|
| Baseline          | 0.81             | 0.75          | 0.78          |
| Reranking         | 0.78             | 0.75          | 0.77          |
| Metadata Filter   | 0.71             | 0.75          | 0.73          |
| Query Expansion   | 0.82             | 0.50          | 0.66          |
| Hybrid            | 0.42             | 0.57          | 0.49          |
| Dynamic K         | —                | 0.57          | —             |

Full CSV: `src/evaluation/advanced_retrieval_comparison.csv`

See also: `src/evaluation/baseline_summary.txt` for manual test case baseline.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT License – See LICENSE file for details.
