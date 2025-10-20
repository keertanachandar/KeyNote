from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Updated prompt with YOUR column order and format
prompt = """Generate 40 additional chord progressions for a songwriting database.

Use this EXACT CSV format with columns in this order:
progression_roman,chords_example,frequency,genres,mood,example_songs

Example format:
"I - V - vi - IV","C - G - Am - F","very_common","pop,rock","uplifting,anthemic","Don't Stop Believin (Journey), With Or Without You (U2), Someone Like You (Adele)"
"vi - IV - I - V","Am - F - C - G","very_common","pop,indie","melancholic,bittersweet","Let It Be (The Beatles), Apologize (OneRepublic)"

IMPORTANT RULES:
1. Columns in order: progression_roman, chords_example, frequency, genres, mood, example_songs
2. Example songs format: "Song Title (Artist), Song Title 2 (Artist 2), Song Title 3 (Artist 3)"
3. Use REAL songs that actually use these progressions
4. Frequency values: very_common, common, uncommon
5. Include minor key progressions (lowercase roman numerals: i, iv, v)
6. Mix of 3-chord, 4-chord, and 5-chord progressions
7. Cover diverse genres: rock, indie, folk, pop, jazz, blues, country, electronic, metal
8. Cover diverse moods: happy, sad, dark, energetic, relaxed, mysterious, triumphant, melancholic

Generate 40 progressions covering a wide range of styles.
Output ONLY the CSV rows with NO headers, NO explanations, NO markdown code blocks."""

print("🎵 Generating progressions with GPT-4...")
print("This may take 30-60 seconds...\n")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)

content = response.choices[0].message.content

# Save to file
output_file = "data/theorytab/generated_progressions.csv"
with open(output_file, "w") as f:
    f.write(content)

print(f"✓ Generated {len(content.splitlines())} progressions")
print(f"✓ Saved to: {output_file}")
print("\n📋 Next steps:")
print("1. Open data/theorytab/generated_progressions.csv")
print("2. Review the progressions (delete any that look wrong)")
print("3. Append them to your main progressions.csv file")
