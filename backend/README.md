# MUSEic Backend API

**The AI tool that turns your lyrical into a miracle**

FastAPI backend for MUSEic chord progression generator.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
pip install -e ..
```

### 2. Configure Environment

```bash
cp env.example .env
# Edit .env with your API keys
```

### 3. Run Locally

```bash
cd backend
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --port 8000
```

API will be available at: `http://localhost:8000`

Docs at: `http://localhost:8000/docs`

## API Endpoints

### Health Check
```
GET /api/health
```

### Generate Chord Progressions
```
POST /api/generate
```

Request body:
```json
{
  "description": "melancholic indie folk",
  "lyrics": "Verse 1:\nI remember...",
  "reference_artists": "Bon Iver",
  "preferred_key": "C",
  "vocal_range": "Medium"
}
```

### Transpose Progression
```
POST /api/transpose
```

Request body:
```json
{
  "progression_data": {
    "progression_roman": "I - V - vi - IV",
    "chords_example": "C - G - Am - F"
  },
  "target_key": "D",
  "use_theory": false
}
```

## Deployment

### Railway

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Add environment variables in Railway dashboard
5. Deploy: `railway up`

### Render

1. Create new Web Service
2. Connect GitHub repository
3. Set build command: `pip install -r backend/requirements.txt && pip install -e .`
4. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

### Docker

```bash
# Build
docker build -t museic-backend -f backend/Dockerfile .

# Run
docker run -p 8000:8000 --env-file backend/.env museic-backend
```

## Environment Variables

Required:
- `OPENAI_API_KEY`: OpenAI API key
- `TAVILY_API_KEY`: Tavily API key for web search

Optional:
- `QDRANT_URL`: Qdrant instance URL (if not using in-memory)
- `QDRANT_API_KEY`: Qdrant API key
- `CORS_ORIGINS`: Comma-separated allowed origins

## Project Structure

```
backend/
├── main.py                 # FastAPI app
├── api/
│   ├── routes/
│   │   ├── generate.py    # POST /api/generate
│   │   ├── transpose.py   # POST /api/transpose
│   │   └── health.py      # GET /api/health
│   └── models/
│       ├── request.py     # Pydantic request models
│       └── response.py    # Pydantic response models
├── core/
│   ├── orchestrator.py    # LangGraph orchestrator wrapper
│   └── transposer_wrapper.py  # Transposer wrapper
├── requirements.txt
├── Dockerfile
└── README.md
```

