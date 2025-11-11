# Frontend Setup Instructions

## Create Next.js App

```bash
# In the KeyNote directory
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
cd frontend
```

When prompted:
- ✅ TypeScript: Yes
- ✅ ESLint: Yes
- ✅ Tailwind CSS: Yes
- ✅ `app/` directory: Yes
- ❌ `src/` directory: No
- ✅ App Router: Yes
- ❌ Import alias: No (or use @/*)

## Install Dependencies

```bash
cd frontend
npm install @tanstack/react-query axios tone lucide-react
npm install -D @types/node
```

### Install shadcn/ui

```bash
npx shadcn-ui@latest init
```

When prompted:
- Style: Default
- Base color: Slate
- CSS variables: Yes

Install components:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add select
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add card
npx shadcn-ui@latest add slider
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add collapsible
```

## Environment Variables

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx           # Main page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
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
│   └── utils.ts          # Utilities
├── hooks/
│   ├── useGenerateProgressions.ts
│   └── useChordPlayer.ts
├── types/
│   ├── progression.ts
│   └── analysis.ts
├── public/
└── package.json
```

## Run Development Server

```bash
npm run dev
```

App will be at: `http://localhost:3000`

## Deploy to Vercel

### Via CLI

```bash
npm i -g vercel
vercel
```

### Via Dashboard

1. Go to https://vercel.com
2. Import Git Repository
3. Framework Preset: Next.js
4. Root Directory: `frontend`
5. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-backend-url.com`
6. Deploy

## Next Steps

1. Copy the component files I create below into the appropriate directories
2. Run the development server
3. Test locally with the backend running
4. Deploy to Vercel

