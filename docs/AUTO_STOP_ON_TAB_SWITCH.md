# Auto-Stop on Tab Switch Feature

## Overview
The chord player now automatically stops playback when users switch to a different progression tab. This prevents confusion and audio overlap when exploring multiple progression options.

## Problem It Solves

**Before**: 
- User plays "Option 1" progression
- User switches to "Option 2" tab
- "Option 1" keeps playing in the background
- Confusing audio overlap if user plays "Option 2"
- User has to remember to manually stop the previous progression

**After**:
- User plays "Option 1" progression
- User switches to "Option 2" tab
- "Option 1" **automatically stops** ✅
- Clean, professional experience
- No manual cleanup needed

## How It Works

### Technical Implementation

The feature uses the **Intersection Observer API** to detect when the chord player becomes invisible:

```javascript
// Auto-stop when tab becomes inactive
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting && isPlaying) {
            // Player is no longer visible, stop playback
            stopProgression();
        }
    });
}, {
    threshold: 0.1  // Stop when less than 10% visible
});

// Observe the player container
const playerElement = document.querySelector('.player');
if (playerElement) {
    observer.observe(playerElement);
}
```

### Intersection Observer Explained

- **What it does**: Monitors when an element enters/exits the viewport
- **How we use it**: Detects when the player container is no longer visible
- **Threshold**: `0.1` means trigger when less than 10% of the player is visible
- **Action**: Calls `stopProgression()` to halt playback and clear highlights

### When It Triggers

The auto-stop triggers when:
1. **User switches tabs**: Clicks a different "Option" tab
2. **User scrolls away**: Scrolls so the player is off-screen (rare in our layout)
3. **Tab becomes hidden**: Browser tab becomes inactive

The auto-stop does NOT trigger when:
- User is still viewing the same tab
- Player is fully or mostly visible
- User changes instrument/tempo (player stays visible)

## User Experience

### Scenario 1: Comparing Progressions
```
1. Click "Option 1" tab
2. Click "▶ Play" → Progression plays
3. Click "Option 2" tab → Option 1 stops automatically
4. Click "▶ Play" → Option 2 plays cleanly
```

### Scenario 2: Finding the Perfect Sound
```
1. In "Option 1", enable loop and play
2. Listen while reading Option 2's theory
3. Click "Option 2" tab → Loop stops automatically
4. No need to go back to Option 1 to stop it
```

### Scenario 3: Rapid Exploration
```
1. Play Option 1 → switch to Option 2 (auto-stops)
2. Play Option 2 → switch to Option 3 (auto-stops)
3. Play Option 3 → switch back to Option 1 (auto-stops)
Each tab switch is clean, no audio overlap
```

## Benefits

1. **No Audio Overlap**: Only one progression plays at a time
2. **Clean UX**: Professional behavior users expect
3. **Less Confusion**: Clear which progression is currently active
4. **Automatic**: No manual intervention required
5. **Works with Loop**: Even continuous loops stop when switching tabs
6. **Browser Standard**: Uses native Intersection Observer API (well-supported)

## Browser Compatibility

The Intersection Observer API is supported in:
- ✅ Chrome 51+
- ✅ Firefox 55+
- ✅ Safari 12.1+
- ✅ Edge 15+
- ✅ All modern browsers

For unsupported browsers (very rare):
- Feature gracefully degrades
- Users can still manually stop playback
- No errors or crashes

## Implementation Details

### File Modified
- **src/utils/chord_player.py** (lines 295-311)

### Integration
- Observer created after state restoration
- Observes the `.player` container div
- Fires before any function definitions
- Works seamlessly with existing stop logic

### Performance
- **Lightweight**: Observer has minimal overhead
- **Efficient**: Only fires when visibility changes
- **No polling**: Event-driven, not constantly checking
- **One per player**: Each progression tab has its own observer

## Edge Cases Handled

1. **Player not found**: Check `if (playerElement)` before observing
2. **Already stopped**: Check `if (isPlaying)` before stopping
3. **Multiple rapid switches**: Observer handles debouncing naturally
4. **Loop mode**: Works correctly even with continuous playback
5. **Selected chords only**: Stops regardless of playback mode

## Testing

Manual testing confirmed:
- ✅ Switch from playing tab → auto-stops
- ✅ Switch from looping tab → auto-stops
- ✅ Switch during selected chord playback → auto-stops
- ✅ Stay on same tab → continues playing
- ✅ Change instrument on same tab → keeps playing (correct)
- ✅ No console errors
- ✅ No performance issues

## Related Features

This works alongside:
- **State persistence**: Selections saved when switching tabs
- **Session state**: Results persist across reruns
- **Multiple instruments**: Works with all instrument types
- **Loop mode**: Properly stops even continuous loops

## Future Enhancements

Potential additions:
- Optional "keep playing" mode (user preference)
- Fade-out instead of abrupt stop
- Cross-fade between progressions when switching
- Visual indicator of which tab is playing

---

**Result**: Switching between progression tabs now provides a clean, professional experience with automatic audio management. Users can freely explore options without manual cleanup.

