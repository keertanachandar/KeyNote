// types/progression.ts
export interface Progression {
  progression_roman: string;
  chords_example: string;
  original_key?: string;
  genres?: string;
  frequency?: string;
  example_songs?: string;
  match_score?: number;
}

export interface ScoredProgression {
  progression: Progression;
  match_score: number;
}

// types/analysis.ts
export interface LyricsAnalysis {
  overall_mood?: string;
  overall_genre?: string;
  overall_energy?: string;
  overall_themes?: string[];
  emotional_arc?: string;
  song_structure?: SongSection[];
  emotional_peaks?: EmotionalPeak[];
  section_specific_recommendations?: Record<string, string>;
  is_partial: boolean;
  snippet_type: string;
}

export interface SongSection {
  section: string;
  section_mood?: string;
  emotional_intensity?: number;
  harmonic_needs?: string;
}

export interface EmotionalPeak {
  section: string;
  intensity: number;
  line_text: string;
  harmonic_suggestion?: string;
}

// types/request.ts
export interface GenerateRequest {
  description?: string;
  lyrics?: string;
  reference_artists?: string;
  preferred_key: string;
  vocal_range?: string;
}

export interface GenerateResponse {
  progressions: ScoredProgression[];
  lyrics_analysis?: LyricsAnalysis;
  theory_context?: string[];
  current_examples?: WebExample[];
  synthesis?: string;
}

export interface WebExample {
  title: string;
  url: string;
  content: string;
}

export interface TransposeRequest {
  progression_data: Progression;
  target_key: string;
  use_theory?: boolean;
}

export interface TransposeResponse {
  progression_roman: string;
  chords_example: string;
  original_chords: string;
  original_key: string;
  target_key: string;
}

