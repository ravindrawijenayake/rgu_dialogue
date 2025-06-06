import streamlit as st
from classify import classify_utterances
from summarise import generate_summary
from main import generate_mermaid_diagram
import pandas as pd

# --- Session State Initialization ---
st.session_state.setdefault('transcript', '')
st.session_state.setdefault('utterances', None)
st.session_state.setdefault('summary', None)
st.session_state.setdefault('mermaid', None)

# --- Sidebar ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=60)
st.sidebar.title("Dialogue Analysis Platform")
st.sidebar.markdown("""
**Instructions:**
1. Paste or upload a dialogue transcript below.
2. Click **Analyse** to process.
3. View results below.
""")
st.sidebar.markdown('<hr>', unsafe_allow_html=True)
st.sidebar.markdown('<div style="color:#888;font-size:0.97rem;">Made with <span style="color:#1976d2;">Streamlit</span> &middot; <a href="https://github.com/ravindrawijenayake" style="color:#1976d2;">GitHub</a></div>', unsafe_allow_html=True)

# --- Main Layout ---
st.markdown("""
    <style>
        .main-card {max-width: 800px; margin: 0 auto 40px auto; background: #fff; border-radius: 16px; box-shadow: 0 6px 32px rgba(44,62,80,0.10); padding: 32px 32px 32px 32px;}
        .chip {display:inline-block;padding:2px 10px;border-radius:12px;font-size:0.95em;margin-right:4px;}
        .chip-func {background:#e3f2fd;color:#1976d2;}
        .chip-high {background:#e8f5e9;color:#388e3c;}
        .chip-medium {background:#fffde7;color:#fbc02d;}
        .chip-low {background:#ffebee;color:#d32f2f;}
        .section-title {color:#1976d2;margin-top:32px;}
        .summary {background: #e3f2fd; padding: 18px 16px; border-radius: 10px; margin-top: 18px;}
    </style>
""", unsafe_allow_html=True)
st.markdown('<div class="main-card">', unsafe_allow_html=True)

st.markdown('<h1 style="color:#1976d2;margin-bottom:0;">Dialogue Analysis Platform</h1>', unsafe_allow_html=True)
st.caption("Paste, upload, or use a sample transcript. Then click Analyse.")

# --- Input Section ---
col1, col2, col3 = st.columns([3,2,2])
with col1:
    transcript = st.text_area(
        "Transcript",
        value=st.session_state['transcript'],
        height=180,
        key="transcript_input",
        placeholder="E.g. Alice: Hello! How are you?\nBob: I'm good, thanks! And you?",
        help="Each line should start with the speaker's name, followed by a colon."
    )
with col2:
    uploaded_file = st.file_uploader(
        "Upload .txt",
        type=["txt"],
        help="Upload a plain text file with the dialogue transcript."
    )
with col3:
    if st.button("Insert Sample"):
        transcript = "Alice: Hello! How are you?\nBob: I'm good, thanks! And you?\nAlice: Doing well!"
        st.session_state['transcript'] = transcript
        st.experimental_rerun()

# --- Handle File Upload ---
if uploaded_file:
    transcript = uploaded_file.read().decode("utf-8")
    st.session_state['transcript'] = transcript
    st.experimental_rerun()

# --- Update session state from text area ---
st.session_state['transcript'] = transcript

# --- Analyse Button ---
if st.button("\U0001F50D Analyse", help="Analyse the transcript and generate results."):
    if not transcript.strip():
        st.error("Please provide a transcript to analyse.")
        st.session_state['utterances'] = None
        st.session_state['summary'] = None
        st.session_state['mermaid'] = None
    else:
        with st.spinner("Analysing dialogue, please wait..."):
            utterances = classify_utterances(transcript)
            summary = generate_summary(transcript)
            mermaid_diagram = generate_mermaid_diagram(utterances)
        st.session_state['utterances'] = utterances
        st.session_state['summary'] = summary
        st.session_state['mermaid'] = mermaid_diagram
        st.success("Analysis complete! See results below.")

# --- Results Section ---
if st.session_state.get('utterances'):
    st.markdown('<h2 class="section-title">Utterances Table</h2>', unsafe_allow_html=True)
    def chip(val, kind):
        return f'<span class="chip chip-{kind}">{val}</span>'
    df = pd.DataFrame([
        {
            "Speaker": u['speaker'],
            "Utterance": u['utterance'],
            "Function": chip(u['function'], 'func'),
            "Confidence": chip(u['confidence'], u['confidence'].split()[0].lower()) if u.get('confidence') else '-',
        } for u in st.session_state['utterances']
    ])
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.download_button("Download CSV", df.to_csv(index=False), "utterances.csv")

    st.markdown('<h2 class="section-title">Structured Summary</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary">{st.session_state["summary"]}</div>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">Dialogue Flow Diagram</h2>', unsafe_allow_html=True)
    try:
        import streamlit_mermaid as st_mermaid
        st_mermaid.st_mermaid(st.session_state['mermaid'])
    except ImportError:
        st.code(st.session_state['mermaid'], language="mermaid")

st.markdown('</div>', unsafe_allow_html=True)
