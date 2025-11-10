"""
Intelligent Chord Transposition System for KeyNote
Uses music theory knowledge and LLM assistance for accurate transposition

Features:
- Transpose chord progressions to any key
- Handle both Roman numeral and absolute notation
- Preserve chord quality (major, minor, diminished, augmented)
- Use music theory embeddings for complex cases
- Support slash chords and extensions
"""

import re
from typing import Dict, List, Tuple, Optional
from langchain_openai import ChatOpenAI
import os


class ChordTransposer:
    """
    Intelligent chord transposition system that uses music theory
    and LLM assistance for accurate key changes
    """
    
    # Chromatic scale (all 12 notes)
    CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Enharmonic equivalents (for display)
    ENHARMONICS = {
        'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb'
    }
    
    # Major scale intervals (whole/half steps from root)
    MAJOR_SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]  # C D E F G A B
    
    # Minor scale intervals (natural minor)
    MINOR_SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]  # A B C D E F G
    
    # Roman numeral to scale degree mapping
    ROMAN_TO_DEGREE = {
        'I': 0, 'i': 0,
        'II': 1, 'ii': 1,
        'III': 2, 'iii': 2,
        'IV': 3, 'iv': 3,
        'V': 4, 'v': 4,
        'VI': 5, 'vi': 5,
        'VII': 6, 'vii': 6,
        'bII': 1, 'bii': 1,
        'bIII': 2, 'biii': 2,
        'bIV': 3, 'biv': 3,
        'bV': 4, 'bv': 4,
        'bVI': 5, 'bvi': 5,
        'bVII': 6, 'bvii': 6,
    }
    
    # Common chord qualities and their symbols
    CHORD_QUALITIES = {
        '': 'major',
        'm': 'minor',
        'maj': 'major',
        'min': 'minor',
        'dim': 'diminished',
        '°': 'diminished',
        'aug': 'augmented',
        '+': 'augmented',
        '7': 'dominant7',
        'maj7': 'major7',
        'm7': 'minor7',
        'min7': 'minor7',
        'dim7': 'diminished7',
        '°7': 'diminished7',
        'sus2': 'suspended2',
        'sus4': 'suspended4',
        '6': 'major6',
        'm6': 'minor6',
        '9': 'dominant9',
        'maj9': 'major9',
        'm9': 'minor9',
        '11': 'dominant11',
        '13': 'dominant13',
    }
    
    def __init__(self, rag_system=None):
        """
        Initialize the transposer
        
        Args:
            rag_system: Optional RAG system for querying music theory
        """
        self.rag_system = rag_system
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_note_index(self, note: str) -> int:
        """Get the chromatic index of a note"""
        # Remove quality markers, get just the root note
        root = re.match(r'^([A-G][#b]?)', note)
        if root:
            root_note = root.group(1)
            # Normalize flats to sharps
            if 'b' in root_note:
                root_base = root_note[0]
                idx = self.CHROMATIC_SCALE.index(root_base)
                return (idx - 1) % 12
            return self.CHROMATIC_SCALE.index(root_note)
        return 0
    
    def transpose_note(self, note: str, semitones: int, prefer_flats: bool = False) -> str:
        """
        Transpose a single note by semitones
        
        Args:
            note: Note to transpose (e.g., "C", "F#", "Bb")
            semitones: Number of semitones to transpose (positive = up, negative = down)
            prefer_flats: Whether to use flat notation instead of sharps
            
        Returns:
            Transposed note
        """
        # Parse the note
        match = re.match(r'^([A-G][#b]?)(.*)', note)
        if not match:
            return note
        
        root_note, suffix = match.groups()
        
        # Get current index
        current_idx = self.get_note_index(root_note)
        
        # Calculate new index
        new_idx = (current_idx + semitones) % 12
        
        # Get new note
        new_note = self.CHROMATIC_SCALE[new_idx]
        
        # Apply flat preference if needed
        if prefer_flats and '#' in new_note and new_note in self.ENHARMONICS:
            new_note = self.ENHARMONICS[new_note]
        
        return new_note + suffix
    
    def normalize_chord_case(self, chord: str) -> str:
        """
        Normalize chord case to proper notation
        Examples: am -> Am, dm7 -> Dm7, f#m -> F#m
        
        Args:
            chord: Chord with any case
            
        Returns:
            Chord with proper case (capital root, lowercase quality markers)
        """
        if not chord or len(chord) < 1:
            return chord
        
        # Handle slash chords separately
        if '/' in chord:
            parts = chord.split('/')
            return self.normalize_chord_case(parts[0]) + '/' + self.normalize_chord_case(parts[1])
        
        # Match root note (with optional accidental)
        match = re.match(r'^([A-Ga-g][#b]?)(.*)', chord, re.IGNORECASE)
        if match:
            root, quality = match.groups()
            # Capitalize root note
            root = root[0].upper() + root[1:] if len(root) > 1 else root.upper()
            # Keep quality markers lowercase (m, maj, min, dim, etc.)
            return root + quality.lower() if quality else root
        
        return chord
    
    def parse_chord(self, chord: str) -> Tuple[str, str, Optional[str]]:
        """
        Parse a chord into root, quality, and bass (for slash chords)
        Case-insensitive: am, Am, AM all treated as Am
        
        Args:
            chord: Chord string (e.g., "Cmaj7", "Am/G", "D7", "am", "f#m")
            
        Returns:
            Tuple of (root, quality, bass)
        """
        # Normalize case first
        chord = self.normalize_chord_case(chord)
        
        # Handle slash chords (e.g., C/G)
        if '/' in chord:
            chord_part, bass = chord.split('/')
            root_match = re.match(r'^([A-G][#b]?)(.*)', chord_part)
            if root_match:
                root, quality = root_match.groups()
                return root, quality, bass
        
        # Regular chords
        root_match = re.match(r'^([A-G][#b]?)(.*)', chord)
        if root_match:
            root, quality = root_match.groups()
            return root, quality, None
        
        return chord, '', None
    
    def transpose_chord(self, chord: str, semitones: int, prefer_flats: bool = False) -> str:
        """
        Transpose a single chord
        
        Args:
            chord: Chord to transpose (e.g., "Cmaj7", "Am/G")
            semitones: Semitones to transpose
            prefer_flats: Use flat notation
            
        Returns:
            Transposed chord
        """
        root, quality, bass = self.parse_chord(chord)
        
        # Transpose root
        new_root = self.transpose_note(root, semitones, prefer_flats)
        
        # Transpose bass if present
        new_bass = None
        if bass:
            new_bass = self.transpose_note(bass, semitones, prefer_flats)
        
        # Reconstruct chord
        result = new_root + quality
        if new_bass:
            result += '/' + new_bass
        
        return result
    
    def transpose_progression(self, progression: str, from_key: str, to_key: str) -> str:
        """
        Transpose a chord progression from one key to another
        Case-insensitive: "C - g - am - F" normalized to "C - G - Am - F"
        
        Args:
            progression: Chord progression (e.g., "C - G - Am - F", "c - g - am - f")
            from_key: Original key
            to_key: Target key
            
        Returns:
            Transposed progression with proper case
        """
        # Calculate semitone difference
        from_idx = self.get_note_index(from_key)
        to_idx = self.get_note_index(to_key)
        semitones = (to_idx - from_idx) % 12
        
        # Determine if we should prefer flats (for flat keys)
        prefer_flats = 'b' in to_key or to_key in ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
        
        # Split progression, normalize case, and transpose each chord
        chords = [c.strip() for c in progression.split('-')]
        # Normalize case before transposing
        normalized = [self.normalize_chord_case(chord) for chord in chords]
        transposed = [self.transpose_chord(chord, semitones, prefer_flats) for chord in normalized]
        
        return ' - '.join(transposed)
    
    def get_key_preference_from_vocals(self, vocal_range: str) -> List[str]:
        """
        Suggest comfortable keys based on vocal range
        
        Args:
            vocal_range: Description like "low male", "high female", "tenor", etc.
            
        Returns:
            List of recommended keys
        """
        vocal_range_lower = vocal_range.lower()
        
        # Common vocal range recommendations
        if any(term in vocal_range_lower for term in ['low', 'bass', 'contralto']):
            return ['C', 'D', 'Eb', 'E', 'F']
        elif any(term in vocal_range_lower for term in ['high', 'soprano', 'tenor']):
            return ['G', 'A', 'Bb', 'B', 'C']
        elif 'alto' in vocal_range_lower or 'mezzo' in vocal_range_lower:
            return ['F', 'G', 'Ab', 'A', 'Bb']
        elif 'baritone' in vocal_range_lower:
            return ['D', 'E', 'F', 'G', 'Ab']
        else:
            # Default middle range
            return ['C', 'D', 'E', 'F', 'G', 'A']
    
    def transpose_progression_smart(self, 
                                   progression_data: Dict,
                                   target_key: str,
                                   use_theory: bool = True) -> Dict:
        """
        Intelligently transpose a progression with music theory context
        
        Args:
            progression_data: Dict with progression info (progression_roman, chords_example, etc.)
            target_key: Target key to transpose to
            use_theory: Whether to use RAG system for music theory context
            
        Returns:
            Updated progression_data with transposed chords
        """
        original_progression = progression_data.get('chords_example', '')
        
        # Determine original key (assume C major by default)
        original_key = self._infer_key_from_example(original_progression)
        
        # Get music theory context if available
        theory_context = ""
        if use_theory and self.rag_system:
            theory_query = f"transposing {original_progression} from {original_key} to {target_key}"
            theory_docs = self.rag_system.get_theory_context(theory_query, k=2)
            if theory_docs:
                theory_context = "\n".join([doc.page_content[:300] for doc in theory_docs])
        
        # Transpose the progression
        transposed = self.transpose_progression(
            original_progression,
            original_key,
            target_key
        )
        
        # Create updated data
        result = progression_data.copy()
        result['chords_example'] = transposed
        result['transposed_from'] = original_key
        result['transposed_to'] = target_key
        result['original_chords'] = original_progression
        
        # Add explanation using LLM if theory context available
        if theory_context:
            explanation = self._generate_transposition_explanation(
                original_progression,
                transposed,
                original_key,
                target_key,
                theory_context
            )
            result['transposition_note'] = explanation
        
        return result
    
    def _infer_key_from_example(self, chord_example: str) -> str:
        """
        Infer the key from chord example
        Default to C for examples, but try to detect from first chord
        """
        chords = chord_example.split('-')
        if chords:
            first_chord = chords[0].strip()
            # Extract root note
            match = re.match(r'^([A-G][#b]?)', first_chord)
            if match:
                root = match.group(1)
                # If it's likely a tonic (major chord), use as key
                if not any(qual in first_chord.lower() for qual in ['m', 'min', 'dim']):
                    return root
        return 'C'  # Default
    
    def _generate_transposition_explanation(self,
                                          original: str,
                                          transposed: str,
                                          from_key: str,
                                          to_key: str,
                                          theory_context: str) -> str:
        """Generate a helpful explanation of the transposition"""
        prompt = f"""Briefly explain this chord transposition (1 sentence):

Original ({from_key}): {original}
Transposed ({to_key}): {transposed}

Music Theory Context:
{theory_context[:200]}

Keep it practical and helpful for songwriters."""

        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except:
            return f"Transposed from {from_key} to {to_key} by moving all chords proportionally."
    
    def get_all_keys(self) -> List[str]:
        """Get list of all available keys"""
        # Major keys (both sharp and flat versions for common keys)
        return [
            'C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 
            'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B'
        ]
    
    def normalize_key(self, key: str) -> str:
        """Normalize key name (e.g., 'Db' -> 'C#', but keep 'C#/Db' as is)"""
        if '/' in key:
            return key.split('/')[0]  # Use sharp version
        # Convert flats to sharps for internal use
        if 'b' in key:
            note = key[0]
            idx = self.CHROMATIC_SCALE.index(note)
            return self.CHROMATIC_SCALE[(idx - 1) % 12]
        return key


def transpose_all_progressions(progressions: List[Dict], 
                               target_key: str,
                               transposer: ChordTransposer) -> List[Dict]:
    """
    Transpose all progressions in a list to the target key
    
    Args:
        progressions: List of progression dictionaries
        target_key: Target key
        transposer: ChordTransposer instance
        
    Returns:
        List of transposed progressions
    """
    return [
        transposer.transpose_progression_smart(prog, target_key, use_theory=False)
        for prog in progressions
    ]

