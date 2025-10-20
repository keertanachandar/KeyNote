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
            template="""Analyze these song lyrics and extract musical characteristics.

Lyrics:
{lyrics}

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