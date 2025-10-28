from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import json
import os
from dotenv import load_dotenv

load_dotenv()

class LyricsAnalyzer:
    """Agent that analyzes song lyrics to extract mood, themes, and musical characteristics"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt = PromptTemplate(
            input_variables=["lyrics"],
            template=f"""
You are a music analysis expert. Analyze these song lyrics to extract musical characteristics, song structure, and individual line emotional mapping.

Lyrics:
{lyrics}

Perform a comprehensive analysis that includes:

1. **Song Structure Detection**: Identify and label different sections (verse, chorus, bridge, pre-chorus, outro) if present
2. **Overall Theme Analysis**: Extract the main emotional and thematic content across the entire song
3. **Line-by-Line Emotional Mapping**: For each line, identify:
   - Emotional intensity (1-10 scale)
   - Mood/feeling of that specific line
   - Whether it's an emotional peak or resolution
   - Syllable count and pacing (fast/medium/slow)

Provide your analysis in this exact JSON format:
{{
    "mood": "1-3 mood keywords (e.g., melancholic, uplifting, dark)",
    "energy": "low, medium, or high",
    "themes": ["3-5 thematic keywords"],
    "style_indicators": ["musical style indicators like 'acoustic', 'intimate', 'anthemic'"],
    "suggested_genre": "likely genre (e.g., indie folk, pop rock)",
    "chord_characteristics": "brief description of what chord progressions would fit this mood and theme"
}}

Return ONLY valid JSON, nothing else."""
        )

# TODO: Alternative format that would require updated parsing logic
# {{
#     "overall_mood": "1-3 mood keywords describing the whole song (e.g., melancholic, uplifting, dark)",
#     "overall_energy": "low, medium, or high",
#     "overall_themes": ["3-5 thematic keywords that span the entire song"],
#     "overall_genre": "likely genre (e.g., indie folk, pop rock)",

#     "song_structure": [
#         {{
#             "section": "verse 1|chorus|bridge|etc",
#             "lines": ["first line", "second line", ...],
#             "emotional_intensity": "1-10 scale for this section",
#             "section_mood": "mood specific to this section",
#             "harmonic_needs": "what chord qualities would enhance this section"
#         }}
#     ],

#     "line_analysis": [
#         {{
#             "section": "verse 1|chorus|etc",
#             "line_number": 1,
#             "line_text": "the actual lyric line",
#             "emotional_intensity": "1-10",
#             "mood": "specific mood of this line",
#             "is_peak": true|false,
#             "is_resolution": true|false,
#             "syllable_count": 8,
#             "pacing": "fast|medium|slow",
#             "suggested_chord_quality": "what chord should underpin this line (major/minor/diminished/suspended)"
#         }}
#     ],

#     "emotional_peaks": [
#         {{
#             "section": "chorus",
#             "line_text": "the most climactic line",
#             "intensity": "1-10",
#             "harmonic_suggestion": "what specific chord progression would enhance this peak"
#         }}
#     ],

#     "section_specific_recommendations": {{
#         "verses": "what type of chord progressions work for verses",
#         "chorus": "what type of chord progressions work for chorus",
#         "bridge": "what type of chord progressions work for bridge (if present)"
#     }}
# }}
    
    def analyze(self, lyrics):
        """
        Analyze lyrics and return structured output
        
        Args:
            lyrics (str): Song lyrics to analyze
            
        Returns:
            dict: Analysis results or None if error
        """
        if not lyrics or len(lyrics.strip()) < 20:
            return None
        
        try:
            response = self.llm.invoke(
                self.prompt.format(lyrics=lyrics)
            )
            analysis = json.loads(response.content)
            return analysis
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parsing lyrics analysis JSON: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Lyrics analysis error: {e}")
            return None