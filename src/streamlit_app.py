import streamlit as st
from classify import classify_utterances
from summarise import generate_summary

# --- Mermaid Diagram Renderer ---
def render_mermaid(mermaid_code):
    try:
        from streamlit_mermaid import st_mermaid
        st_mermaid(mermaid_code)
    except ImportError:
        st.info("Install streamlit-mermaid or paste this in a Mermaid live editor.")
        st.code(mermaid_code, language="mermaid")

def generate_mermaid_diagram(utterances):
    nodes = []
    edges = []
    for i, u in enumerate(utterances):
        node_id = f"U{i}"
        label = f"{u['speaker']}: {u['function']}"
        nodes.append(f"{node_id}[{label}]")
        if i > 0:
            edges.append(f"U{i-1} --> U{i}")
    return "graph TD\n" + "\n".join(nodes + edges)

# --- Page Config ---
st.set_page_config(page_title="Dialogue Classifier & Summariser", layout="wide")

# --- Custom CSS ---
st.markdown('''
    <style>
    body, .stApp {
        background: #f4f4f9;
        font-family: 'Segoe UI', sans-serif;
    }
    .main-title {
        color: #1f3b4d;
        font-size: 36px;
        font-weight: bold;
        padding-bottom: 0.5rem;
    }
    .section {
        background-color: #ffffff;
        border: 1px solid #d4d4d4;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .stTextArea textarea, .stFileUploader, .stDataFrame, .stAlert {
        border-radius: 10px;
        background-color: #fefefe;
    }
    .stButton>button {
        background-color: #1f3b4d;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.5em 1em;
    }
    .stButton>button:hover {
        background-color: #406882;
        color: #ffffff;
    }
    .summary-box {
        background-color: #f1f7ff;
        border: 1px solid #aaccee;
        border-radius: 10px;
        padding: 16px;
        font-size: 1.05em;
        color: #1f3b4d;
    }
    </style>
''', unsafe_allow_html=True)

# --- Initial Session State ---
default_keys = ['transcript', 'uploaded_file', 'utterances', 'summary', 'mermaid_diagram', 'transcript_input']
for key in default_keys:
    if key not in st.session_state:
        st.session_state[key] = '' if key != 'utterances' and key != 'uploaded_file' else None

# --- Title ---
st.markdown('<div class="main-title">🗣️ Dialogue Classifier & Summariser</div>', unsafe_allow_html=True)
st.markdown("Use this tool to upload or paste dialogue transcripts. The tool will classify utterances, generate a summary, and visualise the dialogue flow.")

# --- Input Section ---
with st.container():
    st.markdown("### 📝 Input Section")
    st.markdown('<div class="section">', unsafe_allow_html=True)

    with st.form("transcript_form", clear_on_submit=False):
        uploaded_file = st.file_uploader("Upload transcript file (UTF-8 text)", type=["txt"])
        transcript_input = st.text_area("Or paste transcript here", value=st.session_state.get('transcript_input', ''), height=200, key="transcript_input")
        submitted = st.form_submit_button("🔍 Process Transcript", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- Clear All Button ---
col1, col2 = st.columns([0.85, 0.15])
with col2:
    if st.button("🗑️ Clear All", use_container_width=True, help="Reset all inputs and outputs"):
        for key in default_keys:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- Processing Transcript ---
if submitted:
    transcript = ''
    if uploaded_file is not None:
        transcript = uploaded_file.read().decode("utf-8")
    elif transcript_input.strip():
        transcript = transcript_input.strip()

    if not transcript:
        st.warning("⚠️ Please upload a file or paste transcript text.")
    else:
        st.session_state['transcript'] = transcript
        st.session_state['utterances'] = classify_utterances(transcript)
        st.session_state['summary'] = generate_summary(transcript)
        st.session_state['mermaid_diagram'] = generate_mermaid_diagram(st.session_state['utterances'])

# --- Output Display ---
transcript = st.session_state.get('transcript', '')
utterances = st.session_state.get('utterances', None)
summary = st.session_state.get('summary', '')
mermaid_diagram = st.session_state.get('mermaid_diagram', '')

if transcript.strip() and utterances is not None:
    # Transcript
    st.markdown("### 📄 Transcript Preview")
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.code(transcript, language="text")
    st.markdown('</div>', unsafe_allow_html=True)

    # Classified Utterances
    st.markdown("### 🧠 Classified Utterances")
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.dataframe(utterances, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Summary
    st.markdown("### 📑 Summary")
    st.markdown('<div class="section summary-box">', unsafe_allow_html=True)
    st.markdown(summary)
    st.markdown('</div>', unsafe_allow_html=True)

    # Mermaid Diagram
    st.markdown("### 🔄 Dialogue Flow Diagram")
    st.markdown('<div class="section">', unsafe_allow_html=True)
    render_mermaid(mermaid_diagram)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("📥 Awaiting input. Upload a transcript file or paste text to begin.")
