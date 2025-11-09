import streamlit as st
from utils.pdf_loader import load_music_theory_pdfs, chunk_documents
from utils.rag_system import ChordProgressionRAG
from agents.langgraph_orchestrator import LangGraphOrchestrator
import os

# Page config
st.set_page_config(
    page_title="KeyNote", 
    page_icon="🎸",
    layout="wide"
)

# Initialize system (cached so it only runs once)
@st.cache_resource
def initialize_system():
    """Initialize RAG system and orchestrator"""
    print("\n" + "="*60)
    print("INITIALIZING KEYNOTE")
    print("="*60)
    
    # Load PDFs with caching and vision
    # First load: ~2-5 min (vision API), subsequent loads: <5 sec (cached)
    docs = load_music_theory_pdfs("data/pdfs", use_cache=True, use_vision=True)

    chunks = chunk_documents(docs) if docs else []
    
    # Initialize RAG with persistent storage
    rag = ChordProgressionRAG(
        chunks, 
        "data/theorytab/progressions.csv",
        use_persistent_storage=True  # Save Qdrant to disk for instant reloads
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        user_input = st.text_input(
            "Song Description *",
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
        "Your Lyrics (Optional but Recommended)",
        placeholder="Walking through the empty streets at dawn\nEverything reminds me that you're gone\nThe coffee shop where we used to meet\nNow just echoes of memory",
        height=150,
        help="Paste a verse or chorus - we'll analyze the emotional tone and themes to personalize recommendations"
    )
    
    submit = st.form_submit_button("🎵 Generate Chord Progressions", use_container_width=True, type="primary")

# Process
if submit:
    if not user_input:
        st.error("⚠️  Please describe your song!")
    else:
        with st.spinner("🎵 Analyzing your song and generating recommendations..."):
            try:
                # Run orchestrator
                results = orchestrator.generate_recommendations(
                    user_input, 
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
                
                # Display main recommendations
                st.markdown("---")
                st.markdown("## 🎵 Your Personalized Chord Progressions")
                st.markdown(results['synthesis'])
                
                # Show data sources in expandable section
                with st.expander("📚 View Data Sources Used", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Historical Progressions")
                        for prog in results['progressions']:
                            st.markdown(f"**{prog.metadata['progression_roman']}** ({prog.metadata['chords_example']})")
                            st.markdown(f"*{prog.metadata['mood']}* | {prog.metadata['genres']}")
                            st.caption(f"Examples: {prog.metadata.get('example_songs', 'N/A')[:100]}...")
                            st.markdown("")
                    
                    with col2:
                        st.markdown("### Current Trends (Web Search)")
                        if results['current_examples']:
                            for ex in results['current_examples']:
                                st.markdown(f"**{ex['title']}**")
                                st.caption(ex['content'][:150] + "...")
                                st.markdown(f"[Read more]({ex['url']})")
                                st.markdown("")
                        else:
                            st.info("No current trends found")
                
                # Success message
                st.success("✨ Recommendations generated! Use these chord progressions as inspiration for your songwriting.")
                        
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