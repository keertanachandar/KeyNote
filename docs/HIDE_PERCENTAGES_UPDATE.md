# Hide Percentages Below 75% - Update

## Summary
Updated the entire app to hide match percentages when they are below 75%, providing a cleaner UI and only showing high-confidence matches.

## Changes Made

### 1. Tab Labels (Already Implemented) ✅
**Location**: `src/app.py` lines 331-339

```python
# Only show percentage in tab labels if >= 75%
if score >= 75:
    tab_labels.append(f"Option {i+1} ({score}% match)")
else:
    tab_labels.append(f"Option {i+1}")
```

**Result:**
- **High scores (≥75%)**: "Option 1 (92% match)"
- **Lower scores (<75%)**: "Option 1"

---

### 2. Individual Progression Display (Already Implemented) ✅
**Location**: `src/app.py` lines 360-371

```python
# Show percentage prominently if >= 75%
if score >= 75:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {match_emoji} {prog.metadata['progression_roman']}")
    with col2:
        st.markdown(f"**{score}%**")
        st.caption(match_label)
else:
    # Don't show percentage for scores under 75%
    st.markdown(f"### {match_emoji} {prog.metadata['progression_roman']}")
    st.caption(match_label)
```

**Result:**
- **High scores (≥75%)**: Shows percentage prominently (e.g., "92%")
- **Lower scores (<75%)**: Shows only emoji and label (e.g., "👍 Good Option")

---

### 3. Comparative Analysis Context (NEW UPDATE) ✅
**Location**: `src/app.py` lines 495-506

```python
# Only include percentage in context if >= 75%
for idx, scored_prog in enumerate(top_progressions, 1):
    prog = scored_prog['progression']
    score = scored_prog['match_score']
    if score >= 75:
        comp_context += f"**Option {idx}** ({score}% match):\n"
    else:
        comp_context += f"**Option {idx}**:\n"
    # ... rest of context
```

**Result:**
- LLM receives percentage only for high-confidence matches
- Context remains clean and focused

---

### 4. Comparative Analysis Prompt (NEW UPDATE) ✅
**Location**: `src/app.py` lines 516-531

**Before:**
```
1. Quick Recommendation: ... (Reference by Option number and match %)
...
- Be specific about the match percentages
```

**After:**
```
1. Quick Recommendation: ... (Reference by Option number)
...
- If match percentages are shown, you can reference them, but don't invent percentages
```

**Result:**
- LLM instructions updated to not require percentages
- Only references percentages when actually provided
- More flexible and accurate recommendations

---

## UI Behavior

### Example 1: High-Confidence Match (85%)

**Tab Label:**
```
Option 1 (85% match)
```

**Progression Display:**
```
🎯 I - V - vi - IV          85%
                    Excellent Match
```

**Comparative Analysis:**
```
**Option 1** (85% match):
- Progression: I - V - vi - IV
...

Analysis: "Option 1 (85% match) is your best bet because..."
```

---

### Example 2: Lower-Confidence Match (70%)

**Tab Label:**
```
Option 2
```

**Progression Display:**
```
👍 I - IV - V - I
   Good Option
```

**Comparative Analysis:**
```
**Option 2**:
- Progression: I - IV - V - I
...

Analysis: "Option 2 is a solid choice that works well for..."
```

---

## User Experience Benefits

### 1. **Cleaner Interface**
- No overwhelming numbers for every option
- Focus on content, not scores
- Professional appearance

### 2. **Highlight Excellence**
- Percentages shown = high confidence
- Users know these are validated recommendations
- Builds trust in the system

### 3. **Reduced Confusion**
- Lower percentages might confuse users
- "Why is this 65% recommended?"
- Simpler UI = better UX

### 4. **Flexible Recommendations**
- All options are valid suggestions
- Percentage presence indicates "extra confidence"
- LLM can recommend any option freely

---

## Threshold: Why 75%?

**75% is a good cutoff because:**

1. **Psychological**: 75% = "C+ grade" = good enough to highlight
2. **Confidence**: Indicates solid semantic match
3. **User Trust**: Users trust 75%+ recommendations
4. **Balance**: Not too strict (90%) or too lenient (60%)

**Score Interpretation:**
- **85%+**: 🎯 Excellent Match (definitely show)
- **75-84%**: ✨ Great Match (show percentage)
- **<75%**: 👍 Good Option (hide percentage)

---

## Code Locations Summary

All percentage hiding logic in `src/app.py`:

| Location | Lines | Purpose | Status |
|----------|-------|---------|--------|
| Tab labels | 331-339 | Hide in tab names | ✅ Already done |
| Prog display | 360-371 | Hide in progression cards | ✅ Already done |
| Comp context | 495-506 | Hide in LLM context | ✅ NEW update |
| Comp prompt | 516-531 | Update LLM instructions | ✅ NEW update |

---

## Testing

### Verify Behavior:

1. **Generate progressions** with varying scores
2. **Check tab labels**: No % shown for scores <75%
3. **Check progression cards**: No % in header for scores <75%
4. **Check comparative analysis**: No invented percentages

### Expected Output:

**High Scores:**
```
Option 1 (92% match) | Option 2 (85% match) | Option 3 (78% match)
```

**Mixed Scores:**
```
Option 1 (85% match) | Option 2 | Option 3 (77% match)
```

**Low Scores:**
```
Option 1 | Option 2 | Option 3
```

---

## Future Considerations

### Potential Enhancements:

1. **Make threshold configurable**
   ```python
   SCORE_THRESHOLD = 75  # Show percentages only above this
   ```

2. **Different thresholds for different contexts**
   - Tabs: 75%
   - Cards: 70%
   - Analysis: 80%

3. **Visual indicators without percentages**
   - ⭐⭐⭐ (3 stars) instead of 85%
   - Progress bars
   - Color-coded badges

4. **Hover tooltips**
   - Show exact percentage on hover
   - Keep UI clean by default
   - Power users can see details

---

## Files Modified

1. ✅ **`src/app.py`** (4 lines changed)
   - Updated comparative analysis context building
   - Updated comparative analysis prompt instructions

---

**Status**: ✅ Complete

**Date**: November 9, 2024

**Impact**: 
- Cleaner UI throughout entire app
- Only high-confidence percentages shown
- More professional appearance
- Better user experience

---

**Result**: Percentages now only appear when they indicate strong matches (≥75%), keeping the interface clean and user-focused! 🎸✨

