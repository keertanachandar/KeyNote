# Enhanced Lyrics Analysis - System Update

## 🎯 Overview

KeyNote now features **advanced emotional arc tracking** and **section-specific chord progression recommendations**. The system goes beyond simple mood matching to analyze the entire emotional journey of your song, providing tailored chord progressions for verses, choruses, and bridges.

---

## ✨ What's New

### 1. **Emotional Arc Analysis**
- Tracks emotional journey (e.g., "heartbreak to hope," "nostalgia building to celebration")
- Matches progressions to storytelling flow
- Analyzes narrative themes beyond just mood keywords

### 2. **Section-Specific Analysis**
- Detects song structure (verse 1, verse 2, chorus, bridge, etc.)
- Provides unique harmonic recommendations for each section
- Tailors progressions to section intensity and mood

### 3. **Line-by-Line Emotional Mapping**
- Maps emotional intensity for every lyric line (1-10 scale)
- Identifies emotional peaks that need special harmonic treatment
- Suggests chord qualities (major/minor/suspended/diminished) per line
- Tracks pacing (fast/medium/slow) and syllable count

### 4. **Emotional Peak Identification**
- Automatically finds the most climactic moments
- Provides specific chord progression suggestions for peaks
- Helps you emphasize key emotional moments with harmony

### 5. **Section-Specific Progression Recommendations**
- Different progression styles for verses vs. choruses vs. bridges
- Considers section mood and intensity
- Supports dynamic songwriting with varied harmonic palettes

---

## 📊 New Analysis Output Structure

```json
{
  "overall_mood": "melancholic, hopeful, reflective",
  "overall_energy": "low to medium",
  "overall_themes": ["loss", "healing", "growth", "morning", "memory"],
  "overall_genre": "indie folk",
  "emotional_arc": "grief and nostalgia transitioning to acceptance and hope",
  
  "song_structure": [
    {
      "section": "verse 1",
      "lines": ["Walking through the empty streets at dawn", "..."],
      "emotional_intensity": "6",
      "section_mood": "melancholic, nostalgic",
      "harmonic_needs": "minor progressions with introspective feel"
    },
    {
      "section": "chorus",
      "lines": ["So I'll keep moving, step by step", "..."],
      "emotional_intensity": "8",
      "section_mood": "hopeful, determined",
      "harmonic_needs": "uplifting major progressions with resolution"
    }
  ],
  
  "line_analysis": [
    {
      "section": "verse 1",
      "line_number": 1,
      "line_text": "Walking through the empty streets at dawn",
      "emotional_intensity": "5",
      "mood": "lonely, melancholic",
      "is_peak": false,
      "is_resolution": false,
      "syllable_count": 11,
      "pacing": "medium",
      "suggested_chord_quality": "minor chord to establish somber mood"
    }
  ],
  
  "emotional_peaks": [
    {
      "section": "chorus",
      "line_text": "Learning how to love again and forget",
      "intensity": "9",
      "harmonic_suggestion": "IV-V-I resolution for cathartic emotional release"
    }
  ],
  
  "section_specific_recommendations": {
    "verses": "subdued minor progressions (vi-IV-I) for storytelling",
    "chorus": "uplifting major progressions (I-V-vi-IV) for hopeful resolution",
    "bridge": "unexpected chord changes or modulation to create emotional contrast"
  }
}
```

---

## 🔧 System Components Updated

### 1. **`src/agents/lyrics_analyzer.py`**

**Changes:**
- ✅ New comprehensive prompt template
- ✅ Enhanced JSON output structure with all new fields
- ✅ Better error handling and markdown stripping
- ✅ Field validation for required fields
- ✅ New `get_emotional_summary()` helper method

**Key Method:**
```python
analysis = analyzer.analyze(lyrics)
# Returns: dict with overall_mood, emotional_arc, song_structure, 
#          line_analysis, emotional_peaks, section_specific_recommendations
```

---

### 2. **`src/agents/langgraph_orchestrator.py`**

**Changes:**
- ✅ Updated field names (overall_mood, overall_energy, overall_genre)
- ✅ Uses emotional arc in progression search
- ✅ Includes section-specific needs in theory retrieval
- ✅ Enhanced synthesis with emotional peaks and section guidance
- ✅ Better logging of analysis results

**Enhanced Flow:**
1. **Lyrics Analysis** → Extracts emotional arc and section structure
2. **Progression Search** → Uses arc + mood + genre for better matching
3. **Theory Retrieval** → Includes section-specific harmonic needs
4. **Synthesis** → Generates section-specific recommendations with emotional arc guidance

---

### 3. **`src/utils/rag_system.py`**

**New Methods:**
- ✅ `search_progressions_by_section()` - Section-specific search (verse/chorus/bridge)
- ✅ `search_progressions_by_emotional_arc()` - Arc-aware progression matching

**Usage:**
```python
# Search progressions for specific song section
chorus_progressions = rag.search_progressions_by_section(
    section_type="chorus",
    harmonic_needs="anthemic uplifting major progressions",
    emotional_intensity=8,
    k=3
)

# Search progressions matching emotional journey
arc_progressions = rag.search_progressions_by_emotional_arc(
    emotional_arc="heartbreak to acceptance",
    overall_mood="melancholic hopeful",
    k=5
)
```

---

### 4. **`src/app.py`**

**Changes:**
- ✅ Enhanced UI expander with comprehensive analysis display
- ✅ Shows emotional arc prominently
- ✅ Displays song structure with section breakdowns
- ✅ Highlights emotional peaks with suggestions
- ✅ Shows section-specific recommendations

