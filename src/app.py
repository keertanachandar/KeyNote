import streamlit as st
from utils.pdf_loader import load_music_theory_pdfs, chunk_documents
from utils.rag_system import ChordProgressionRAG
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
    rag = ChordProgressionRAG(
        chunks, 
        "data/theorytab/progressions.csv",
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
    
    submit = st.form_submit_button("🎵 Generate Chord Progressions", use_container_width=True, type="primary")

# Process
if submit:
    if not user_input and not lyrics:
        st.error("⚠️  Please provide either a song description OR lyrics (or both for best results)!")
    else:
        with st.spinner("🎵 Analyzing your song and generating recommendations..."):
            try:
                # If no description but lyrics provided, use lyrics as primary input
                if not user_input and lyrics:
                    query = f"Song based on these lyrics: {lyrics[:200]}..."  # Use first 200 chars as query
                else:
                    query = user_input
                
                # Run orchestrator
                results = orchestrator.generate_recommendations(
                    query, 
                    lyrics if lyrics else None,
                    reference_artists if reference_artists else None
                )
                
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
                    # Create tabs for each progression
                    tab_labels = [f"Option {i+1} ({prog['match_score']}% match)" 
                                  for i, prog in enumerate(top_progressions)]
                    tabs = st.tabs(tab_labels)
                    
                    for i, (tab, scored_prog) in enumerate(zip(tabs, top_progressions)):
                        with tab:
                            prog = scored_prog['progression']
                            score = scored_prog['match_score']
                            
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
                                match_label = "Good Match"
                                match_color = "gray"
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"### {match_emoji} {prog.metadata['progression_roman']}")
                            with col2:
                                st.markdown(f"**{score}%**")
                                st.caption(match_label)
                            
                            # Progression details
                            st.markdown(f"**Chords:** `{prog.metadata['chords_example']}`")
                            
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
                            
                            # Progression-specific theory and recommendations
                            st.markdown("---")
                            st.markdown("### 🎓 Music Theory for This Progression")
                            
                            # Create unique key for this progression to cache analysis
                            prog_key = f"{prog.metadata['progression_roman']}_{i}"
                            
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
                    st.markdown("## 🎼 Comparative Analysis & Recommendations")
                    
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
                                    comp_context += f"**Option {idx}** ({score}% match):\n"
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

1. **Quick Recommendation**: Which option should they start with and why? (Reference by Option number and match %)
2. **Comparing the Top 3**: Briefly compare Options 1, 2, and 3 - what makes each unique?
3. **When to Use Each**: Practical guidance on which progression works best for different sections (verse/chorus/bridge)
4. **Mixing Progressions**: Can they combine different options? Which ones complement each other?

IMPORTANT: 
- Reference progressions by their Option numbers (Option 1, Option 2, etc.) 
- Use the actual progression names shown above (e.g., "Option 1's vi-IV-I-V")
- Be specific about the match percentages
- Keep it practical and actionable

Format with clear headers and bullet points. Be conversational."""
                                
                                from langchain_openai import ChatOpenAI
                                llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
                                response = llm.invoke(comp_prompt)
                                
                                st.session_state[comp_key] = response.content
                            except Exception as e:
                                st.session_state[comp_key] = f"Error generating analysis: {e}"
                    
                    with st.expander("📊 Compare All Options & Get Overall Recommendations", expanded=False):
                        st.info("💡 **Tip:** This compares the options shown in the tabs above and helps you choose.")
                        st.markdown(st.session_state[comp_key])
                    
                    # Current trends
                    if results.get('current_examples'):
                        with st.expander("🔍 Current Trends (Web Search)", expanded=False):
                            for ex in results['current_examples']:
                                st.markdown(f"**{ex['title']}**")
                                st.caption(ex['content'][:200] + "...")
                                st.markdown(f"[Read more]({ex['url']})")
                                st.markdown("")
                
                # Success message
                st.success("✨ Click through the tabs above to explore different chord progression options!")
                        
            except Exception as e:
                st.error(f"❌ Error generating recommendations: {e}")
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