# Snippet Handling - Single Lines & Partial Lyrics

## 🎯 Overview

KeyNote now intelligently handles **any amount of lyrics** - from single lines to full songs. The system automatically detects snippet length and adjusts its analysis accordingly.

---

## 📊 Detection Logic

The system categorizes your input as:

| Type | Line Count | Description | Analysis Depth |
|------|------------|-------------|----------------|
| **Single Line** | 1-2 lines | A single lyric line | Basic mood/theme only |
| **Snippet** | 3-6 lines | Single verse or short passage | Partial structure analysis |
| **Partial Song** | 7-12 lines | One long verse, half a song, or missing sections | Good analysis with **inferred** structure |
| **Full Song** | 13+ lines | Multiple complete sections | Complete emotional arc analysis |

**Key Point:** For partial songs and snippets, **section labels are inferred** - the LLM makes its best guess at whether something is a verse, chorus, or simply labels it as "section 1", "section 2", etc. This is intentionally flexible.

---

## 🔍 What You Get with Each Type

### Single Line (1-2 lines)
**Example:** `"Walking through the empty streets at dawn"`

**Analysis Includes:**
- ✅ Overall mood (inferred from line)
- ✅ Overall energy
- ✅ Overall themes
- ✅ Overall genre (suggested)
- ✅ Emotional arc (inferred)
- ⚠️ Limited section recommendations
- ⚠️ No emotional peaks
- ⚠️ No detailed structure

**UI Feedback:**
> ✓ Lyrics analyzed (single line - limited analysis)  
> 💡 Tip: For more comprehensive analysis with emotional arc and section-specific recommendations, provide multiple verses or the full song.

---

### Snippet (3-6 lines)
**Example:**
```
Walking through the empty streets at dawn
Everything reminds me that you're gone
The coffee shop where we used to meet
Now just echoes of memory
```

**Analysis Includes:**
- ✅ Overall mood
- ✅ Overall energy
- ✅ Overall themes
- ✅ Overall genre
- ✅ Emotional arc (inferred from snippet)
- ✅ Song structure (single section)
- ✅ Line-by-line analysis (for provided lines)
- ✅ Emotional peaks (if present)
- ✅ Section recommendations (inferred)

**UI Feedback:**
> ✓ Lyrics analyzed (snippet - partial analysis)  
> 💡 Tip: Analysis based on snippet. For complete emotional arc and section recommendations, provide the full song.

---

### Partial Song (7-12 lines)
**Example:**
```
Walking through the empty streets at dawn
Everything reminds me that you're gone
The coffee shop where we used to meet
Now just echoes of memory
The photographs still on my phone
Each smile a moment we had known
But time keeps moving, can't rewind
These memories I leave behind
```

