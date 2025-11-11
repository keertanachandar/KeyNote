# KeyNote Deployment Guide - Complete Setup

## Overview

This guide walks you through deploying KeyNote with:
- **Backend (FastAPI)** → Railway or Render
- **Frontend (Next.js)** → Vercel

## Table of Contents

1. [Backend Setup & Deployment](#backend-setup--deployment)
2. [Frontend Setup & Development](#frontend-setup--development)
3. [Frontend Deployment to Vercel](#frontend-deployment-to-vercel)
4. [Testing & Verification](#testing--verification)

---

## Backend Setup & Deployment

### Step 1: Test Backend Locally

```bash
cd backend

# Install dependencies (from project root)
cd ..
pip install -r backend/requirements.txt
pip install -e .

# Set environment variables
cd backend
cp env.example .env
# Edit .env with your API keys

# Run the backend
python main.py
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Step 2: Deploy to Railway

#### Install Railway CLI
```bash
npm install -g @railway/cli
```

#### Deploy
```bash
# From project root
railway login
railway init

# Railway will detect the Dockerfile
# Or manually set:
# Build Command: pip install -r backend/requirements.txt && pip install -e .
# Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### Add Environment Variables in Railway Dashboard
- `OPENAI_API_KEY`
- `TAVILY_API_KEY`
- `CORS_ORIGINS=https://your-app.vercel.app`

#### Deploy
```bash
railway up
```

Your backend will be at: `https://your-app.railway.app`

### Alternative: Deploy to Render

1. Go to https://render.com
2. Create new **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r backend/requirements.txt && pip install -e .`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11
5. Add environment variables
6. Deploy

---

## Frontend Setup & Development

### Step 1: Create Next.js App

```bash
# From project root
npx create-next-app@latest frontend --typescript --tailwind --app

cd frontend
```

Answer prompts:
- TypeScript: Yes
- ESLint: Yes
- Tailwind CSS: Yes
- `app/` directory: Yes
- `src/` directory: No
- App Router: Yes

### Step 2: Install Dependencies

```bash
# Core dependencies
npm install @tanstack/react-query axios tone

# UI components
npx shadcn-ui@latest init

# Add shadcn components
npx shadcn-ui@latest add button input textarea select tabs card slider badge
```

### Step 3: Copy Template Files

Copy files from `docs/frontend-templates/` to your `frontend/` directory:

1. **Types**: `types.ts` → `frontend/types/`
2. **API Client**: `api-client.ts` → `frontend/lib/api/client.ts`
3. **Hooks**: `hooks.ts` → `frontend/hooks/`
4. **Main Page**: `page.tsx` → `frontend/app/page.tsx`

### Step 4: Create Components

You'll need to create these components (see frontend-templates for structure):

#### frontend/components/forms/SongInputForm.tsx
```tsx
'use client';

import { useState } from 'react';
import { useGenerateProgressions } from '@/hooks/useGenerateProgressions';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';

export default function SongInputForm({ onResults }) {
  const [description, setDescription] = useState('');
  const [lyrics, setLyrics] = useState('');
  const [preferredKey, setPreferredKey] = useState('C');
  
  const { mutate, isLoading } = useGenerateProgressions();

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate(
      { description, lyrics, preferred_key: preferredKey },
      { onSuccess: (data) => onResults(data) }
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
      <Input
        placeholder="Song description (e.g., melancholic indie folk)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <Textarea
        placeholder="Song lyrics (optional)"
        value={lyrics}
        onChange={(e) => setLyrics(e.target.value)}
        rows={6}
      />
      <Select value={preferredKey} onValueChange={setPreferredKey}>
        {['C', 'D', 'E', 'F', 'G', 'A', 'B'].map((key) => (
          <option key={key} value={key}>{key}</option>
        ))}
      </Select>
      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? 'Generating...' : '🎵 Generate Chord Progressions'}
      </Button>
    </form>
  );
}
```

#### frontend/components/progressions/ProgressionResults.tsx
Basic structure for displaying results with tabs

#### frontend/components/progressions/ChordPlayer.tsx
Use Tone.js to play chords (similar to Python version)

### Step 5: Configure Environment

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 6: Run Development Server

```bash
npm run dev
```

App runs at: http://localhost:3000

---

## Frontend Deployment to Vercel

### Method 1: Vercel CLI

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Follow prompts:
- Set up and deploy: Yes
- Which scope: Your account
- Link to existing project: No
- Project name: keynote
- Directory: `./` (already in frontend/)
- Override settings: No

### Method 2: Vercel Dashboard

1. Go to https://vercel.com
2. Click **"New Project"**
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. Add Environment Variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-backend.railway.app`
6. Click **Deploy**

### Update CORS

After frontend deploys, update backend CORS_ORIGINS:
```
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

---

## Testing & Verification

### 1. Test Backend

```bash
# Health check
curl https://your-backend.railway.app/api/health

# Test generate (requires valid API keys)
curl -X POST https://your-backend.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{"description":"happy pop song","preferred_key":"C"}'
```

### 2. Test Frontend Locally

```bash
cd frontend
npm run dev

# Visit http://localhost:3000
# Fill in form and submit
```

### 3. Test Production

Visit your Vercel URL: `https://your-app.vercel.app`

---

## Architecture Diagram

```
┌─────────────────────────┐
│  Frontend (Vercel)      │
│  - Next.js              │
│  - React/TypeScript     │
│  - Tailwind CSS         │
│  - Tone.js              │
└───────────┬─────────────┘
            │
            │ HTTPS REST API
            │
┌───────────▼─────────────┐
│  Backend (Railway)      │
│  - FastAPI              │
│  - LangGraph            │
│  - RAG System           │
│  - OpenAI/Qdrant/Tavily │
└─────────────────────────┘
```

---

## Cost Estimate

### Monthly Costs
- **Vercel (Frontend)**: Free tier (likely sufficient)
- **Railway (Backend)**: $5-20/month
- **OpenAI API**: $10-50/month (usage-based)
- **Tavily API**: Free tier available
- **Total**: ~$15-70/month

---

## Troubleshooting

### Backend Issues

**Error: Module not found**
```bash
# Make sure you installed from project root
pip install -e .
```

**CORS errors**
- Check CORS_ORIGINS in backend .env matches frontend URL

### Frontend Issues

**API calls failing**
- Verify NEXT_PUBLIC_API_URL is correct
- Check browser console for errors
- Verify backend is running and accessible

**Build errors**
- Run `npm run build` locally first
- Check all imports are correct
- Verify all dependencies are in package.json

---

## Next Steps

1. ✅ Deploy backend to Railway/Render
2. ✅ Test backend API endpoints
3. ✅ Create and configure Next.js frontend
4. ✅ Test frontend locally
5. ✅ Deploy frontend to Vercel
6. ✅ Update CORS settings
7. ✅ Test production deployment

You're all set! 🎉

---

## Support Files

- Backend code: `backend/`
- Frontend templates: `docs/frontend-templates/`
- Backend setup: `backend/README.md`
- Frontend setup: `FRONTEND_SETUP.md`
- Deployment plan: `VERCEL_DEPLOYMENT_PLAN.md`