**New UI Sections:**
- 🎭 Overall Analysis (mood, energy, genre, themes, emotional arc)
- 📖 Song Structure (sections with intensity and harmonic needs)
- ⭐ Emotional Peaks (key moments with specific chord suggestions)
- 🎸 Section-Specific Recommendations (verse/chorus/bridge guidance)

---

## 🚀 How to Use

### Running the App

```bash
streamlit run src/app.py
```

**Paste lyrics and get:**
1. Emotional arc analysis
2. Section-specific chord recommendations
3. Emotional peak identification
4. Line-by-line harmonic suggestions

---

### Testing the System

```bash
python test_enhanced_analysis.py
```

**Tests:**
1. Enhanced lyrics analyzer with sample lyrics
2. RAG system integration with arc-based search
3. Full pipeline with orchestrator
4. Section-specific progression search

---

### Programmatic Usage

```python
from src.agents.lyrics_analyzer import LyricsAnalyzer
from src.utils.rag_system import ChordProgressionRAG
from src.agents.langgraph_orchestrator import LangGraphOrchestrator

# Analyze lyrics
analyzer = LyricsAnalyzer()
analysis = analyzer.analyze(your_lyrics)

# Get emotional summary
summary = analyzer.get_emotional_summary(analysis)

# Initialize RAG
rag = ChordProgressionRAG(chunks, "data/theorytab/progressions.csv")

# Search by emotional arc
arc_progressions = rag.search_progressions_by_emotional_arc(
    analysis['emotional_arc'],
    analysis['overall_mood']
)

# Search by section
chorus_progressions = rag.search_progressions_by_section(
    "chorus",
    analysis['section_specific_recommendations']['chorus'],
    emotional_intensity=8
)

# Run full pipeline
orchestrator = LangGraphOrchestrator(rag)
results = orchestrator.generate_recommendations(
    user_input="your description",
    lyrics=your_lyrics,
    reference_artists="optional artists"
)
```

---

## 📈 Benefits

### For Songwriters

✅ **Better Storytelling**: Match chord progressions to your emotional narrative  
✅ **Section Variety**: Get different suggestions for verses vs. choruses  
✅ **Emotional Peaks**: Emphasize climactic moments with specific harmonic choices  
✅ **Professional Structure**: Learn how to use harmony to support song structure  

### For the System

✅ **Richer Context**: More detailed analysis leads to better recommendations  
✅ **Semantic Matching**: Emotional arc enables better progression retrieval  
✅ **Educational Value**: Users learn *why* certain progressions fit their songs  
✅ **Advanced RAG**: Leverages narrative themes, not just keywords  

---

## 🔄 Backward Compatibility

All changes are **fully backward compatible**:
- Old field names (mood, energy, themes) map to new names (overall_mood, overall_energy, overall_themes)
- System gracefully handles missing fields
- Existing code continues to work without modifications
- New features are opt-in enhancements

---

## 🧪 Example Output

### Input Lyrics:
```
Walking through the empty streets at dawn
Everything reminds me that you're gone
But somewhere in the silence I can hear
Tomorrow brings a brighter way
```

### Enhanced Analysis:
- **Emotional Arc**: "grief transitioning to hope"
- **Verse 1**: Minor progressions (vi-IV-I) for melancholic storytelling
- **Chorus**: Major resolution (I-V-vi-IV) for hopeful uplift
- **Peak Moment**: "Tomorrow brings a brighter way" → IV-V-I for cathartic release

### Recommendations:
1. **Verse**: vi-IV-I-V (Am-F-C-G) - subdued, introspective
2. **Chorus**: I-V-vi-IV (C-G-Am-F) - hopeful resolution
3. **Bridge**: IV-vi-V (F-Am-G) - tension building

---

## 📝 API Reference

### LyricsAnalyzer

```python
class LyricsAnalyzer:
    def analyze(lyrics: str) -> dict:
        """Returns comprehensive analysis with emotional arc"""
        
    def get_emotional_summary(analysis: dict) -> str:
        """Returns concise summary of emotional journey"""
```

### ChordProgressionRAG

```python
class ChordProgressionRAG:
    def search_progressions_by_section(
        section_type: str,
        harmonic_needs: str,
        emotional_intensity: int = None,
        k: int = 3
    ) -> list:
        """Search progressions for specific song section"""
        
    def search_progressions_by_emotional_arc(
        emotional_arc: str,
        overall_mood: str,
        k: int = 5
    ) -> list:
        """Search progressions matching emotional journey"""
```

---

## 🎓 Next Steps

1. **Test it out**: Run `streamlit run src/app.py` and paste some lyrics
2. **Explore analysis**: Open the "View Comprehensive Lyrics Analysis" expander
3. **Try section-specific search**: Use new RAG methods programmatically
4. **Evaluate improvements**: Run `python test_enhanced_analysis.py`

---

## 📚 Documentation

- **README.md**: Updated with new features
- **USAGE_GUIDE.md**: Still relevant for basic usage
- **test_enhanced_analysis.py**: Comprehensive test suite
- **This file**: Complete feature documentation

---

## ✅ Summary

KeyNote now provides:
- 🎭 **Emotional arc tracking** for narrative-driven progression selection
- 📖 **Section-specific analysis** with tailored recommendations
- ⭐ **Emotional peak identification** for climactic moments
- 🎸 **Line-by-line mapping** with harmonic suggestions
- 🔍 **Advanced RAG methods** for section and arc-based search

**Result**: More personalized, contextual, and educationally valuable chord progression recommendations that match not just the mood, but the entire emotional journey of your song.

