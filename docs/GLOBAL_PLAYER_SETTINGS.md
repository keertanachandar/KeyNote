# Global Player Settings Feature

## Overview
Tempo and instrument settings are now global and persist across all progression options. Users set them once and they apply to every progression tab, only changing when explicitly adjusted.

## Problem It Solved

**Before**: Each progression tab had its own instrument and tempo selectors
- Option 1: Piano at 120 BPM
- Switch to Option 2: Reset to Piano at 120 BPM again (separate controls)
- Change to Guitar at 140 BPM in Option 2
- Switch back to Option 1: Still Piano at 120 BPM (settings didn't transfer)

**After**: One set of controls for all progressions
- Set Guitar at 140 BPM once
- All progression options use Guitar at 140 BPM
- Switch between Option 1, 2, 3... all use the same settings
- Only changes when you explicitly adjust the controls

## User Experience

### Setting Your Preferences Once

1. User generates chord progressions
2. User sees global "Player Settings" section
3. User selects "Guitar" and sets tempo to 140 BPM
4. **All progression tabs now use Guitar at 140 BPM**

### Exploring Options with Consistent Settings

```
User sets: Guitar + 140 BPM

Option 1 → Plays with Guitar at 140 BPM
Option 2 → Plays with Guitar at 140 BPM
Option 3 → Plays with Guitar at 140 BPM
...all options use the same settings
```

### Changing Settings

```
Change instrument to "Synth"
→ All options immediately use Synth

Adjust tempo to 100 BPM
→ All options immediately use 100 BPM
```

## Technical Implementation

### Location
Global controls appear **between the tabs and the tab content**:

```
Tabs: [Option 1] [Option 2] [Option 3]
      ↓
🎹 Player Settings (applies to all progressions)
[Instrument: Piano ▼] [Tempo: 120 ━━●━━ ]
      ↓
Tab Content (Option 1 selected)
[Progression details and player]
```

### Session State Storage

```python
# Initialize defaults on first load
if 'global_instrument' not in st.session_state:
    st.session_state['global_instrument'] = 'piano'

if 'global_tempo' not in st.session_state:
    st.session_state['global_tempo'] = 120

# Store user selections
st.session_state['global_instrument'] = selected_instrument
st.session_state['global_tempo'] = selected_tempo
```

### Widget Keys
- **Instrument selector**: `global_instrument_selector` (unique, not tab-specific)
- **Tempo slider**: `global_tempo_slider` (unique, not tab-specific)

### Passing to Player

```python
play_chord_progression(
    progression_roman=prog.metadata['progression_roman'],
    chords_example=prog.metadata['chords_example'],
    tempo=global_tempo,        # Global value
    instrument=global_instrument,  # Global value
    widget_key=prog_key        # Still unique per progression
)
```

## Benefits

### 1. Consistent Experience
Users don't have to reset instrument/tempo for each progression they want to try.

### 2. Faster Comparison
Quickly switch between Option 1, 2, 3 with the same sound settings to compare progressions fairly.

### 3. Less Confusion
Clear that settings apply globally - no wondering why settings "reset" when switching tabs.

### 4. Fewer Clicks
Set once, apply everywhere. No repetitive adjustments.

### 5. Better Workflow
```
Workflow Before:
1. Try Option 1 → Set guitar/tempo
2. Try Option 2 → Set guitar/tempo again
3. Try Option 3 → Set guitar/tempo again
❌ Repetitive, frustrating

Workflow After:
1. Set guitar/tempo once
2. Try Option 1, 2, 3... all use same settings
✅ Efficient, smooth
```

## UI Design

### Header Section
```
🎹 Player Settings (applies to all progressions)
🎵 These settings apply to all progression options
[Instrument ▼]  [Tempo Slider]
```

### Visual Hierarchy
1. Tabs at top (progression selection)
2. Global settings (instrument/tempo)
3. Tab content (selected progression details)
4. Player (uses global settings)

### Placement Rationale
- **After tabs**: So users know what progressions are available
- **Before content**: So settings are visible before playing
- **Separate section**: Clear visual distinction from per-progression controls

## What Stays Tab-Specific

### Per-Progression Settings (Still Unique)
- ✅ **Chord selections**: Each tab remembers which chords you selected
- ✅ **Loop toggle**: Each tab remembers if loop was on/off
- ✅ **Play state**: Playing in one tab doesn't affect others
- ✅ **Theory explanations**: Each progression has unique theory

### Global Settings (Shared)
- 🌐 **Instrument**: All tabs use same instrument
- 🌐 **Tempo**: All tabs use same tempo

## Edge Cases Handled

### 1. First Load
- Defaults to Piano at 120 BPM
- Session state initialized

### 2. Switching Between Generated Results
- Settings persist across different song generations
- Clear only on browser refresh or explicit reset

### 3. Changing Settings Mid-Play
- If progression is playing, settings update doesn't stop playback
- New settings apply next time user clicks play

## Files Modified

- **src/app.py** (lines 351-385, 469-481)
  - Added global player controls section
  - Removed per-tab instrument/tempo selectors
  - Updated play_chord_progression calls to use global values

## User Feedback Anticipated

### Positive
- ✅ "Much easier to compare progressions!"
- ✅ "Love that I don't have to reset settings for each option"
- ✅ "More professional and streamlined"

### Potential Questions
- ❓ "Can I have different tempos for different progressions?"
  - **Answer**: No, tempo is global for fair comparison. Use loop + chord selection for focused listening.

## Future Enhancements

Possible additions:
- "Reset to defaults" button (Piano, 120 BPM)
- Save/load preset combinations (e.g., "Fast Rock", "Slow Ballad")
- Per-progression tempo override toggle (advanced feature)

---

**Result**: Users can now set their preferred instrument and tempo once, then freely explore all progression options with consistent playback settings. Much more efficient and professional workflow!

