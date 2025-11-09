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
            template="""
You are an expert music analyst specializing in emotional arc analysis and harmonic storytelling.

Analyze these song lyrics to extract comprehensive musical characteristics, emotional narrative, and section-specific chord recommendations.

Lyrics:
{lyrics}

Perform a DEEP analysis that tracks the emotional journey of the song:

1. **Overall Analysis**: Capture the song's overarching mood, energy, themes, and genre
2. **Song Structure**: Break down into sections (verse 1, verse 2, chorus, bridge, pre-chorus, outro, etc.)
3. **Emotional Arc**: Track how emotions evolve through the song (e.g., "heartbreak to hope," "nostalgia building to celebration")
4. **Line-by-Line Mapping**: Analyze each line's emotional intensity, mood, and harmonic needs
5. **Identify Peaks**: Find the most emotionally intense moments that need specific harmonic treatment
6. **Section-Specific Recommendations**: Suggest chord progression characteristics for each section type

Return your analysis in this EXACT JSON format (valid JSON only, no markdown):
{{
    "overall_mood": "1-3 mood keywords describing the whole song (e.g., melancholic, uplifting, dark)",
    "overall_energy": "low, medium, or high",
    "overall_themes": ["3-5 thematic keywords that span the entire song"],
    "overall_genre": "likely genre (e.g., indie folk, pop rock, alternative)",
    "emotional_arc": "describe the emotional journey/narrative (e.g., 'heartbreak to acceptance', 'nostalgia building to hope', 'celebration throughout'). If partial lyrics, infer the arc from what's provided.",
    
    "song_structure": [
        {{
            "section": "verse 1 (or your best guess: verse, chorus, bridge, or 'section' if unclear)",
            "lines": ["first line of this section", "second line", "etc"],
            "emotional_intensity": "1-10 scale for this section's average intensity",
            "section_mood": "mood specific to this section",
            "harmonic_needs": "what chord qualities would enhance this section (e.g., 'minor progressions with melancholic feel', 'uplifting major chords')"
        }}
    ],
    
    NOTE: If you can't determine exact section types (verse vs chorus), just make your best inference or label as "section 1", "section 2", etc. It's OK to have uncertain section labels.
    
    "line_analysis": [
        {{
            "section": "verse 1",
            "line_number": 1,
            "line_text": "the actual lyric line",
            "emotional_intensity": "1-10",
            "mood": "specific mood of this line",
            "is_peak": false,
            "is_resolution": false,
            "syllable_count": 8,
            "pacing": "fast, medium, or slow",
            "suggested_chord_quality": "major/minor/suspended/diminished and why"
        }}
    ],
    
    "emotional_peaks": [
        {{
            "section": "chorus",
            "line_text": "the most climactic line",
            "intensity": "1-10",
            "harmonic_suggestion": "specific chord progression or quality (e.g., 'IV-V-I resolution for cathartic release', 'vi-IV-I-V for anthemic feel')"
        }}
    ],
    
    "section_specific_recommendations": {{
        "verses": "chord progression characteristics for verses (e.g., 'subdued minor progressions, I-vi-IV', 'storytelling flow with ii-V-I')",
        "chorus": "chord progression characteristics for chorus (e.g., 'anthemic I-V-vi-IV', 'climactic IV-V resolution')",
        "bridge": "chord progression characteristics for bridge if present (e.g., 'unexpected modulation to relative major', 'tension-building with suspended chords')"
    }}
}}

CRITICAL: Return ONLY the JSON object. No markdown, no code blocks, no explanations."""
        )
    
    def _detect_snippet_type(self, lyrics):
        """
        Detect if input is a snippet or potentially partial song
        
        Returns:
            str: "single_line", "snippet", "partial_song", or "full_song"
        """
        lines = [line.strip() for line in lyrics.strip().split('\n') if line.strip()]
        
        if len(lines) <= 2:
            return "single_line"
        elif len(lines) <= 6:
            return "snippet"
        elif len(lines) <= 12:
            # Could be a single long verse or partial song
            return "partial_song"
        else:
            # Likely a more complete song
            return "full_song"
    
    def analyze(self, lyrics):
        """
        Analyze lyrics and return enhanced structured output with emotional arc
        
        Works with full songs, single verses, or even single lines.
        For snippets, some fields may be limited or inferred.
        
        Args:
            lyrics (str): Song lyrics to analyze (can be full song or snippet)
            
        Returns:
            dict: Enhanced analysis results with structure:
                - overall_mood: Overall mood keywords
                - overall_energy: Energy level
                - overall_themes: Thematic keywords
                - overall_genre: Suggested genre
                - emotional_arc: Emotional journey description (inferred for snippets)
                - song_structure: List of sections with lines and analysis
                - line_analysis: Line-by-line emotional mapping
                - emotional_peaks: Key emotional moments
                - section_specific_recommendations: Chord suggestions per section
                - is_snippet: Boolean indicating if this is a partial song
                
            Returns None if error or lyrics too short
        """
        if not lyrics or len(lyrics.strip()) < 20:
            return None
        
        # Detect if this is a snippet
        snippet_type = self._detect_snippet_type(lyrics)
        
        try:
            # Add context hint to prompt based on input type
            if snippet_type == "single_line":
                context_hint = "\n\nNOTE: This is a SINGLE LINE from a song. Provide your best analysis based on this line alone. For fields that require more context (like full song structure), provide reasonable inferences or mark as 'partial/inferred'."
            elif snippet_type == "snippet":
                context_hint = "\n\nNOTE: This is a SNIPPET (single verse or partial lyrics). Analyze what's provided and make reasonable inferences. For song_structure, only include the section(s) you can identify. If you can't determine the exact section (verse/chorus/bridge), label it as 'verse' or 'section' with a note."
            elif snippet_type == "partial_song":
                context_hint = "\n\nNOTE: This appears to be PARTIAL LYRICS (possibly one long verse, half a song, or missing sections). Analyze what's provided thoroughly. For song_structure, infer section types as best you can (e.g., if it feels like a verse, call it verse 1; if repetitive, maybe a chorus). Mark emotional_arc and section_specific_recommendations as 'inferred from partial lyrics' where appropriate. It's OK if some sections are unclear."
            else:
                context_hint = "\n\nNOTE: Analyze the full song structure. If you're uncertain about exact section labels, make your best inference."
            
            # Invoke LLM with context
            full_prompt = self.prompt.format(lyrics=lyrics) + context_hint
            response = self.llm.invoke(full_prompt)
            
            # Clean response content (remove markdown if present)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(content)
            
            # Add snippet/partial indicator
            analysis['is_snippet'] = (snippet_type not in ["full_song"])
            analysis['is_partial'] = (snippet_type in ["partial_song", "snippet", "single_line"])
            analysis['snippet_type'] = snippet_type
            
            # Validate CORE fields only (structure fields are now optional/inferred)
            required_core_fields = [
                "overall_mood", "overall_energy", "overall_themes", 
                "overall_genre", "emotional_arc"
            ]
            
            missing_core_fields = []
            for field in required_core_fields:
                if field not in analysis:
                    missing_core_fields.append(field)
            
            if missing_core_fields:
                print(f"⚠️  Missing required core fields: {missing_core_fields}")
                return None
            
            # For single lines, provide minimal defaults only if completely missing
            if snippet_type == "single_line":
                analysis.setdefault('song_structure', [{
                    'section': 'unknown',
                    'lines': lyrics.split('\n'),
                    'emotional_intensity': 'N/A',
                    'section_mood': analysis.get('overall_mood', 'N/A'),
                    'harmonic_needs': 'Cannot determine from single line'
                }])
                analysis.setdefault('line_analysis', [])
                analysis.setdefault('emotional_peaks', [])
                analysis.setdefault('section_specific_recommendations', {
                    'verses': 'Insufficient context from single line',
                    'chorus': 'Insufficient context from single line',
                    'bridge': 'Insufficient context from single line'
                })
            
            # For all other types, set empty defaults if missing (LLM should provide these)
            analysis.setdefault('song_structure', [])
            analysis.setdefault('line_analysis', [])
            analysis.setdefault('emotional_peaks', [])
            analysis.setdefault('section_specific_recommendations', {})
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parsing lyrics analysis JSON: {e}")
            print(f"Response content: {response.content[:200]}...")
            return None
        except Exception as e:
            print(f"⚠️  Lyrics analysis error: {e}")
            return None
    
    def get_emotional_summary(self, analysis):
        """
        Extract a concise emotional summary from the analysis
        
        Args:
            analysis (dict): Full lyrics analysis
            
        Returns:
            str: Human-readable emotional summary
        """
        if not analysis:
            return "No lyrics analysis available"
        
        mood = analysis.get('overall_mood', 'unknown')
        arc = analysis.get('emotional_arc', 'unclear emotional journey')
        energy = analysis.get('overall_energy', 'medium')
        
        return f"{mood} ({energy} energy) - {arc}"