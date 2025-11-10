# KeyNote Vercel Deployment Plan

## Overview
Migrate KeyNote from Streamlit to Next.js/React (TypeScript) frontend on Vercel with FastAPI backend.

## Architecture

### Frontend (Vercel)
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **UI Library**: shadcn/ui + Tailwind CSS
- **State Management**: React Query for API calls
- **Audio**: Tone.js (already using this)

### Backend (Railway/Render)
- **Framework**: FastAPI
- **Language**: Python
- **Keep**: All existing RAG, LangGraph, embeddings logic
- **Add**: REST API endpoints

## Phase 1: Backend API Creation (Week 1)

### 1.1 Create FastAPI Backend Structure

```
backend/
├── main.py                 # FastAPI app
├── api/
│   ├── routes/
│   │   ├── generate.py    # POST /api/generate
│   │   ├── transpose.py   # POST /api/transpose
│   │   └── health.py      # GET /health
│   └── models/
│       ├── request.py     # Pydantic request models
│       └── response.py    # Pydantic response models
├── core/
│   ├── orchestrator.py    # Existing LangGraph
│   ├── rag.py            # Existing RAG system
│   └── transposer.py     # Existing transposer
├── requirements.txt
└── Dockerfile
```

### 1.2 API Endpoints to Create

1. **POST /api/generate**
   - Input: Song description, lyrics, artists, key preferences
   - Output: Chord progressions, analysis, theory, web results
   - Calls: LangGraphOrchestrator.generate_recommendations()

2. **POST /api/transpose**
   - Input: Progression, target key
   - Output: Transposed progression
   - Calls: ChordTransposer.transpose_progression_smart()

3. **GET /health**
   - Health check endpoint

## Phase 2: Frontend Creation (Week 2)

### 2.1 Create Next.js App

```bash
npx create-next-app@latest keynote-frontend --typescript --tailwind --app
cd keynote-frontend
npx shadcn-ui@latest init
```

### 2.2 Frontend Structure

```
keynote-frontend/
├── app/
│   ├── page.tsx           # Main page
│   ├── layout.tsx         # Root layout
│   └── api/               # API route handlers (optional proxy)
├── components/
│   ├── forms/
│   │   ├── SongInputForm.tsx
│   │   └── KeySelector.tsx
│   ├── progressions/
│   │   ├── ProgressionTabs.tsx
│   │   ├── ProgressionCard.tsx
│   │   └── ChordPlayer.tsx
│   ├── analysis/
│   │   ├── LyricsAnalysis.tsx
│   │   └── TheoryExplanation.tsx
│   └── ui/                # shadcn components
├── lib/
│   ├── api/
│   │   └── client.ts     # API client
│   └── utils/
│       └── chord-utils.ts
├── hooks/
│   ├── useGenerateProgressions.ts
│   └── useChordPlayer.ts
├── types/
│   ├── progression.ts
│   └── analysis.ts
└── public/
```

### 2.3 Key Components to Build

1. **SongInputForm.tsx**
   - Description input
   - Lyrics textarea
   - Reference artists
   - Key selector
   - Submit button

2. **ProgressionTabs.tsx**
   - Tabbed interface for multiple options
   - Match score display
   - Auto-stop on tab switch

3. **ChordPlayer.tsx**
   - Instrument selector
   - Tempo slider
   - Play/Stop/Loop controls
   - Chord selection
   - Tone.js integration

4. **LyricsAnalysis.tsx**
   - Mood, genre, themes
   - Song structure
   - Emotional peaks
   - Collapsible sections

## Phase 3: Deployment (Week 3)

### 3.1 Deploy Backend

**Option A: Railway**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Option B: Render**
1. Connect GitHub repo
2. Create new Web Service
3. Set environment variables
4. Deploy

### 3.2 Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd keynote-frontend
vercel
```

Or use Vercel dashboard:
1. Import GitHub repository
2. Framework preset: Next.js
3. Add environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

## Migration Checklist

### Backend Tasks
- [ ] Create FastAPI main.py
- [ ] Move orchestrator to backend/core/
- [ ] Move RAG system to backend/core/
- [ ] Move transposer to backend/core/
- [ ] Create API route models (Pydantic)
- [ ] Implement /api/generate endpoint
- [ ] Implement /api/transpose endpoint
- [ ] Add CORS middleware
- [ ] Add rate limiting
- [ ] Test API endpoints locally
- [ ] Create Dockerfile
- [ ] Deploy to Railway/Render
- [ ] Test deployed API

### Frontend Tasks
- [ ] Create Next.js app
- [ ] Install dependencies (shadcn, Tone.js, React Query)
- [ ] Create type definitions
- [ ] Build SongInputForm
- [ ] Build ProgressionTabs
- [ ] Build ChordPlayer (port from chord_player.py)
- [ ] Build LyricsAnalysis
- [ ] Build TheoryExplanation
- [ ] Implement API client
- [ ] Add loading states
- [ ] Add error handling
- [ ] Test locally
- [ ] Deploy to Vercel
- [ ] Test production

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
QDRANT_URL=...
QDRANT_API_KEY=...
CORS_ORIGINS=https://keynote.vercel.app
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://keynote-api.railway.app
```

## Cost Estimate

### Vercel (Frontend)
- **Free tier**: Likely sufficient
- **Pro**: $20/month if needed

### Railway/Render (Backend)
- **Hobby tier**: $5-10/month
- **Pro tier**: $20-30/month (if needed for scaling)

### APIs
- **OpenAI**: Pay per use (~$10-50/month depending on usage)
- **Tavily**: Free tier available
- **Qdrant**: Free tier or $25/month

**Total estimated**: $15-70/month

## Timeline

- **Week 1**: Backend API creation and testing
- **Week 2**: Frontend development and local testing
- **Week 3**: Deployment and production testing
- **Total**: ~3 weeks for full migration

## Quick Start Commands

I can help you with:
1. Creating the FastAPI backend structure
2. Creating the Next.js frontend scaffold
3. Porting components to React/TypeScript
4. Deployment configurations

Would you like me to start with creating the backend API structure first?

