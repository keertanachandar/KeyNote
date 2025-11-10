import streamlit as st
from utils.pdf_loader import load_music_theory_pdfs, chunk_documents
from utils.rag_system import ChordProgressionRAG
from utils.transposer import ChordTransposer
from utils.chord_player import play_chord_progression
from agents.langgraph_orchestrator import LangGraphOrchestrator
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page config
st.set_page_config(
    page_title="KeyNote", 
    page_icon="🎸",
    layout="wide"
)

# Initialize system (cached so it only runs once)
# Note: Clear cache if you update the code: Streamlit menu > Clear cache
@st.cache_resource
def initialize_system():
    """Initialize RAG system and orchestrator"""
    print("\n" + "="*60)
    print("INITIALIZING KEYNOTE")
    print("="*60)
    
    # Load PDFs with caching and vision
    # First load: ~2-5 min (vision API), subsequent loads: <5 sec (cached)
    # Set use_vision=False to skip GPT-4 Vision (faster, text-only extraction)
    docs = load_music_theory_pdfs("data/pdfs", use_cache=True, use_vision=False)

    chunks = chunk_documents(docs) if docs else []
    
    # Initialize RAG (in-memory for now due to version compatibility)
    # Now using JSON format for cleaner data structure
    # Using consolidated, deduplicated progressions (138 unique progressions)
    rag = ChordProgressionRAG(
        chunks, 
        "data/theorytab/progressions.json",
        use_persistent_storage=False  # Using in-memory for compatibility
    )
    
    # Initialize orchestrator
    orchestrator = LangGraphOrchestrator(rag)
    
    print("="*60)
    print("KEYNOTE READY")
    print("="*60 + "\n")
    
    return orchestrator

# Header
st.title("🎸 KeyNote")
st.markdown("*AI-Powered Chord Progression Assistant for Songwriters*")
st.markdown("Transform your lyrics and musical ideas into personalized chord progressions with AI analysis of 50+ progressions, current trends, and music theory.")
st.markdown("---")

# Initialize system
try:
    with st.spinner("Initializing KeyNote... (first load: 2-5 min, subsequent loads: <5 sec)"):
        orchestrator = initialize_system()
    st.success("✓ KeyNote is ready!")
except Exception as e:
    st.error(f"❌ Initialization error: {e}")
    st.exception(e)
    st.stop()

# Input form
with st.form("input_form"):
    st.markdown("### 🎵 Describe Your Song")
    st.caption("Provide either a description OR lyrics (or both for best results)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        user_input = st.text_input(
            "Song Description",
            placeholder="melancholic indie folk, slow tempo",
            help="Describe the mood, genre, tempo, or vibe of your song"
        )
    
    with col2:
        reference_artists = st.text_input(
            "Reference Artists (Optional)",
            placeholder="Phoebe Bridgers, Bon Iver",
            help="Artists whose style you want to emulate"
        )
    
    lyrics = st.text_area(
        "Your Lyrics",
        placeholder="Walking through the empty streets at dawn\nEverything reminds me that you're gone\nThe coffee shop where we used to meet\nNow just echoes of memory",
        height=150,
        help="Paste a verse, chorus, or full song - we'll analyze the emotional tone and themes. Works with any amount of lyrics!"
    )
    
    # Key selection
    st.markdown("### 🎹 Choose Your Key")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        preferred_key = st.selectbox(
            "Preferred Key",
            options=["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"],
            index=0,
            help="All chord progressions will be shown in this key. Choose a key comfortable for your vocal range."
        )
    
    with col2:
        vocal_range = st.selectbox(
            "Vocal Range (Optional)",
            options=["", "Low (Bass/Contralto)", "Medium-Low (Baritone/Alto)", "Medium (Tenor/Mezzo)", "High (Soprano)"],
            help="Get key suggestions based on your vocal range"
        )
    
    submit = st.form_submit_button("🎵 Generate Chord Progressions", use_container_width=True, type="primary")

