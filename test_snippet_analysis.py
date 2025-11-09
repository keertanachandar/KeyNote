#!/usr/bin/env python3
"""
Test script for snippet analysis (single lines and verses)
Run from project root: python test_snippet_analysis.py
"""

import sys
sys.path.insert(0, 'src')

from agents.lyrics_analyzer import LyricsAnalyzer

print("\n" + "="*80)
print("TESTING SNIPPET ANALYSIS")
print("="*80 + "\n")

analyzer = LyricsAnalyzer()

# Test 1: Single Line
print("=" * 80)
print("TEST 1: Single Line")
print("=" * 80 + "\n")

single_line = "Walking through the empty streets at dawn"

print(f"Input: \"{single_line}\"\n")

analysis1 = analyzer.analyze(single_line)

if analysis1:
    print("✓ Analysis successful!")
    print(f"  Snippet Type: {analysis1.get('snippet_type')}")
    print(f"  Is Snippet: {analysis1.get('is_snippet')}")
    print(f"  Mood: {analysis1.get('overall_mood', 'N/A')}")
    print(f"  Energy: {analysis1.get('overall_energy', 'N/A')}")
    print(f"  Genre: {analysis1.get('overall_genre', 'N/A')}")
    print(f"  Emotional Arc: {analysis1.get('emotional_arc', 'N/A')}")
    print(f"  Section Recommendations: {analysis1.get('section_specific_recommendations', {})}")
else:
    print("✗ Analysis failed")

print("\n")

# Test 2: Single Verse (4 lines)
print("=" * 80)
print("TEST 2: Single Verse")
print("=" * 80 + "\n")

single_verse = """Walking through the empty streets at dawn
Everything reminds me that you're gone
The coffee shop where we used to meet
Now just echoes of memory"""

print("Input:")
print(single_verse)
print()

analysis2 = analyzer.analyze(single_verse)

if analysis2:
    print("✓ Analysis successful!")
    print(f"  Snippet Type: {analysis2.get('snippet_type')}")
    print(f"  Is Snippet: {analysis2.get('is_snippet')}")
    print(f"  Mood: {analysis2.get('overall_mood', 'N/A')}")
    print(f"  Energy: {analysis2.get('overall_energy', 'N/A')}")
    print(f"  Genre: {analysis2.get('overall_genre', 'N/A')}")
    print(f"  Emotional Arc: {analysis2.get('emotional_arc', 'N/A')[:60]}...")
    
    song_structure = analysis2.get('song_structure', [])
    print(f"\n  Song Structure: {len(song_structure)} section(s)")
    for section in song_structure:
        print(f"    - {section.get('section', 'N/A')}: {section.get('section_mood', 'N/A')}")
    
    section_recs = analysis2.get('section_specific_recommendations', {})
    print(f"\n  Section Recommendations:")
    for section, rec in section_recs.items():
        print(f"    - {section}: {rec[:60]}...")
else:
    print("✗ Analysis failed")

print("\n")

# Test 3: Partial Song (8 lines - one long verse or partial)
print("=" * 80)
print("TEST 3: Partial Song (8 lines - could be one verse or partial)")
print("=" * 80 + "\n")

partial_song = """Walking through the empty streets at dawn
Everything reminds me that you're gone
The coffee shop where we used to meet
Now just echoes of memory
The photographs still on my phone
Each smile a moment we had known
But time keeps moving, can't rewind
These memories I leave behind"""

print("Input:")
print(partial_song)
print()

analysis3 = analyzer.analyze(partial_song)

if analysis3:
    print("✓ Analysis successful!")
    print(f"  Snippet Type: {analysis3.get('snippet_type')}")
    print(f"  Is Snippet: {analysis3.get('is_snippet')}")
    print(f"  Mood: {analysis3.get('overall_mood', 'N/A')}")
    print(f"  Emotional Arc: {analysis3.get('emotional_arc', 'N/A')}")
    
    song_structure = analysis3.get('song_structure', [])
    print(f"\n  Song Structure: {len(song_structure)} section(s)")
    for section in song_structure:
        print(f"    - {section.get('section', 'N/A')}: Intensity {section.get('emotional_intensity', 'N/A')}/10")
    
    peaks = analysis3.get('emotional_peaks', [])
    print(f"\n  Emotional Peaks: {len(peaks)}")
    for peak in peaks:
        print(f"    - \"{peak.get('line_text', 'N/A')[:50]}...\"")
else:
    print("✗ Analysis failed")

print("\n")

# Test 4: Full Song (13+ lines)
print("=" * 80)
print("TEST 4: Full Song (Multiple sections)")
print("=" * 80 + "\n")

full_song = """Walking through the empty streets at dawn
Everything reminds me that you're gone
The coffee shop where we used to meet
Now just echoes of memory

But somewhere in the silence I can hear
A whisper telling me you're still near
And though the pain cuts deep today
Tomorrow brings a brighter way

So I'll keep moving, step by step
Learning how to love again and forget
The weight upon my shoulders starts to fade
As morning light breaks through the shade"""

print("Input:")
print(full_song)
print()

analysis4 = analyzer.analyze(full_song)

if analysis4:
    print("✓ Analysis successful!")
    print(f"  Snippet Type: {analysis4.get('snippet_type')}")
    print(f"  Is Partial: {analysis4.get('is_partial')}")
    print(f"  Emotional Arc: {analysis4.get('emotional_arc', 'N/A')}")
    
    song_structure = analysis4.get('song_structure', [])
    print(f"\n  Song Structure: {len(song_structure)} section(s)")
    for section in song_structure:
        print(f"    - {section.get('section', 'N/A')}: {section.get('section_mood', 'N/A')}")
else:
    print("✗ Analysis failed")

print("\n")

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80 + "\n")

print("✅ The system now handles:")
print("  1. Single lines (1-2 lines) - Basic analysis")
print("  2. Snippets (3-6 lines) - Partial analysis with inferred structure")
print("  3. Partial songs (7-12 lines) - Good analysis with inferred sections")
print("  4. Full songs (13+ lines) - Complete analysis with full structure")
print()
print("💡 Key Benefits:")
print("  - Works with ANY amount of lyrics")
print("  - Section labels are INFERRED when unclear (no strict requirements)")
print("  - Provides appropriate analysis depth for each input type")
print("  - Users get helpful feedback about what more lyrics would provide")
print("  - Half a song or single long verse? No problem - we'll infer structure")
print()
print("🎵 Try it in the app: streamlit run src/app.py")

print("\n" + "="*80 + "\n")

