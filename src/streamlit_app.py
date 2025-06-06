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

# --- Custom CSS for clean look ---
st.markdown("""
    <style>
        html, body, .stApp {background: #f6fafc !important;}
        .stTextArea textarea {background: #f8fbfd; font-size: 1.1rem; border-radius: 8px;}
        .stFileUploader {margin-bottom: 10px;}
        .stButton>button {background: #29597a; color: #fff; border-radius: 6px; border: none; padding: 10px 32px; font-size: 1.1rem; font-weight: 600; margin-right: 12px;}
        .stButton>button:hover {background: #1d3c53;}
        .stMarkdown h1 {color: #29597a; font-size: 2.6rem; margin-bottom: 0.2em;}
        .stMarkdown h2 {color: #29597a; margin-top: 2.2em;}
        .stMarkdown h3 {color: #4b6584;}
        .stMarkdown pre {background: #eaf4fb; border-radius: 6px;}
        .summary {background: #e3f2fd; padding: 18px 16px; border-radius: 10px; margin-top: 18px;}
        .chip {display:inline-block;padding:2px 10px;border-radius:12px;font-size:0.95em;margin-right:4px;}
        .chip-func {background:#e3f2fd;color:#1976d2;}
        .chip-high {background:#e8f5e9;color:#388e3c;}
        .chip-medium {background:#fffde7;color:#fbc02d;}
        .chip-low {background:#ffebee;color:#d32f2f;}
        .footer {text-align:center;color:#888;font-size:0.97rem;margin-top:32px;}
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<h1>Dialogue Analysis Platform</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center; color:#29597a; margin-top:0;">Created by Ravindra Wijenayake</h3>', unsafe_allow_html=True)

# --- Input Section ---
st.markdown('<b>Paste transcript or upload file:</b>', unsafe_allow_html=True)
transcript = st.text_area(
    "Paste your dialogue transcript here...",
    value=st.session_state['transcript'],
    height=180,
    key="transcript_input",
    placeholder="Paste your dialogue transcript here...",
    help="Each line should start with the speaker's name, followed by a colon."
)
uploaded_file = st.file_uploader(
    "",
    type=["txt"],
    help="Upload a plain text file with the dialogue transcript."
)

colA, colB = st.columns([1,1])
with colA:
    analyse_clicked = st.button("Analyse")
with colB:
    clear_clicked = st.button("Clear")

# --- Handle Clear Button ---
if clear_clicked:
    st.session_state['transcript'] = ''
    st.session_state['utterances'] = None
    st.session_state['summary'] = None
    st.session_state['mermaid'] = None
    st.experimental_set_query_params()  # Soft reset
    st.experimental_rerun()

# --- Handle File Upload ---
if uploaded_file is not None:
    transcript = uploaded_file.read().decode("utf-8")
    st.session_state['transcript'] = transcript
    st.session_state['utterances'] = None
    st.session_state['summary'] = None
    st.session_state['mermaid'] = None
    # No rerun needed, just update state

# --- Update session state from text area ---
st.session_state['transcript'] = transcript

# --- Handle Analyse Button ---
if analyse_clicked:
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
    st.markdown('<h2>Utterances Table</h2>', unsafe_allow_html=True)
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

    st.markdown('<h2>Structured Summary</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary">{st.session_state["summary"]}</div>', unsafe_allow_html=True)

    st.markdown('<h2>Dialogue Flow Diagram</h2>', unsafe_allow_html=True)
    try:
        import streamlit_mermaid as st_mermaid
        st_mermaid.st_mermaid(st.session_state['mermaid'])
    except ImportError:
        st.code(st.session_state['mermaid'], language="mermaid")

# --- Footer ---
st.markdown('<div class="footer">Made with <span style="color:#1976d2;">Streamlit</span> &middot; <a href="https://github.com/ravindrawijenayake" style="color:#1976d2;">GitHub</a></div>', unsafe_allow_html=True)