# Process - Generate results on form submit
if submit:
    if not user_input and not lyrics:
        st.error("⚠️  Please provide either a song description OR lyrics (or both for best results)!")
    else:
        with st.spinner("🎵 Analyzing your song and generating recommendations..."):
            try:
                # Store selected key in session state
                st.session_state['selected_key'] = preferred_key
                st.session_state['vocal_range'] = vocal_range
                
                # If no description but lyrics provided, create a better search query
                if not user_input and lyrics:
                    # Don't use lyrics directly - use placeholder for analysis
                    query = "chord progressions for songwriting"  # Generic but will be enhanced by lyrics analysis
                else:
                    query = user_input
                
                # Run orchestrator (it will enhance query with lyrics analysis)
                results = orchestrator.generate_recommendations(
                    query, 
                    lyrics if lyrics else None,
                    reference_artists if reference_artists else None
                )
                
                # Initialize transposer
                transposer = ChordTransposer(rag_system=orchestrator.rag)
                
                # Transpose all progressions to the selected key
                transposed_progressions = []
                for item in results['progressions']:
                    # Handle both old format (Document) and new format (dict)
                    if isinstance(item, dict) and 'progression' in item:
                        prog = item['progression']
                        match_score = item.get('match_score', 75)
                    else:
                        prog = item
                        match_score = 75
                    
                    # Transpose the progression
                    transposed_data = transposer.transpose_progression_smart(
                        prog.metadata if hasattr(prog, 'metadata') else prog,
                        preferred_key,
                        use_theory=False  # Skip theory lookup for speed
                    )
                    
                    # Update the document's metadata with transposed chords
                    if hasattr(prog, 'metadata'):
                        prog.metadata.update(transposed_data)
                    
                    transposed_progressions.append({
                        'progression': prog,
                        'match_score': match_score
                    })
                
                # Update results with transposed progressions
                results['progressions'] = transposed_progressions
                
                # Store results in session state
                st.session_state['results'] = results
                st.session_state['original_results'] = results  # Keep original for re-transposing
                
            except Exception as e:
                st.error(f"❌ Error generating recommendations: {e}")
                st.exception(e)

