// hooks/useGenerateProgressions.ts
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { GenerateRequest, GenerateResponse } from '@/types/progression';

export function useGenerateProgressions() {
  return useMutation<GenerateResponse, Error, GenerateRequest>({
    mutationFn: (request) => apiClient.generateProgressions(request),
  });
}

// hooks/useTranspose.ts
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { TransposeRequest, TransposeResponse } from '@/types/progression';

export function useTranspose() {
  return useMutation<TransposeResponse, Error, TransposeRequest>({
    mutationFn: (request) => apiClient.transposeProgression(request),
  });
}

// hooks/useChordPlayer.ts
import { useState, useCallback, useRef, useEffect } from 'react';
import * as Tone from 'tone';

interface UseChordPlayerProps {
  chords: string;
  tempo: number;
  instrument: 'piano' | 'guitar' | 'synth' | 'pad';
  loop: boolean;
}

export function useChordPlayer({ chords, tempo, instrument, loop }: UseChordPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedChords, setSelectedChords] = useState<number[]>([]);
  const synthRef = useRef<Tone.PolySynth | null>(null);

  useEffect(() => {
    // Initialize Tone.js synth
    const initSynth = () => {
      if (synthRef.current) {
        synthRef.current.dispose();
      }

      const instrumentConfigs = {
        piano: { oscillator: 'sine', attack: 0.08, decay: 0.3, sustain: 0.15, release: 2.5, volume: -12 },
        guitar: { oscillator: 'triangle', attack: 0.05, decay: 0.4, sustain: 0.12, release: 2.0, volume: -14 },
        synth: { oscillator: 'triangle', attack: 0.12, decay: 0.3, sustain: 0.2, release: 1.8, volume: -16 },
        pad: { oscillator: 'sine', attack: 0.5, decay: 0.5, sustain: 0.4, release: 3.0, volume: -10 },
      };

      const config = instrumentConfigs[instrument];

      synthRef.current = new Tone.PolySynth(Tone.Synth, {
        volume: config.volume,
        oscillator: { type: config.oscillator },
        envelope: {
          attack: config.attack,
          decay: config.decay,
          sustain: config.sustain,
          release: config.release,
        },
      });

      const filter = new Tone.Filter({ frequency: 2000, type: 'lowpass', rolloff: -12 });
      const reverb = new Tone.Reverb({ decay: 4, preDelay: 0.02, wet: 0.4 });
      const compressor = new Tone.Compressor({ threshold: -24, ratio: 4, attack: 0.003, release: 0.1 });

      synthRef.current.chain(filter, reverb, compressor, Tone.Destination);
    };

    initSynth();

    return () => {
      if (synthRef.current) {
        synthRef.current.dispose();
      }
    };
  }, [instrument]);

  const toggleChordSelection = useCallback((index: number) => {
    setSelectedChords((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );
  }, []);

  const play = useCallback(async (chordIndices?: number[]) => {
    if (!synthRef.current || isPlaying) return;

    await Tone.start();
    setIsPlaying(true);

    const chordList = chords.split('-').map((c) => c.trim());
    const indices = chordIndices || Array.from({ length: chordList.length }, (_, i) => i);
    const beatDuration = (60 / tempo) * 2;

    // Simplified chord-to-notes mapping
    const chordToNotes = (chord: string): string[] => {
      // This is a simplified version - you'd need full chord parsing
      const root = chord[0].toUpperCase();
      return [`${root}3`, `${root}4`, `${root}5`];
    };

    const playSequence = async () => {
      do {
        for (const i of indices) {
          if (!isPlaying) return;

          const notes = chordToNotes(chordList[i]);
          synthRef.current?.triggerAttackRelease(notes, beatDuration);

          await new Promise((resolve) => setTimeout(resolve, beatDuration * 1000));
        }
      } while (isPlaying && loop);

      setIsPlaying(false);
    };

    playSequence();
  }, [chords, tempo, isPlaying, loop]);

  const stop = useCallback(() => {
    setIsPlaying(false);
    synthRef.current?.releaseAll();
  }, []);

  return {
    isPlaying,
    selectedChords,
    toggleChordSelection,
    play,
    stop,
  };
}

