"""
Chord Player Component for MUSEic Streamlit App
Uses Tone.js to play chord progressions in the browser with multiple instruments
"""

import streamlit as st
import streamlit.components.v1 as components

def play_chord_progression(
    progression_roman: str, 
    chords_example: str, 
    tempo: int = 120,
    instrument: str = "piano",
    loop: bool = True,
    widget_key: str = "default"
):
    """
    Create an interactive chord player in Streamlit with enhanced controls
    
    Args:
        progression_roman: Roman numeral notation (e.g., "I - V - vi - IV")
        chords_example: Chord names (e.g., "C - G - Am - F")
        tempo: BPM (default: 120)
        instrument: Sound type - "piano", "guitar", "synth", "pad" (default: "piano")
        loop: Whether to loop continuously (default: True)
        widget_key: Unique key for widget (default: "default")
    
    Returns:
        HTML component with playable chord progression
    """
    
    # Parse chords
    chord_names = [c.strip() for c in chords_example.split('-')]
    
    # Convert chord names to note arrays
    chord_notes = []
    for chord_name in chord_names:
        notes = chord_to_notes(chord_name)
        chord_notes.append(notes)
    
    # Instrument configurations - softer, less jarring
    instruments = {
        "piano": {
            "oscillator": "sine",
            "attack": 0.08,      # Slower attack for softer start
            "decay": 0.3,        # Longer decay
            "sustain": 0.15,     # Lower sustain (quieter)
            "release": 2.5,      # Longer release (smoother fade)
            "volume": -12        # Reduce overall volume
        },
        "guitar": {
            "oscillator": "triangle",
            "attack": 0.05,
            "decay": 0.4,
            "sustain": 0.12,
            "release": 2.0,
            "volume": -14
        },
        "synth": {
            "oscillator": "triangle",  # Changed from sawtooth (less harsh)
            "attack": 0.12,
            "decay": 0.3,
            "sustain": 0.2,
            "release": 1.8,
            "volume": -16        # Synth can be harsh, reduce more
        },
        "pad": {
            "oscillator": "sine",
            "attack": 0.5,       # Very slow attack for pad
            "decay": 0.5,
            "sustain": 0.4,
            "release": 3.0,      # Long release for pad
            "volume": -10
        }
    }
    
    instrument_config = instruments.get(instrument, instruments["piano"])
    
    # Create HTML with Tone.js
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
        <style>
            body {{
                font-family: 'Source Sans Pro', sans-serif;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                margin: 0;
            }}
            .player {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .progression {{
                text-align: center;
                font-size: 20px;
                font-weight: 600;
                color: #333;
                margin-bottom: 15px;
            }}
            .chords {{
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }}
            .chord {{
                background: #f0f2f6;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                color: #555;
                transition: all 0.3s ease;
                cursor: pointer;
                user-select: none;
            }}
            .chord:hover {{
                background: #e1e4e8;
                transform: translateY(-2px);
            }}
            .chord.active {{
                background: #667eea;
                color: white;
                transform: scale(1.08);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }}
            .chord.selected {{
                border: 2px solid #667eea;
                background: #e8ebf7;
            }}
            .controls {{
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-bottom: 15px;
                flex-wrap: wrap;
            }}
            button {{
                padding: 10px 20px;
                font-size: 14px;
                border: none;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 600;
                letter-spacing: 0.3px;
            }}
            .play-btn {{
                background: #667eea;
                color: white;
            }}
            .play-btn:hover:not(:disabled) {{
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }}
            .loop-btn {{
                background: #3498db;
                color: white;
            }}
            .loop-btn.active {{
                background: #2ecc71;
            }}
            .loop-btn:hover:not(:disabled) {{
                background: #2980b9;
                transform: translateY(-2px);
            }}
            .stop-btn {{
                background: #e74c3c;
                color: white;
            }}
            .stop-btn:hover:not(:disabled) {{
                background: #c0392b;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
            }}
            button:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            .help-text {{
                text-align: center;
                font-size: 12px;
                color: #888;
                margin-top: 10px;
            }}
            .status {{
                text-align: center;
                font-size: 13px;
                color: #667eea;
                min-height: 18px;
                font-weight: 500;
            }}
        </style>
    </head>
    <body>
        <div class="player">
            <div class="progression">{progression_roman}</div>
            <div class="chords" id="chords">
                {' '.join(f'<div class="chord" id="chord-{i}" onclick="toggleChordSelection({i})">{chord}</div>' for i, chord in enumerate(chord_names))}
            </div>
            <div class="status" id="status"></div>
            <div class="controls">
                <button class="play-btn" onclick="playProgression()">▶ Play</button>
                <button class="play-btn" onclick="playSelected()">▶ Play Selected</button>
                <button class="loop-btn" id="loop-btn" onclick="toggleLoop()">🔁 Loop</button>
                <button class="stop-btn" onclick="stopProgression()">⏹ Stop</button>
            </div>
            <div class="help-text">Click chords to select • Your settings are saved automatically</div>
        </div>

        <script>
            // Unique storage key for this progression
            const storageKey = "chord_player_{widget_key}";
            const activePlayerKey = "chord_player_active";  // Global key to track active player
            const thisPlayerId = "{widget_key}";
            
            // Check if another player is active and stop it
            function stopOtherPlayers() {{
                try {{
                    const activePlayer = sessionStorage.getItem(activePlayerKey);
                    if (activePlayer && activePlayer !== thisPlayerId) {{
                        // Another player is active, broadcast stop signal
                        sessionStorage.setItem(`stop_signal_${{activePlayer}}`, Date.now().toString());
                    }}
                    // Mark this player as active
                    sessionStorage.setItem(activePlayerKey, thisPlayerId);
                }} catch (e) {{
                    console.log("Could not stop other players:", e);
                }}
            }}
            
            // Listen for stop signals from other players
            window.addEventListener('storage', (e) => {{
                if (e.key === `stop_signal_${{thisPlayerId}}` && isPlaying) {{
                    stopProgression();
                }}
            }});
            
            // Also check for stop signal on interval (for same-window communication)
            setInterval(() => {{
                try {{
                    const stopSignal = sessionStorage.getItem(`stop_signal_${{thisPlayerId}}`);
                    if (stopSignal && isPlaying) {{
                        const signalTime = parseInt(stopSignal);
                        const now = Date.now();
                        // If signal is recent (within 1 second), stop
                        if (now - signalTime < 1000) {{
                            stopProgression();
                            sessionStorage.removeItem(`stop_signal_${{thisPlayerId}}`);
                        }}
                    }}
                }} catch (e) {{
                    // Ignore errors
                }}
            }}, 100);  // Check every 100ms
            
            // Load persisted state from sessionStorage
            function loadState() {{
                try {{
                    const saved = sessionStorage.getItem(storageKey);
                    if (saved) {{
                        const state = JSON.parse(saved);
                        return {{
                            shouldLoop: state.shouldLoop || false,
                            selectedChords: new Set(state.selectedChords || [])
                        }};
                    }}
                }} catch (e) {{
                    console.log("Could not load state:", e);
                }}
                return {{
                    shouldLoop: {"true" if loop else "false"},
                    selectedChords: new Set()
                }};
            }}
            
            // Save state to sessionStorage
            function saveState() {{
                try {{
                    const state = {{
                        shouldLoop: shouldLoop,
                        selectedChords: Array.from(selectedChords)
                    }};
                    sessionStorage.setItem(storageKey, JSON.stringify(state));
                }} catch (e) {{
                    console.log("Could not save state:", e);
                }}
            }}
            
            // Initialize Tone.js synth with configurable instrument
            const synth = new Tone.PolySynth(Tone.Synth, {{
                volume: {instrument_config['volume']},  // Reduce volume
                oscillator: {{
                    type: "{instrument_config['oscillator']}"
                }},
                envelope: {{
                    attack: {instrument_config['attack']},
                    decay: {instrument_config['decay']},
                    sustain: {instrument_config['sustain']},
                    release: {instrument_config['release']}
                }}
            }});

            // Low-pass filter to reduce harsh high frequencies
            const filter = new Tone.Filter({{
                frequency: 2000,  // Cut frequencies above 2kHz
                type: "lowpass",
                rolloff: -12
            }});

            // Reverb for smoother, more spacious sound
            const reverb = new Tone.Reverb({{
                decay: 4,        // Increased from 2 for more smoothness
                preDelay: 0.02,
                wet: 0.4         // 40% reverb mix
            }});

            // Compressor to even out dynamics and prevent harsh peaks
            const compressor = new Tone.Compressor({{
                threshold: -24,
                ratio: 4,
                attack: 0.003,
                release: 0.1
            }});

            // Connect signal chain: synth → filter → reverb → compressor → output
            synth.chain(filter, reverb, compressor, Tone.Destination);

            // Chord data from Python
            const progression = {chord_notes};
            const tempo = {tempo};
            const beatDuration = 60 / tempo * 2; // 2 beats per chord

            // Load persisted state
            const savedState = loadState();
            let isPlaying = false;
            let shouldLoop = savedState.shouldLoop;
            let selectedChords = savedState.selectedChords;
            let currentChordIndex = 0;

            // Restore UI state
            if (shouldLoop) {{
                document.getElementById('loop-btn').classList.add('active');
            }}
            
            // Restore selected chords visually
            selectedChords.forEach(index => {{
                const chord = document.getElementById(`chord-${{index}}`);
                if (chord) chord.classList.add('selected');
            }});

            // Note: Audio will automatically stop when switching tabs (component unmounts)
            // No auto-stop on scroll - users can scroll to lyrics while music plays

            function toggleChordSelection(index) {{
                const chord = document.getElementById(`chord-${{index}}`);
                if (selectedChords.has(index)) {{
                    selectedChords.delete(index);
                    chord.classList.remove('selected');
                }} else {{
                    selectedChords.add(index);
                    chord.classList.add('selected');
                }}
                saveState();  // Persist selection
            }}

            function toggleLoop() {{
                shouldLoop = !shouldLoop;
                const btn = document.getElementById('loop-btn');
                if (shouldLoop) {{
                    btn.classList.add('active');
                    updateStatus('Loop enabled');
                }} else {{
                    btn.classList.remove('active');
                    updateStatus('Loop disabled');
                }}
                saveState();  // Persist loop state
            }}

            function updateStatus(message) {{
                const status = document.getElementById('status');
                status.textContent = message;
                setTimeout(() => status.textContent = '', 2000);
            }}

            function highlightChord(index) {{
                document.querySelectorAll('.chord').forEach((el, i) => {{
                    if (i === index) {{
                        el.classList.add('active');
                    }} else {{
                        el.classList.remove('active');
                    }}
                }});
            }}

            async function playChordSequence(chordIndices) {{
                do {{
                    for (let i of chordIndices) {{
                        if (!isPlaying) return;
                        
                        currentChordIndex = i;
                        highlightChord(i);
                        
                        // Play the chord
                        synth.triggerAttackRelease(progression[i], beatDuration);
                        
                        // Wait for the beat duration
                        await new Promise(resolve => setTimeout(resolve, beatDuration * 1000));
                    }}
                }} while (isPlaying && shouldLoop);
                
                // Clear highlights if not looping
                if (!shouldLoop || !isPlaying) {{
                    document.querySelectorAll('.chord').forEach(el => el.classList.remove('active'));
                    isPlaying = false;
                }}
            }}

            async function playProgression() {{
                if (isPlaying) return;
                
                stopOtherPlayers();  // Stop any other active players
                isPlaying = true;
                await Tone.start(); // Required for audio to play
                
                const indices = Array.from({{length: progression.length}}, (_, i) => i);
                await playChordSequence(indices);
            }}

            async function playSelected() {{
                if (isPlaying) return;
                
                if (selectedChords.size === 0) {{
                    updateStatus('Select chords first');
                    return;
                }}
                
                stopOtherPlayers();  // Stop any other active players
                isPlaying = true;
                await Tone.start();
                
                const indices = Array.from(selectedChords).sort((a, b) => a - b);
                await playChordSequence(indices);
            }}

            function stopProgression() {{
                isPlaying = false;
                synth.releaseAll();
                document.querySelectorAll('.chord').forEach(el => el.classList.remove('active'));
                updateStatus('Stopped');
                
                // Clear active player tracking if we're the active one
                try {{
                    const activePlayer = sessionStorage.getItem(activePlayerKey);
                    if (activePlayer === thisPlayerId) {{
                        sessionStorage.removeItem(activePlayerKey);
                    }}
                }} catch (e) {{
                    // Ignore errors
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    # Render in Streamlit
    components.html(html_code, height=280)


def chord_to_notes(chord_name: str) -> list:
    """
    Convert chord name to array of note names
    Handles major, minor, 7th chords, and slash chords
    
    Args:
        chord_name: Chord name (e.g., "C", "Am", "G7", "C/G")
    
    Returns:
        List of note names (e.g., ["C4", "E4", "G4"])
    """
    
    # Handle slash chords (e.g., C/G) - just use the main chord for now
    if '/' in chord_name:
        chord_name = chord_name.split('/')[0]
    
    # Comprehensive note mapping
    note_map = {
        # C major family
        'C': ['C4', 'E4', 'G4'],
        'Cm': ['C4', 'Eb4', 'G4'],
        'C7': ['C4', 'E4', 'G4', 'Bb4'],
        'Cmaj7': ['C4', 'E4', 'G4', 'B4'],
        'Cm7': ['C4', 'Eb4', 'G4', 'Bb4'],
        
        # C# / Db
        'C#': ['C#4', 'F4', 'G#4'],
        'C#m': ['C#4', 'E4', 'G#4'],
        'Db': ['Db4', 'F4', 'Ab4'],
        'Dbm': ['Db4', 'E4', 'Ab4'],
        
        # D major family
        'D': ['D4', 'F#4', 'A4'],
        'Dm': ['D4', 'F4', 'A4'],
        'D7': ['D4', 'F#4', 'A4', 'C5'],
        'Dmaj7': ['D4', 'F#4', 'A4', 'C#5'],
        'Dm7': ['D4', 'F4', 'A4', 'C5'],
        
        # D# / Eb
        'D#': ['D#4', 'G4', 'A#4'],
        'D#m': ['D#4', 'F#4', 'A#4'],
        'Eb': ['Eb4', 'G4', 'Bb4'],
        'Ebm': ['Eb4', 'Gb4', 'Bb4'],
        
        # E major family
        'E': ['E4', 'G#4', 'B4'],
        'Em': ['E4', 'G4', 'B4'],
        'E7': ['E4', 'G#4', 'B4', 'D5'],
        'Emaj7': ['E4', 'G#4', 'B4', 'D#5'],
        'Em7': ['E4', 'G4', 'B4', 'D5'],
        
        # F major family
        'F': ['F4', 'A4', 'C5'],
        'Fm': ['F4', 'Ab4', 'C5'],
        'F7': ['F4', 'A4', 'C5', 'Eb5'],
        'Fmaj7': ['F4', 'A4', 'C5', 'E5'],
        'Fm7': ['F4', 'Ab4', 'C5', 'Eb5'],
        
        # F# / Gb
        'F#': ['F#4', 'A#4', 'C#5'],
        'F#m': ['F#4', 'A4', 'C#5'],
        'Gb': ['Gb4', 'Bb4', 'Db5'],
        'Gbm': ['Gb4', 'A4', 'Db5'],
        
        # G major family
        'G': ['G4', 'B4', 'D5'],
        'Gm': ['G4', 'Bb4', 'D5'],
        'G7': ['G4', 'B4', 'D5', 'F5'],
        'Gmaj7': ['G4', 'B4', 'D5', 'F#5'],
        'Gm7': ['G4', 'Bb4', 'D5', 'F5'],
        
        # G# / Ab
        'G#': ['G#4', 'C5', 'D#5'],
        'G#m': ['G#4', 'B4', 'D#5'],
        'Ab': ['Ab4', 'C5', 'Eb5'],
        'Abm': ['Ab4', 'B4', 'Eb5'],
        
        # A major family
        'A': ['A4', 'C#5', 'E5'],
        'Am': ['A4', 'C5', 'E5'],
        'A7': ['A4', 'C#5', 'E5', 'G5'],
        'Amaj7': ['A4', 'C#5', 'E5', 'G#5'],
        'Am7': ['A4', 'C5', 'E5', 'G5'],
        
        # A# / Bb
        'A#': ['A#4', 'D5', 'F5'],
        'A#m': ['A#4', 'C#5', 'F5'],
        'Bb': ['Bb4', 'D5', 'F5'],
        'Bbm': ['Bb4', 'Db5', 'F5'],
        
        # B major family
        'B': ['B4', 'D#5', 'F#5'],
        'Bm': ['B4', 'D5', 'F#5'],
        'B7': ['B4', 'D#5', 'F#5', 'A5'],
        'Bmaj7': ['B4', 'D#5', 'F#5', 'A#5'],
        'Bm7': ['B4', 'D5', 'F#5', 'A5'],
        
        # Diminished
        'Bdim': ['B4', 'D5', 'F5'],
        'Cdim': ['C4', 'Eb4', 'Gb4'],
        'Ddim': ['D4', 'F4', 'Ab4'],
        'Edim': ['E4', 'G4', 'Bb4'],
        'Fdim': ['F4', 'Ab4', 'B4'],
        'Gdim': ['G4', 'Bb4', 'Db5'],
        'Adim': ['A4', 'C5', 'Eb5'],
    }
    
    # Try exact match first
    if chord_name in note_map:
        return note_map[chord_name]
    
    # Try removing extensions (sus2, sus4, add9, etc.)
    base_chord = chord_name
    for extension in ['sus2', 'sus4', 'add9', '9', '11', '13', 'maj', 'min']:
        base_chord = base_chord.replace(extension, '')
    
    if base_chord in note_map:
        return note_map[base_chord]
    
    # If still not found, try to construct from root note
    import re
    match = re.match(r'^([A-G][#b]?)(.*)$', chord_name)
    if match:
        root, quality = match.groups()
        # Check if it's minor
        if 'm' in quality.lower() and 'maj' not in quality.lower():
            # Try adding 'm'
            if root + 'm' in note_map:
                return note_map[root + 'm']
        # Try just the root (major)
        if root in note_map:
            return note_map[root]
    
    # Default to C major if unknown
    return note_map['C']


# ==================== USAGE IN STREAMLIT APP ====================

if __name__ == "__main__":
    st.set_page_config(page_title="Chord Player Demo", page_icon="🎵")
    
    st.title("🎵 MUSEic Chord Player")
    st.write("Play chord progressions directly in your browser!")
    
    # Example usage
    st.subheader("Example: I - V - vi - IV")
    play_chord_progression(
        progression_roman="I - V - vi - IV",
        chords_example="C - G - Am - F",
        tempo=100
    )
    
    st.markdown("---")
    
    st.subheader("Example: vi - IV - I - V")
    play_chord_progression(
        progression_roman="vi - IV - I - V",
        chords_example="Am - F - C - G",
        tempo=120
    )
    
    st.markdown("---")
    
    # Interactive example
    st.subheader("Try Your Own Progression")
    
    col1, col2 = st.columns(2)
    
    with col1:
        custom_roman = st.text_input("Roman Numerals", "I - IV - V - I")
    
    with col2:
        custom_chords = st.text_input("Chord Names", "C - F - G - C")
    
    tempo = st.slider("Tempo (BPM)", 60, 180, 120)
    
    if st.button("Play Custom Progression"):
        play_chord_progression(
            progression_roman=custom_roman,
            chords_example=custom_chords,
            tempo=tempo
        )