# Display results (from current generation OR from session state on rerun)
if 'results' in st.session_state:
    results = st.session_state['results']
    
    try:
        # Display enhanced lyrics analysis if available
        if results['lyrics_analysis']:
            analysis = results['lyrics_analysis']
            
            # Check if it's a snippet or partial
            is_partial = analysis.get('is_partial', False)
            snippet_type = analysis.get('snippet_type', 'full_song')
            
            if is_partial:
                if snippet_type == 'single_line':
                    st.success("✓ Lyrics analyzed (single line - basic analysis)")
                    st.info("💡 Tip: For comprehensive emotional arc and section-specific recommendations, provide multiple verses.")
                elif snippet_type == 'snippet':
                    st.success("✓ Lyrics analyzed (snippet - partial analysis)")
                    st.info("💡 Tip: Section labels and emotional arc are inferred from the snippet. More complete results with full song.")
                elif snippet_type == 'partial_song':
                    st.success("✓ Lyrics analyzed (partial song - inferred structure)")
                    st.info("💡 Tip: Section labels (verse/chorus/bridge) are inferred from partial lyrics. For most accurate structure, provide the complete song.")
            else:
                st.success("✓ Lyrics analyzed with emotional arc tracking")
            
            with st.expander("📝 View Comprehensive Lyrics Analysis", expanded=False):
                # Overall Analysis
                st.markdown("### 🎭 Overall Analysis")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Mood:** {analysis.get('overall_mood', 'N/A')}")
                    st.markdown(f"**Energy:** {analysis.get('overall_energy', 'N/A')}")
                with col2:
                    st.markdown(f"**Genre:** {analysis.get('overall_genre', 'N/A')}")
                    st.markdown(f"**Themes:** {', '.join(analysis.get('overall_themes', []))}")
                with col3:
                    st.markdown(f"**Emotional Arc:**")
                    st.markdown(f"*{analysis.get('emotional_arc', 'N/A')}*")
                
                st.markdown("---")
                
                # Song Structure
                song_structure = analysis.get('song_structure', [])
                if song_structure:
                    st.markdown("### 📖 Song Structure")
                    for section in song_structure:
                        with st.container():
                            st.markdown(f"**{section.get('section', 'Unknown').upper()}** "
                                      f"(Intensity: {section.get('emotional_intensity', 'N/A')}/10)")
                            st.caption(f"Mood: {section.get('section_mood', 'N/A')}")
                            st.caption(f"Harmonic needs: {section.get('harmonic_needs', 'N/A')}")
                            st.markdown("")
                
                st.markdown("---")
                
                # Emotional Peaks
                peaks = analysis.get('emotional_peaks', [])
                if peaks:
                    st.markdown("### ⭐ Emotional Peaks")
                    for i, peak in enumerate(peaks, 1):
                        st.markdown(f"**Peak {i}** [{peak.get('section', 'N/A')}] "
                                  f"- Intensity: {peak.get('intensity', 'N/A')}/10")
                        st.caption(f"\"{peak.get('line_text', 'N/A')}\"")
                        st.info(f"💡 {peak.get('harmonic_suggestion', 'N/A')}")
                        st.markdown("")
                
                st.markdown("---")
                
                # Section-Specific Recommendations
                section_recs = analysis.get('section_specific_recommendations', {})
                if section_recs:
                    st.markdown("### 🎸 Section-Specific Chord Recommendations")
                    for section, rec in section_recs.items():
                        if rec:
                            st.markdown(f"**{section.capitalize()}:**")
                            st.markdown(f"- {rec}")
                            st.markdown("")
        
        # Display multiple progression options with match scores
        st.markdown("---")
        st.markdown("## 🎵 Your Chord Progression Options")
        
        # Key adjuster (outside form for real-time updates)
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            current_key = st.selectbox(
                "🎹 Adjust Key",
                options=["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"],
                index=["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"].index(st.session_state.get('selected_key', 'C')),
                help="Change the key and all progressions will update automatically",
                key="key_adjuster"
            )
        
        with col2:
            if st.session_state.get('selected_key') != current_key:
                st.info(f"🎼 Transposed from {st.session_state.get('selected_key', 'C')} to {current_key}")
        
        with col3:
            if st.button("♻️ Reset to Original", help="Reset to originally selected key"):
                current_key = preferred_key
                st.rerun()
        
        # Re-transpose if key changed
        if current_key != st.session_state.get('selected_key', 'C'):
            transposer = ChordTransposer(rag_system=orchestrator.rag)
            transposed_progressions = []
            
            for item in st.session_state.get('original_results', results)['progressions']:
                if isinstance(item, dict) and 'progression' in item:
                    prog = item['progression']
                    match_score = item.get('match_score', 75)
                else:
                    prog = item
                    match_score = 75
                
                # Get original metadata
                original_metadata = prog.metadata if hasattr(prog, 'metadata') else prog
                original_chords = original_metadata.get('original_chords', original_metadata.get('chords_example', ''))
                
                # Transpose from original C to new key
                transposed_data = transposer.transpose_progression_smart(
                    {'chords_example': original_chords, **original_metadata},
                    current_key,
                    use_theory=False
                )
                
                # Update metadata
                if hasattr(prog, 'metadata'):
                    prog.metadata.update(transposed_data)
                
                transposed_progressions.append({
                    'progression': prog,
                    'match_score': match_score
                })
            
            results['progressions'] = transposed_progressions
            st.session_state['selected_key'] = current_key
        
        # Get top progressions
        raw_progressions = results['progressions'][:6]  # Show top 6
        
        # Handle both old format (Document objects) and new format (scored dicts)
        top_progressions = []
        for item in raw_progressions:
            if isinstance(item, dict) and 'progression' in item and 'match_score' in item:
                # New format with scoring
                top_progressions.append(item)
            else:
                # Old format - raw Document, add default score
                top_progressions.append({
                    'progression': item,
                    'match_score': 75
                })
        
        if top_progressions:
            # Create tabs for each progression (hide percentage if < 75%)
            tab_labels = []
            for i, prog in enumerate(top_progressions):
                score = prog['match_score']
                if score >= 75:
                    tab_labels.append(f"Option {i+1} ({score}% match)")
                else:
                    tab_labels.append(f"Option {i+1}")
            tabs = st.tabs(tab_labels)
            
            for i, (tab, scored_prog) in enumerate(zip(tabs, top_progressions)):
                with tab:
                    prog = scored_prog['progression']
                    score = scored_prog['match_score']
                    
                    # Create unique key for this progression (used for caching and widgets)
                    prog_key = f"{prog.metadata['progression_roman']}_{i}"
                    
                    # Match score indicator
                    if score >= 85:
                        match_emoji = "🎯"
                        match_label = "Excellent Match"
                        match_color = "green"
                    elif score >= 75:
                        match_emoji = "✨"
                        match_label = "Great Match"
                        match_color = "blue"
                    else:
                        match_emoji = "👍"
                        match_label = "Good Option"
                        match_color = "gray"
                    
                    # Show progression name prominently
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
                    
                    # Progression details
                    st.markdown(f"**Chords in {current_key}:** `{prog.metadata['chords_example']}`")
                    
                    # Show original chords if transposed
                    if prog.metadata.get('transposed_to') and prog.metadata.get('original_chords'):
                        original_key = prog.metadata.get('transposed_from', 'C')
                        if original_key != current_key:
                            st.caption(f"Original ({original_key}): {prog.metadata['original_chords']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Mood:** {prog.metadata['mood']}")
                        st.markdown(f"**Genres:** {prog.metadata['genres']}")
                    with col2:
                        st.markdown(f"**Popularity:** {prog.metadata.get('frequency', 'Common')}")
                    
                    # Famous examples
                    st.markdown("**🎸 Famous Songs Using This:**")
                    st.caption(prog.metadata.get('example_songs', 'N/A'))
                    
                    # Why it matches (if lyrics analyzed)
                    if results.get('lyrics_analysis'):
                        st.markdown("**💡 Why This Matches Your Song:**")
                        analysis = results['lyrics_analysis']
                        
                        prog_mood = prog.metadata.get('mood', '').lower()
                        lyric_mood = analysis.get('overall_mood', '').lower()
                        
                        match_reasons = []
                        if lyric_mood in prog_mood or prog_mood in lyric_mood:
                            match_reasons.append(f"✓ Matches your {lyric_mood} mood")
                        
                        lyric_genre = analysis.get('overall_genre', '').lower()
                        prog_genres = prog.metadata.get('genres', '').lower()
                        if lyric_genre in prog_genres:
                            match_reasons.append(f"✓ Perfect for {lyric_genre} genre")
                        
                        emotional_arc = analysis.get('emotional_arc', '')
                        if emotional_arc:
                            match_reasons.append(f"✓ Supports your emotional journey")
                        
                        if match_reasons:
                            for reason in match_reasons:
                                st.markdown(reason)
                        else:
                            st.markdown("✓ Well-suited for your song's characteristics")
                    
                    # Interactive Chord Player
                    st.markdown("---")
                    st.markdown("### 🎹 Listen to This Progression")
                    
                    # Player controls
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.caption("🎵 Click play to hear • Select chords for custom playback • Loop continuously")
                    with col2:
                        instrument = st.selectbox(
                            "Instrument",
                            ["piano", "guitar", "synth", "pad"],
                            index=0,
                            key=f"instrument_{prog_key}",
                            help="Choose the sound/instrument"
                        )
                    with col3:
                        tempo = st.slider(
                            "Tempo (BPM)", 
                            60, 180, 100, 
                            key=f"tempo_{prog_key}",
                            help="Adjust the playback speed"
                        )
                    
                    # Play the progression in the current key
                    play_chord_progression(
                        progression_roman=prog.metadata['progression_roman'],
                        chords_example=prog.metadata['chords_example'],
                        tempo=tempo,
                        instrument=instrument,
                        loop=False,  # User can toggle in the player
                        widget_key=prog_key
                    )
                    
                    # Progression-specific theory and recommendations
                    st.markdown("---")
                    st.markdown("### 🎓 Music Theory for This Progression")
                    
                    # Cache in session state to avoid regenerating when switching tabs
                    if f'theory_{prog_key}' not in st.session_state:
                        with st.spinner("Analyzing this progression..."):
                            try:
                                # Build query for this specific progression
                                theory_query = f"{prog.metadata['progression_roman']} {prog.metadata['chords_example']} chord progression"
                                if results.get('lyrics_analysis'):
                                    theory_query += f" {analysis.get('overall_mood', '')} {analysis.get('overall_genre', '')}"
                                
                                # Get theory context from RAG
                                theory_docs = orchestrator.rag.get_theory_context(theory_query, k=2)
                                
                                # Generate progression-specific analysis
                                prog_context = f"""Analyze this specific chord progression for the user's song:

Progression: {prog.metadata['progression_roman']} ({prog.metadata['chords_example']})
Mood: {prog.metadata['mood']}
Genres: {prog.metadata['genres']}"""
                                
                                if results.get('lyrics_analysis'):
                                    prog_context += f"""

User's Song:
- Mood: {analysis.get('overall_mood', 'N/A')}
- Genre: {analysis.get('overall_genre', 'N/A')}
- Emotional Arc: {analysis.get('emotional_arc', 'N/A')}"""
                                
                                if theory_docs:
                                    prog_context += f"\n\nMusic Theory Context:\n"
                                    for doc in theory_docs:
                                        prog_context += f"{doc.page_content[:400]}\n"
                                
                                prog_prompt = f"""{prog_context}

Provide a focused, practical explanation (3-4 paragraphs):

1. **How This Progression Works**: Explain the harmonic movement and why these chords work together
2. **Why It Fits Your Song**: Connect it specifically to the user's mood/genre/emotional arc
3. **Tips for Using It**: Practical advice for implementation (strumming patterns, variations, sections to use it in)
4. **Emotional Impact**: How this progression creates the desired emotional effect

Be conversational, educational, and actionable. Focus specifically on THIS progression."""
                                
                                from langchain_openai import ChatOpenAI
                                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
                                response = llm.invoke(prog_prompt)
                                
                                # Cache the response
                                st.session_state[f'theory_{prog_key}'] = response.content
                                
                            except Exception as e:
                                st.session_state[f'theory_{prog_key}'] = f"*This progression works well for your song based on the mood and genre match.* (Error: {e})"
                    
                    # Display cached or newly generated theory
                    st.markdown(st.session_state[f'theory_{prog_key}'])
            
            # Generate cohesive comparative analysis for the displayed options
            st.markdown("---")
            st.markdown("## 🎼 How to Choose & Use These Progressions")
            
            # Check if we need to generate comparative analysis
            comp_key = "comparative_analysis"
            if comp_key not in st.session_state:
                with st.spinner("Generating comparative analysis..."):
                    try:
                        # Build context with the actual progressions shown
                        comp_context = "You are analyzing chord progressions for a user's song. Here are the top options:\n\n"
                        
                        for idx, scored_prog in enumerate(top_progressions, 1):
                            prog = scored_prog['progression']
                            score = scored_prog['match_score']
                            # Only show percentage if >= 75%
                            if score >= 75:
                                comp_context += f"**Option {idx}** ({score}% match):\n"
                            else:
                                comp_context += f"**Option {idx}**:\n"
                            comp_context += f"- Progression: {prog.metadata['progression_roman']} ({prog.metadata['chords_example']})\n"
                            comp_context += f"- Mood: {prog.metadata['mood']}\n"
                            comp_context += f"- Genres: {prog.metadata['genres']}\n"
                            comp_context += f"- Examples: {prog.metadata.get('example_songs', 'N/A')[:100]}\n\n"
                        
                        if results.get('lyrics_analysis'):
                            analysis = results['lyrics_analysis']
                            comp_context += f"\nUser's Song Analysis:\n"
                            comp_context += f"- Mood: {analysis.get('overall_mood', 'N/A')}\n"
                            comp_context += f"- Energy: {analysis.get('overall_energy', 'N/A')}\n"
                            comp_context += f"- Genre: {analysis.get('overall_genre', 'N/A')}\n"
                            comp_context += f"- Emotional Arc: {analysis.get('emotional_arc', 'N/A')}\n"
                        
                        comp_prompt = f"""{comp_context}

Provide a cohesive comparative analysis that helps the user choose between these {len(top_progressions)} options:

1. **Quick Recommendation**: Which option should they start with and why? (Reference by Option number)
2. **Comparing the Top 3**: Briefly compare Options 1, 2, and 3 - what makes each unique?
3. **When to Use Each**: Practical guidance on which progression works best for different sections (verse/chorus/bridge)
4. **Mixing Progressions**: Can they combine different options? Which ones complement each other?

IMPORTANT: 
- Reference progressions by their Option numbers (Option 1, Option 2, etc.) 
- Use the actual progression names shown above (e.g., "Option 1's vi-IV-I-V")
- If match percentages are shown, you can reference them, but don't invent percentages
- Keep it practical and actionable

Format with clear headers and bullet points. Be conversational."""
                        
                        from langchain_openai import ChatOpenAI
                        llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
                        response = llm.invoke(comp_prompt)
                        
                        st.session_state[comp_key] = response.content
                    except Exception as e:
                        st.session_state[comp_key] = f"Error generating analysis: {e}"
            
            with st.expander("📊 Detailed Comparison & Usage Guide", expanded=True):
                st.info("💡 **This section compares all the options above and helps you decide which to use for different parts of your song.**")
                st.markdown(st.session_state[comp_key])
            
            # Enhanced Current Trends - Show structured web insights
            web_details = results.get('web_search_details', {})
            has_web_results = any(web_details.get(k) for k in ['trends', 'production', 'theory', 'similar_songs'])
            
            if has_web_results or results.get('current_examples'):
                with st.expander("🌐 Additional Research & Context (Web Sources)", expanded=False):
                    st.caption("Current trends, production techniques, and examples from music journalism and songwriting resources")
                    
                    # Genre Trends
                    if web_details.get('trends'):
                        st.markdown("### 📈 What's Trending in Your Genre")
                        st.info("💡 **Use this to:** Stay current with what's popular in your genre right now")
                        for i, result in enumerate(web_details['trends'][:3], 1):
                            with st.container():
                                st.markdown(f"**{i}. {result.get('title', 'N/A')}**")
                                st.caption(f"→ Helps you understand current production trends and popular progressions")
                                st.markdown(result.get('content', 'No description')[:250] + "...")
                                st.markdown(f"🔗 [Read full article]({result.get('url', '#')})")
                                st.markdown("")
                    
                    # Production Techniques
                    if web_details.get('production'):
                        st.markdown("### 🎚️ How to Play & Produce These Chords")
                        st.info("💡 **Use this to:** Learn specific techniques for voicing, arranging, and recording")
                        for i, result in enumerate(web_details['production'][:2], 1):
                            with st.container():
                                st.markdown(f"**{i}. {result.get('title', 'N/A')}**")
                                st.caption(f"→ Practical tips on instrumentation, voicing, and production techniques")
                                st.markdown(result.get('content', 'No description')[:250] + "...")
                                st.markdown(f"🔗 [Read full article]({result.get('url', '#')})")
                                st.markdown("")
                    
                    # Theory / Mood-based
                    if web_details.get('theory'):
                        st.markdown("### 🎓 Understanding the Theory")
                        st.info("💡 **Use this to:** Understand WHY these progressions create the emotional effect you want")
                        for i, result in enumerate(web_details['theory'][:2], 1):
                            with st.container():
                                st.markdown(f"**{i}. {result.get('title', 'N/A')}**")
                                st.caption(f"→ Music theory explaining mood-based chord choices")
                                st.markdown(result.get('content', 'No description')[:200] + "...")
                                st.markdown(f"🔗 [Read more]({result.get('url', '#')})")
                                st.markdown("")
                    
                    # Similar Songs / Examples
                    if web_details.get('similar_songs'):
                        st.markdown("### 🎵 Learn from Similar Songs")
                        st.info("💡 **Use this to:** Study real examples with similar emotional characteristics")
                        for i, result in enumerate(web_details['similar_songs'][:3], 1):
                            with st.container():
                                st.markdown(f"**{i}. {result.get('title', 'N/A')}**")
                                st.caption(f"→ Songs with similar mood/emotional arc you can learn from")
                                st.markdown(result.get('content', 'No description')[:200] + "...")
                                st.markdown(f"🔗 [Read more]({result.get('url', '#')})")
                                st.markdown("")
                    
                    # Fallback to old format if structured not available
                    if not has_web_results and results.get('current_examples'):
                        st.markdown("### 🔍 Web Search Results")
                        for ex in results['current_examples']:
                            st.markdown(f"**{ex.get('title', 'N/A')}**")
                            st.caption(ex.get('content', '')[:200] + "...")
                            st.markdown(f"[Read more]({ex.get('url', '#')})")
                            st.markdown("")
                    
                    if not has_web_results and not results.get('current_examples'):
                        st.info("💡 Tip: Add reference artists or a song description for more comprehensive web research!")
        
        # Success message
        st.success("✨ Click through the tabs above to explore different chord progression options!")
        
    except Exception as e:
        st.error(f"❌ Error displaying results: {e}")
        st.exception(e)

# Footer
st.markdown("---")
st.markdown("### 💡 Tips for Best Results")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**📝 Include Lyrics**")
    st.caption("Lyrics help us understand your song's emotional core")
with col2:
    st.markdown("**🎨 Be Specific**")
    st.caption("'Dark moody indie' works better than just 'indie'")
with col3:
    st.markdown("**🎸 Try Variations**")
    st.caption("Experiment with different artists and moods")
