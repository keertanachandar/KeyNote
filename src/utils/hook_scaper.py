"""
Hooktheory TheoryTab Scraper - Production Version
Extracts chord progressions with verified song examples from Hooktheory's database

Author: For KeyNote project
Usage: python hooktheory_scraper_v2.py
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import re
from typing import List, Dict, Optional
from collections import defaultdict

class HooktheoryScraperV2:
    """
    Advanced scraper for Hooktheory TheoryTab database
    Extracts progressions with real song examples and metadata
    """
    
    def __init__(self, delay: float = 2.0):
        """
        Args:
            delay: Seconds to wait between requests (be respectful!)
        """
        self.base_url = "https://www.hooktheory.com"
        self.delay = delay
        self.session = requests.Session()
        
        # Browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.progressions = []
        self.seen_progressions = set()  # Track to avoid duplicates
    
    def scrape_common_progressions_page(self, max_progressions: int = 150) -> List[Dict]:
        """
        Scrape the common chord progressions listing page
        
        Args:
            max_progressions: Maximum number of progressions to scrape
        
        Returns:
            List of progression dictionaries
        """
        print(f"🎵 Scraping common chord progressions from Hooktheory...")
        print(f"⏱️  Using {self.delay}s delay between requests")
        
        # Try the main common progressions page
        url = f"{self.base_url}/theorytab/common-chord-progressions"
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Failed to access {url}: Status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for progression links on the page
            progression_links = self._extract_progression_links(soup)
            
            if not progression_links:
                print("⚠️  No progression links found. Page structure may have changed.")
                print("Attempting alternative scraping method...")
                return self._scrape_individual_progression_pages(max_progressions)
            
            print(f"✓ Found {len(progression_links)} progression links")
            
            # Scrape each progression
            for i, link in enumerate(progression_links[:max_progressions], 1):
                print(f"\n📊 Scraping progression {i}/{min(len(progression_links), max_progressions)}")
                
                progression_data = self._scrape_progression_detail_page(link)
                
                if progression_data:
                    # Check for duplicates
                    prog_key = progression_data['progression_roman']
                    if prog_key not in self.seen_progressions:
                        self.progressions.append(progression_data)
                        self.seen_progressions.add(prog_key)
                        print(f"   ✓ Added: {progression_data['progression_roman']}")
                    else:
                        print(f"   ⊗ Skipped duplicate: {prog_key}")
                
                # Be respectful - delay between requests
                if i < len(progression_links):
                    time.sleep(self.delay)
            
        except Exception as e:
            print(f"❌ Error scraping common progressions: {e}")
            print("Attempting alternative method...")
            return self._scrape_individual_progression_pages(max_progressions)
        
        print(f"\n✅ Successfully scraped {len(self.progressions)} unique progressions")
        return self.progressions
    
    def _scrape_individual_progression_pages(self, max_count: int = 150) -> List[Dict]:
        """
        Fallback method: Try accessing progressions by ID
        URL pattern: /theorytab/common-chord-progressions/{id}
        """
        print("🔄 Trying individual progression page scraping...")
        
        for i in range(1, max_count + 1):
            url = f"{self.base_url}/theorytab/common-chord-progressions/{i}"
            
            try:
                print(f"   Trying progression #{i}...")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 404:
                    print(f"   ⊗ Progression #{i} not found")
                    continue
                
                if response.status_code != 200:
                    print(f"   ⚠️  Error {response.status_code}")
                    continue
                
                progression_data = self._parse_progression_page(response.content, i)
                
                if progression_data:
                    prog_key = progression_data['progression_roman']
                    if prog_key not in self.seen_progressions:
                        self.progressions.append(progression_data)
                        self.seen_progressions.add(prog_key)
                        print(f"   ✓ Added: {progression_data['progression_roman']}")
                
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"   ✗ Error on progression #{i}: {e}")
                continue
        
        return self.progressions
    
    def _extract_progression_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract progression detail page links from listing page"""
        links = []
        
        # Try different possible selectors
        selectors = [
            'a[href*="/theorytab/common-chord-progressions/"]',
            'a.progression-link',
            'div.progression-item a',
            'a[href*="/progressions/"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    href = elem.get('href')
                    if href and '/common-chord-progressions/' in href:
                        if not href.startswith('http'):
                            href = self.base_url + href
                        if href not in links:
                            links.append(href)
        
        return links
    
    def _scrape_progression_detail_page(self, url: str) -> Optional[Dict]:
        """Scrape a single progression detail page"""
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            return self._parse_progression_page(response.content, url)
            
        except Exception as e:
            print(f"   ✗ Error scraping {url}: {e}")
            return None
    
    def _parse_progression_page(self, html_content, source_id) -> Optional[Dict]:
        """
        Parse progression data from page HTML
        
        This is the core parsing logic - may need adjustment based on actual page structure
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            # Initialize progression data
            progression = {
                'progression_roman': None,
                'chords_example': None,
                'frequency': 'common',
                'genres': '',
                'mood': '',
                'example_songs': '',
                'source_url': f"{self.base_url}/theorytab/common-chord-progressions/{source_id}"
            }
            
            # === EXTRACT PROGRESSION (Roman Numerals) ===
            # Try multiple possible selectors
            progression_selectors = [
                'div.progression-display',
                'span.chord-notation',
                'div.chord-sequence',
                'h1.progression-title',
                '.theorytab-progression'
            ]
            
            for selector in progression_selectors:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    # Clean up the progression text
                    progression['progression_roman'] = self._clean_progression_text(text)
                    break
            
            # If still not found, try parsing from title or meta
            if not progression['progression_roman']:
                title = soup.find('title')
                if title:
                    # Extract progression from title like "I-V-vi-IV Progression"
                    match = re.search(r'([IViv\-\s]+)(?:Progression|Chord)', title.text)
                    if match:
                        progression['progression_roman'] = self._clean_progression_text(match.group(1))
            
            # === EXTRACT EXAMPLE SONGS ===
            songs = self._extract_songs(soup)
            if songs:
                progression['example_songs'] = ', '.join(songs[:5])  # Top 5 songs
                
                # Extract genres and moods from song metadata
                genres, moods = self._extract_genres_and_moods(soup, songs)
                progression['genres'] = ', '.join(list(set(genres))[:4])
                progression['mood'] = ', '.join(list(set(moods))[:4])
            
            # === GENERATE EXAMPLE CHORDS (in C major) ===
            if progression['progression_roman']:
                progression['chords_example'] = self._roman_to_chords(progression['progression_roman'])
            
            # === DETERMINE FREQUENCY ===
            song_count = len(songs)
            if song_count >= 100:
                progression['frequency'] = 'very_common'
            elif song_count >= 20:
                progression['frequency'] = 'common'
            else:
                progression['frequency'] = 'uncommon'
            
            # Validate we have minimum required data
            if not progression['progression_roman'] or not progression['example_songs']:
                return None
            
            return progression
            
        except Exception as e:
            print(f"   ✗ Parse error: {e}")
            return None
    
    def _extract_songs(self, soup: BeautifulSoup) -> List[str]:
        """Extract song titles and artists from page"""
        songs = []
        
        # Try different possible selectors
        song_selectors = [
            'div.song-item',
            'li.song-entry',
            'a.song-link',
            'div.theorytab-item'
        ]
        
        for selector in song_selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    song_text = elem.get_text(strip=True)
                    # Format: "Song Title (Artist)"
                    songs.append(song_text)
        
        # Also try parsing from links
        if not songs:
            song_links = soup.find_all('a', href=re.compile(r'/theorytab/view/'))
            for link in song_links:
                text = link.get_text(strip=True)
                if text:
                    songs.append(text)
        
        return songs
    
    def _extract_genres_and_moods(self, soup: BeautifulSoup, songs: List[str]) -> tuple:
        """Extract genres and infer moods from page"""
        genres = []
        moods = []
        
        # Try to find genre tags
        genre_selectors = [
            'span.genre-tag',
            'div.genre',
            'a.genre-link'
        ]
        
        for selector in genre_selectors:
            elements = soup.select(selector)
            for elem in elements:
                genre = elem.get_text(strip=True).lower()
                if genre:
                    genres.append(genre)
        
        # If no genres found, infer from song titles
        if not genres:
            genres = self._infer_genres_from_songs(songs)
        
        # Infer moods from progression characteristics
        # (This is heuristic-based)
        moods = self._infer_moods_from_context(soup, genres)
        
        return genres, moods
    
    def _infer_genres_from_songs(self, songs: List[str]) -> List[str]:
        """Infer genres from famous songs"""
        genre_keywords = {
            'rock': ['Beatles', 'Stones', 'Zeppelin', 'Queen', 'Guns'],
            'pop': ['Swift', 'Grande', 'Bieber', 'Perry', 'Gaga'],
            'indie': ['Bon Iver', 'Coldplay', 'Arctic Monkeys'],
            'country': ['Swift', 'Denver', 'Cash'],
            'jazz': ['Sinatra', 'Fitzgerald', 'Coltrane'],
            'blues': ['B.B. King', 'Clapton'],
            'folk': ['Dylan', 'Mitchell', 'Simon'],
        }
        
        inferred = []
        songs_text = ' '.join(songs).lower()
        
        for genre, keywords in genre_keywords.items():
            if any(keyword.lower() in songs_text for keyword in keywords):
                inferred.append(genre)
        
        return inferred if inferred else ['pop', 'rock']
    
    def _infer_moods_from_context(self, soup: BeautifulSoup, genres: List[str]) -> List[str]:
        """Infer moods from page context and genres"""
        moods = []
        
        # Look for mood-related keywords in page text
        page_text = soup.get_text().lower()
        
        mood_keywords = {
            'happy': ['happy', 'upbeat', 'cheerful', 'joyful', 'bright'],
            'sad': ['sad', 'melancholic', 'sorrowful', 'emotional'],
            'energetic': ['energetic', 'powerful', 'driving', 'intense'],
            'relaxed': ['relaxed', 'calm', 'mellow', 'smooth'],
            'dark': ['dark', 'heavy', 'moody', 'brooding'],
            'uplifting': ['uplifting', 'inspiring', 'hopeful', 'optimistic']
        }
        
        for mood, keywords in mood_keywords.items():
            if any(keyword in page_text for keyword in keywords):
                moods.append(mood)
        
        # Genre-based mood inference
        genre_moods = {
            'rock': ['energetic', 'powerful'],
            'pop': ['upbeat', 'catchy'],
            'indie': ['introspective', 'melancholic'],
            'jazz': ['smooth', 'sophisticated'],
            'blues': ['soulful', 'emotional']
        }
        
        for genre in genres:
            if genre in genre_moods:
                moods.extend(genre_moods[genre])
        
        return list(set(moods))[:4]  # Return up to 4 unique moods
    
    def _clean_progression_text(self, text: str) -> str:
        """Clean and standardize progression notation"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Ensure proper spacing around hyphens
        text = re.sub(r'\s*-\s*', ' - ', text)
        
        # Remove any trailing "Progression" or "Chord" text
        text = re.sub(r'(?i)\s*(progression|chord|chords)\s*$', '', text)
        
        return text.strip()
    
    def _roman_to_chords(self, roman: str, key: str = 'C') -> str:
        """
        Convert Roman numeral notation to actual chords in C major
        
        Args:
            roman: Roman numeral progression (e.g., "I - V - vi - IV")
            key: Key to convert to (default: C major)
        
        Returns:
            Chord names (e.g., "C - G - Am - F")
        """
        # C major scale
        major_scale = ['C', 'Dm', 'Em', 'F', 'G', 'Am', 'Bdim']
        
        # Mapping for different notations
        roman_to_index = {
            'I': 0, 'i': 0,
            'II': 1, 'ii': 1,
            'III': 2, 'iii': 2,
            'IV': 3, 'iv': 3,
            'V': 4, 'v': 4,
            'VI': 5, 'vi': 5,
            'VII': 6, 'vii': 6,
            'bII': 1, 'biii': 2, 'bVII': 6  # Flat notations
        }
        
        # Split progression
        numerals = [n.strip() for n in roman.split('-')]
        
        chords = []
        for numeral in numerals:
            # Remove any extra notation (6, 7, etc.)
            base_numeral = re.sub(r'[^IViv]+', '', numeral)
            
            if base_numeral in roman_to_index:
                idx = roman_to_index[base_numeral]
                chord = major_scale[idx]
                
                # Handle lowercase (minor)
                if numeral.startswith(('i', 'v')) and not numeral.startswith('iv'):
                    if not chord.endswith('m'):
                        chord = chord + 'm'
                
                chords.append(chord)
            else:
                chords.append(numeral)  # Keep original if can't parse
        
        return ' - '.join(chords)
    
    def remove_duplicates_from_existing(self, existing_csv_path: str):
        """
        Remove any progressions that already exist in your CSV
        
        Args:
            existing_csv_path: Path to existing progressions.csv
        """
        try:
            existing_df = pd.read_csv(existing_csv_path)
            existing_progs = set(existing_df['progression_roman'].str.strip())
            
            print(f"\n🔍 Checking for duplicates with {len(existing_progs)} existing progressions...")
            
            original_count = len(self.progressions)
            self.progressions = [
                p for p in self.progressions 
                if p['progression_roman'] not in existing_progs
            ]
            
            removed = original_count - len(self.progressions)
            print(f"   Removed {removed} duplicates")
            print(f"   Kept {len(self.progressions)} new progressions")
            
        except Exception as e:
            print(f"⚠️  Could not check for duplicates: {e}")
    
    def save_to_csv(self, filename: str = "hooktheory_new_progressions.csv"):
        """Save scraped progressions to CSV matching your format"""
        if not self.progressions:
            print("⚠️  No progressions to save")
            return
        
        # Create DataFrame with exact column order
        df = pd.DataFrame(self.progressions)
        
        # Ensure column order matches your existing CSV
        column_order = [
            'progression_roman',
            'chords_example',
            'frequency',
            'genres',
            'mood',
            'example_songs'
        ]
        
        # Only include columns that exist
        df = df[[col for col in column_order if col in df.columns]]
        
        # Save without index
        df.to_csv(filename, index=False)
        print(f"✅ Saved {len(df)} progressions to {filename}")
        
        # Also save backup JSON
        backup_file = filename.replace('.csv', '_backup.json')
        with open(backup_file, 'w') as f:
            json.dump(self.progressions, f, indent=2)
        print(f"✅ Backup saved to {backup_file}")
    
    def print_summary(self):
        """Print summary statistics"""
        if not self.progressions:
            print("No progressions scraped")
            return
        
        print(f"\n{'='*60}")
        print(f"SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Total progressions: {len(self.progressions)}")
        
        # Frequency distribution
        freq_counts = defaultdict(int)
        for p in self.progressions:
            freq_counts[p['frequency']] += 1
        
        print(f"\nFrequency distribution:")
        for freq, count in sorted(freq_counts.items()):
            print(f"  {freq}: {count}")
        
        # Show first few examples
        print(f"\nFirst 5 progressions:")
        for i, p in enumerate(self.progressions[:5], 1):
            print(f"\n{i}. {p['progression_roman']}")
            print(f"   Example: {p['chords_example']}")
            print(f"   Songs: {p['example_songs'][:80]}...")


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("🎵 Hooktheory TheoryTab Scraper for KeyNote")
    print("="*60)
    
    # Initialize scraper with 2-second delay (be respectful!)
    scraper = HooktheoryScraperV2(delay=2.0)
    
    # Scrape progressions
    print("\n⚠️  IMPORTANT: This will take several minutes due to rate limiting")
    print("⚠️  Please ensure you have permission to scrape Hooktheory")
    print("\nStarting in 5 seconds... (Ctrl+C to cancel)\n")
    
    time.sleep(5)
    
    # Scrape up to 150 progressions
    progressions = scraper.scrape_common_progressions_page(max_progressions=150)
    
    # Remove duplicates from your existing CSV
    scraper.remove_duplicates_from_existing("data/theorytab/progressions.csv")
    
    # Print summary
    scraper.print_summary()
    
    # Save results
    if progressions:
        scraper.save_to_csv("hooktheory_new_progressions.csv")
        print("\n✅ Done! Review hooktheory_new_progressions.csv before merging.")
    else:
        print("\n❌ No progressions were scraped. The page structure may have changed.")
        print("Consider using the GPT-4o generation approach instead.")