**Analysis Includes:**
- ✅ Overall mood (good inference)
- ✅ Overall energy
- ✅ Overall themes
- ✅ Overall genre
- ✅ Emotional arc (inferred from partial lyrics)
- ✅ Song structure (**inferred** - might be labeled as "verse 1" or "section" if unclear)
- ✅ Line-by-line analysis (for all provided lines)
- ✅ Emotional peaks (if present)
- ✅ Section recommendations (**inferred** based on what's provided)

**UI Feedback:**
> ✓ Lyrics analyzed (partial song - inferred structure)  
> 💡 Tip: Section labels (verse/chorus/bridge) are inferred from partial lyrics. For most accurate structure, provide the complete song.

**Important:** 
- The LLM will do its best to identify if sections are verses, choruses, or bridges
- If uncertain, it may label sections as "section 1", "section 2", etc.
- This is intentional - we provide useful analysis even when structure is ambiguous
- Works great for "half a song" or "one long verse" scenarios

---

### Full Song (13+ lines)
**Example:** Complete verses, chorus, bridge, etc.

**Analysis Includes:**
- ✅ **Complete** overall analysis
- ✅ **Full** emotional arc tracking
- ✅ **Detailed** song structure (verse 1, verse 2, chorus, bridge)
- ✅ **Comprehensive** line-by-line analysis
- ✅ **Accurate** emotional peaks
- ✅ **Precise** section-specific recommendations

**UI Feedback:**
> ✓ Lyrics analyzed with emotional arc tracking

---

## 💻 Technical Implementation

### Snippet Detection

```python
def _detect_snippet_type(self, lyrics):
    """
    Detect if input is a snippet, partial, or full song
    
    Returns:
        str: "single_line", "snippet", "partial_song", or "full_song"
    """
    lines = [line.strip() for line in lyrics.strip().split('\n') if line.strip()]
    
    if len(lines) <= 2:
        return "single_line"
    elif len(lines) <= 6:
        return "snippet"
    elif len(lines) <= 12:
        return "partial_song"  # Could be one long verse or half a song
    else:
        return "full_song"
```

### Adaptive Prompting

The system adds context hints to the LLM prompt based on snippet type:

```python
if snippet_type == "single_line":
    context_hint = "This is a SINGLE LINE. Provide best analysis based on this line alone."
elif snippet_type == "snippet":
    context_hint = "This is a SNIPPET. Analyze and make reasonable inferences. Label sections as best you can."
elif snippet_type == "partial_song":
    context_hint = "This appears to be PARTIAL LYRICS (one long verse, half a song, or missing sections). Infer section types as best you can. It's OK if some sections are unclear - label them as 'section 1', 'section 2', etc. if needed."
else:
    context_hint = "Analyze the full song. Make your best inference for section labels."
```

**Key Feature:** The prompt explicitly tells the LLM it's OK to be uncertain about section labels and to use generic labels like "section 1" if it can't determine verse vs. chorus.

### Flexible Validation

**Old approach:** Required all fields (song_structure, line_analysis, etc.)  
**New approach:** Only requires core fields (mood, energy, themes, genre, emotional_arc)

```python
# Validate CORE fields only (structure fields are now optional/inferred)
required_core_fields = [
    "overall_mood", "overall_energy", "overall_themes", 
    "overall_genre", "emotional_arc"
]

# Structure fields are optional - LLM provides them if it can
analysis.setdefault('song_structure', [])
analysis.setdefault('line_analysis', [])
analysis.setdefault('emotional_peaks', [])
analysis.setdefault('section_specific_recommendations', {})
```

**Result:** The system works with ANY amount of lyrics. Section labels are inferred, not required.

---

## 📝 Example Usage

### Using the App

```bash
streamlit run src/app.py
```

**Single Line Example:**
```
Input: "Tomorrow brings a brighter way"

Output:
✓ Lyrics analyzed (single line - limited analysis)
💡 Tip: For more comprehensive analysis...

Mood: hopeful, optimistic
Energy: medium
Genre: pop, indie
Emotional Arc: Looking forward to better times
```

**Partial Song Example:**
```
Input: [8 lines - could be one verse or partial]

Output:
✓ Lyrics analyzed (partial song - inferred structure)
💡 Tip: Section labels are inferred from partial lyrics...

Emotional Arc: Loss and moving forward (inferred)
Song Structure: 
  - verse 1 or section (lines 1-8): melancholic, introspective
Emotional Peaks: May identify key moments
Section Recommendations: Inferred based on mood and content
```

**Full Song Example:**
```
Input: [13+ lines with multiple sections]

Output:
✓ Lyrics analyzed with emotional arc tracking

Emotional Arc: grief transitioning to acceptance and hope
Song Structure: verse 1, verse 2, chorus
Emotional Peaks: 2 identified
Section Recommendations: Different for verse vs. chorus
```

---

### Programmatic Usage

```python
from src.agents.lyrics_analyzer import LyricsAnalyzer

analyzer = LyricsAnalyzer()

# Single line
analysis = analyzer.analyze("Walking through the empty streets at dawn")
print(f"Snippet Type: {analysis['snippet_type']}")  # "single_line"
print(f"Is Partial: {analysis['is_partial']}")      # True

# Snippet (4 lines)
analysis = analyzer.analyze("""
Walking through the empty streets at dawn
Everything reminds me that you're gone
The coffee shop where we used to meet
Now just echoes of memory
""")
print(f"Snippet Type: {analysis['snippet_type']}")  # "snippet"
print(f"Is Partial: {analysis['is_partial']}")      # True

# Partial song (8 lines - one verse or half song)
analysis = analyzer.analyze("""
[8 lines of lyrics - could be one long verse]
""")
print(f"Snippet Type: {analysis['snippet_type']}")  # "partial_song"
print(f"Is Partial: {analysis['is_partial']}")      # True
# Section labels will be inferred!

# Full song (13+ lines)
analysis = analyzer.analyze("""
[13+ lines of lyrics with multiple sections]
""")
print(f"Snippet Type: {analysis['snippet_type']}")  # "full_song"
print(f"Is Partial: {analysis['is_partial']}")      # False
```

---

## 🧪 Testing

Run the snippet test suite:

```bash
python test_snippet_analysis.py
```

**Tests:**
1. Single line analysis
2. Single verse analysis (4 lines)
3. Two verses detection (full song)

---

## 💡 Best Practices

### For Users

✅ **Best Results**: Provide full songs with multiple sections (13+ lines)  
✅ **Great Results**: Half a song or partial lyrics (7-12 lines) - structure will be inferred  
✅ **Good Results**: Single verse (4-6 lines) - partial analysis with inferred structure  
✅ **Basic Results**: Single lines work but give basic analysis only  

**Important:** Don't worry about perfect section labels! The system will infer what it can.  

### For Developers

✅ **Always check** `is_partial` field in results (replaces `is_snippet`)  
✅ **Handle gracefully** when section labels might be generic ("section 1" vs "verse 1")  
✅ **Show UI hints** to users when analyzing partial lyrics  
✅ **Consider context** when using partial analysis for recommendations  
✅ **Don't require** specific section labels - the system infers them flexibly  

---

## 🔄 Backward Compatibility

All existing code continues to work:
- Full songs get complete analysis (no changes)
- Snippets now work instead of failing
- Single lines now provide basic analysis

**Fields Added:**
- `is_partial`: Boolean indicating if input was partial/incomplete
- `is_snippet`: Boolean (deprecated, use `is_partial`)
- `snippet_type`: "single_line", "snippet", "partial_song", or "full_song"

**Validation Changes:**
- Only requires core fields (mood, energy, themes, genre, emotional_arc)
- Structure fields (song_structure, line_analysis, etc.) are **optional**
- LLM infers section labels flexibly (can use "section 1" if uncertain)
- Returns `None` only for truly invalid input (< 20 chars)

---

## 🎯 Why This Matters

### User Experience
✅ **No more errors** when pasting a single verse or half a song  
✅ **Clear feedback** about analysis limitations and what's inferred  
✅ **Useful results** even with minimal input  
✅ **Flexible structure** - section labels are inferred, not required  
✅ **Encouragement** to provide more lyrics for better accuracy  

### System Robustness
✅ **Handles edge cases** gracefully (one long verse, half a song, etc.)  
✅ **Provides partial value** instead of failing  
✅ **Educational feedback** guides users to better input  
✅ **Flexible analysis** adapts to input length  
✅ **Inferred structure** - no strict requirements for section labels  

---

## 📚 Documentation Links

- **Main README**: General usage
- **ENHANCED_LYRICS_ANALYSIS_UPDATE**: Full feature docs
- **test_snippet_analysis.py**: Test examples
- **This file**: Snippet handling details

---

## ✅ Summary

KeyNote now intelligently handles:
- ✅ **Single lines** (1-2 lines) - Basic analysis
- ✅ **Snippets** (3-6 lines) - Partial analysis with inferred structure
- ✅ **Partial songs** (7-12 lines) - **Good analysis with inferred sections** (half a song, one long verse, etc.)
- ✅ **Full songs** (13+ lines) - Complete analysis with accurate structure

**Key Feature:** Section labels (verse/chorus/bridge) are **inferred** by the LLM. If it's uncertain, it uses generic labels like "section 1", "section 2". This means the system works with ANY amount of lyrics!

**Result:** Users can paste any amount of lyrics and get useful results, with clear feedback about what's being inferred.

**Test it:** `python test_snippet_analysis.py` or `streamlit run src/app.py`

