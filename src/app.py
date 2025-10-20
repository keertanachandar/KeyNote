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
    
    # Load PDFs
    docs = load_music_theory_pdfs("data/pdfs")
    chunks = chunk_documents(docs) if docs else []
    
    # Initialize RAG
    rag = ChordProgressionRAG(
        chunks, 
        "data/theorytab/progressions.csv"
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
    with st.spinner("Initializing KeyNote... (this may take 30 seconds on first load)"):
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
                
                # Display lyrics analysis if available
                if results['lyrics_analysis']:
                    st.success("✓ Lyrics analyzed successfully")
                    with st.expander("📝 View Lyrics Analysis", expanded=False):
                        analysis = results['lyrics_analysis']
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Mood:** {analysis['mood']}")
                            st.markdown(f"**Energy:** {analysis['energy']}")
                            st.markdown(f"**Genre:** {analysis['suggested_genre']}")
                        with col2:
                            st.markdown(f"**Themes:** {', '.join(analysis['themes'])}")
                            st.markdown(f"**Style:** {', '.join(analysis['style_indicators'])}")
                
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