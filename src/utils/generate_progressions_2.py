"""
High-Quality Chord Progression Generator using GPT-4o
Generates accurate, diverse progressions in JSON format

For KeyNote project - JSON-only version
"""

from openai import OpenAI
import os
import json
import time
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class ProgressionGenerator:
    """
    Generate high-quality chord progressions with real song examples using GPT-4o
    Outputs clean JSON format only
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.progressions = []
        self.existing_progressions = set()
    
    def load_existing_progressions(self, json_path: str):
        """Load existing progressions from JSON to avoid duplicates"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both list and dict formats
            if isinstance(data, list):
                progressions_list = data
            else:
                progressions_list = data.get('progressions', [])
            
            self.existing_progressions = set(
                p['progression_roman'].strip() 
                for p in progressions_list 
                if 'progression_roman' in p
            )
            print(f"✓ Loaded {len(self.existing_progressions)} existing progressions to avoid")
        except Exception as e:
            print(f"⚠️  Could not load existing: {e}")
    
    def generate_progressions_batch(self, 
                                   batch_size: int = 20,
                                   focus_genres: List[str] = None,
                                   focus_moods: List[str] = None) -> List[Dict]:
        """
        Generate a batch of progressions using GPT-4o
        
        Args:
            batch_size: Number of progressions to generate
            focus_genres: Optional list of genres to focus on
            focus_moods: Optional list of moods to focus on
        
        Returns:
            List of progression dictionaries
        """
        
        # Build focused prompt
        genre_focus = ""
        if focus_genres:
            genre_focus = f"\nFOCUS ON THESE GENRES: {', '.join(focus_genres)}"
        
        mood_focus = ""
        if focus_moods:
            mood_focus = f"\nFOCUS ON THESE MOODS: {', '.join(focus_moods)}"
        
        # Build exclusion list
        exclusion_text = ""
        if self.existing_progressions:
            sample_exclusions = list(self.existing_progressions)[:20]
            exclusion_text = f"\nDO NOT GENERATE THESE (already in database): {', '.join(sample_exclusions)}"
        
        prompt = f"""Generate {batch_size} chord progressions for a songwriting database.

Output as a JSON array with this EXACT structure (NO markdown code blocks, ONLY the JSON array):

CRITICAL RULES:
1. Output ONLY valid JSON - no markdown, no explanations, no code blocks
2. Each object must have exactly these 6 fields: progression_roman, chords_example, frequency, genres, mood, example_songs
3. Use REAL songs that ACTUALLY use these progressions
4. Double-check song accuracy before including
5. example_songs: "Song Title (Artist), Song Title 2 (Artist 2), Song Title 3 (Artist 3)"
6. frequency: "very_common", "common", or "uncommon"
7. genres: comma-separated string (e.g., "pop, rock, indie")
8. mood: comma-separated descriptive string (e.g., "melancholic, bittersweet")
9. Include diverse progressions: major and minor keys, 3-6 chord progressions
10. Cover wide range of genres and moods
{genre_focus}{mood_focus}{exclusion_text}

EXAMPLE OUTPUT FORMAT:
[
  {{
    "progression_roman": "I - V - vi - IV",
    "chords_example": "C - G - Am - F",
    "frequency": "very_common",
    "genres": "pop, rock",
    "mood": "uplifting, anthemic",
    "example_songs": "Don't Stop Believin (Journey), With Or Without You (U2), Someone Like You (Adele)"
  }},
  {{
    "progression_roman": "vi - IV - I - V",
    "chords_example": "Am - F - C - G",
    "frequency": "common",
    "genres": "pop, indie",
    "mood": "melancholic, bittersweet",
    "example_songs": "Let It Be (The Beatles), Apologize (OneRepublic), Skinny Love (Bon Iver)"
  }}
]

Now generate {batch_size} NEW progressions as a JSON array:"""

        try:
            print(f"🎵 Generating {batch_size} progressions with GPT-4o...")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a music theory expert who knows chord progressions of thousands of songs. You provide accurate, verified information about chord progressions and the songs that use them. You output ONLY valid JSON with no markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,  # Balance creativity and accuracy
                max_tokens=4000
            )
            
            json_text = response.choices[0].message.content.strip()
            
            # Clean response (remove markdown if present)
            json_text = json_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            new_progressions = self._parse_json_response(json_text)
            
            print(f"   ✓ Generated {len(new_progressions)} progressions")
            
            return new_progressions
            
        except Exception as e:
            print(f"   ✗ Error generating batch: {e}")
            return []
    
    def _parse_json_response(self, json_text: str) -> List[Dict]:
        """Parse JSON response into progression dictionaries"""
        progressions = []
        
        try:
            data = json.loads(json_text)
            
            # Ensure we have a list
            if not isinstance(data, list):
                print(f"   ⚠️  Expected JSON array, got {type(data)}")
                return []
            
            for item in data:
                # Validate and clean
                if self._validate_progression(item):
                    progressions.append(item)
                else:
                    print(f"   ⚠️  Skipping invalid: {item.get('progression_roman', 'Unknown')}")
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parsing error: {e}")
            print(f"   Response: {json_text[:200]}...")
        except Exception as e:
            print(f"   ⚠️  Error parsing JSON: {e}")
        
        return progressions
    
    def _validate_progression(self, prog: Dict) -> bool:
        """Validate progression data"""
        # Check required fields
        if not all([
            prog.get('progression_roman'),
            prog.get('chords_example'),
            prog.get('frequency'),
            prog.get('example_songs')
        ]):
            return False
        
        # Check frequency value
        if prog['frequency'] not in ['very_common', 'common', 'uncommon']:
            return False
        
        # Check for duplicates
        if prog['progression_roman'] in self.existing_progressions:
            return False
        
        # Check example songs format (should have at least one song)
        if '(' not in prog['example_songs']:
            return False
        
        return True
    
    def generate_by_category(self, target_count: int = 150) -> List[Dict]:
        """
        Generate progressions across different categories for diversity
        
        Args:
            target_count: Total number of progressions to generate
        
        Returns:
            List of all generated progressions
        """
        
        categories = [
            {
                'name': 'Pop & Rock Classics',
                'genres': ['pop', 'rock', 'indie rock'],
                'moods': ['uplifting', 'anthemic', 'energetic'],
                'count': 25
            },
            {
                'name': 'Melancholic & Emotional',
                'genres': ['indie', 'alternative', 'folk'],
                'moods': ['melancholic', 'bittersweet', 'introspective'],
                'count': 25
            },
            {
                'name': 'Jazz & Blues',
                'genres': ['jazz', 'blues', 'soul'],
                'moods': ['sophisticated', 'soulful', 'smooth'],
                'count': 20
            },
            {
                'name': 'Metal & Hard Rock',
                'genres': ['metal', 'hard rock', 'punk'],
                'moods': ['dark', 'heavy', 'aggressive'],
                'count': 20
            },
            {
                'name': 'Country & Folk',
                'genres': ['country', 'folk', 'americana'],
                'moods': ['nostalgic', 'storytelling', 'warm'],
                'count': 15
            },
            {
                'name': 'Electronic & Dance',
                'genres': ['electronic', 'dance', 'edm'],
                'moods': ['energetic', 'atmospheric', 'upbeat'],
                'count': 15
            },
            {
                'name': 'R&B & Hip Hop',
                'genres': ['r&b', 'hip hop', 'neo-soul'],
                'moods': ['smooth', 'romantic', 'groovy'],
                'count': 15
            },
            {
                'name': 'Experimental & Unique',
                'genres': ['experimental', 'progressive', 'avant-garde'],
                'moods': ['complex', 'unconventional', 'surprising'],
                'count': 15
            }
        ]
        
        all_progressions = []
        
        for i, category in enumerate(categories, 1):
            print(f"\n{'='*60}")
            print(f"Category {i}/{len(categories)}: {category['name']}")
            print(f"{'='*60}")
            
            batch_progs = self.generate_progressions_batch(
                batch_size=category['count'],
                focus_genres=category['genres'],
                focus_moods=category['moods']
            )
            
            # Add to existing progressions set to avoid future duplicates
            for prog in batch_progs:
                self.existing_progressions.add(prog['progression_roman'])
            
            all_progressions.extend(batch_progs)
            
            print(f"   Category total: {len(batch_progs)} progressions")
            print(f"   Running total: {len(all_progressions)} progressions")
            
            # Delay between batches to respect API rate limits
            if i < len(categories):
                print("   Waiting 5 seconds before next batch...")
                time.sleep(5)
        
        self.progressions = all_progressions
        return all_progressions
    
    def save_to_json(self, filename: str = "gpt4o_generated_progressions.json"):
        """Save generated progressions to JSON"""
        if not self.progressions:
            print("⚠️  No progressions to save")
            return
        
        # Save main file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.progressions, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(self.progressions)} progressions to {filename}")
        
        # Save timestamped backup
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = filename.replace('.json', f'_backup_{timestamp}.json')
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(self.progressions, f, indent=2, ensure_ascii=False)
        print(f"✅ Timestamped backup saved to {backup_file}")
    
    def print_summary(self):
        """Print generation summary"""
        if not self.progressions:
            print("No progressions generated")
            return
        
        print(f"\n{'='*60}")
        print(f"GENERATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total generated: {len(self.progressions)}")
        
        # Frequency distribution
        freq_counts = {}
        for p in self.progressions:
            freq = p['frequency']
            freq_counts[freq] = freq_counts.get(freq, 0) + 1
        
        print(f"\nFrequency distribution:")
        for freq, count in sorted(freq_counts.items()):
            print(f"  {freq}: {count}")
        
        # Genre coverage
        all_genres = set()
        for p in self.progressions:
            genres = [g.strip() for g in p['genres'].split(',')]
            all_genres.update(genres)
        
        print(f"\nGenre coverage: {len(all_genres)} unique genres")
        print(f"Genres: {', '.join(sorted(all_genres)[:10])}...")
        
        # Show samples
        print(f"\nSample progressions:")
        for i, p in enumerate(self.progressions[:3], 1):
            print(f"\n{i}. {p['progression_roman']}")
            print(f"   Example: {p['chords_example']}")
            print(f"   Genres: {p['genres']}")
            print(f"   Songs: {p['example_songs'][:80]}...")


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("🎵 GPT-4o Chord Progression Generator for KeyNote (JSON-only)")
    print("="*60)
    
    generator = ProgressionGenerator()
    
    # Load existing progressions to avoid duplicates
    generator.load_existing_progressions("data/theorytab/progressions.json")
    
    # Generate 150 diverse progressions across categories
    print("\n⚠️  This will make multiple GPT-4o API calls (costs ~$0.50-1.00)")
    print("⚠️  Generation will take 5-10 minutes with rate limiting")
    print("\nStarting in 5 seconds... (Ctrl+C to cancel)\n")
    
    time.sleep(5)
    
    progressions = generator.generate_by_category(target_count=150)
    
    # Print summary
    generator.print_summary()
    
    # Save results
    if progressions:
        generator.save_to_json("data/theorytab/gpt4o_generated_progressions.json")
        print("\n✅ Done! Review gpt4o_generated_progressions.json before merging.")
        print("\n💡 TIP: Manually verify a few song examples for accuracy before adding to your database.")
    else:
        print("\n❌ No progressions were generated. Check your API key and try again.")