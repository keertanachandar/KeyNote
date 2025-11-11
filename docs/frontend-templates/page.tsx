// app/page.tsx
'use client';

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SongInputForm from '@/components/forms/SongInputForm';
import ProgressionResults from '@/components/progressions/ProgressionResults';
import type { GenerateResponse } from '@/types/progression';

const queryClient = new QueryClient();

export default function Home() {
  return (
    <QueryClientProvider client={queryClient}>
      <HomeContent />
    </QueryClientProvider>
  );
}

function HomeContent() {
  const [results, setResults] = useState<GenerateResponse | null>(null);

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-slate-900">
            🎸 KeyNote
          </h1>
          <p className="text-slate-600 mt-2">
            AI-Powered Chord Progression Assistant for Songwriters
          </p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Input Form */}
        <SongInputForm onResults={setResults} />

        {/* Results */}
        {results && <ProgressionResults results={results} />}

        {/* Footer */}
        <footer className="mt-16 text-center text-slate-600 text-sm">
          <p>Transform your lyrics and musical ideas into personalized chord progressions</p>
        </footer>
      </div>
    </main>
  );
}

