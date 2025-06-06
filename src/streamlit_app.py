import streamlit as st
from classify import classify_utterances
from summarise import generate_summary
import base64

# Helper to render Mermaid diagrams in Streamlit (requires st_mermaid or iframe fallback)
def render_mermaid(mermaid_code):
    try:
        from streamlit_mermaid import st_mermaid
        st_mermaid(mermaid_code)
    except ImportError:
        st.info("Install streamlit-mermaid for diagram rendering, or copy the code below to a Mermaid live editor.")
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
    diagram = "graph TD\n" + "\n".join(nodes + edges)
    return diagram

st.set_page_config(page_title="Dialogue Classifier & Summariser", layout="wide")

# --- Session State for Inputs/Outputs ---
if 'transcript' not in st.session_state:
    st.session_state['transcript'] = ''
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None
if 'utterances' not in st.session_state:
    st.session_state['utterances'] = None
if 'summary' not in st.session_state:
    st.session_state['summary'] = ''
if 'mermaid_diagram' not in st.session_state:
    st.session_state['mermaid_diagram'] = ''

st.title("🗣️ Dialogue Analysis Platform")
st.markdown("""
Upload a transcript file or paste your transcript below. The app will classify utterances, generate a summary, and visualize the dialogue flow.
""")
st.divider()

# --- Inject Custom CSS for Colorful UI ---
st.markdown('''
    <style>
    body { background: linear-gradient(120deg, #f6d365 0%, #fda085 100%); }
    .stApp { background: linear-gradient(120deg, #f6d365 0%, #fda085 100%); }
    .stButton>button { background-color: #4F8BF9; color: white; border-radius: 8px; border: none; margin-right: 8px; font-weight: bold; }
    .stButton>button:hover { background-color: #1B2845; color: #f6d365; }
    .stTextArea textarea { background: #fffbe7; border: 2px solid #fda085; border-radius: 8px; }
    .stFileUploader { background: #fffbe7; border-radius: 8px; }
    .stDataFrame { background: #fffbe7; border-radius: 8px; }
    .stAlert { background: #f6d365; color: #1B2845; border-radius: 8px; }
    .stCodeBlock { background: #f6d365; color: #1B2845; border-radius: 8px; }
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 { color: #1B2845; }
    </style>
''', unsafe_allow_html=True)

# --- UI Layout: Input Area with Process & Clear Buttons ---
with st.form("transcript_form", clear_on_submit=False):
    uploaded_file = st.file_uploader("Upload transcript file (UTF-8 text)", type=["txt"])
    transcript_text = st.text_area("Or paste transcript here", value=st.session_state['transcript'], height=200, key="transcript_text_area")
    btn_col1, btn_col2 = st.columns([1,1])
    with btn_col1:
        submitted = st.form_submit_button("Process Transcript", use_container_width=True)
    with btn_col2:
        clear_clicked = st.form_submit_button("Clear", use_container_width=True)

# --- Clear Button Functionality ---
if clear_clicked:
    st.session_state['transcript'] = ''
    st.session_state['uploaded_file'] = None
    st.session_state['utterances'] = None
    st.session_state['summary'] = ''
    st.session_state['mermaid_diagram'] = ''
    st.session_state['transcript_text_area'] = ''
    st.experimental_rerun()

# --- Process Transcript ---
if submitted:
    if uploaded_file is not None:
        transcript = uploaded_file.read().decode("utf-8")
        st.session_state['transcript'] = transcript
    elif transcript_text.strip():
        transcript = transcript_text
        st.session_state['transcript'] = transcript
    else:
        st.warning("Please upload a file or paste transcript text.")
        transcript = ''
    if transcript.strip():
        utterances = classify_utterances(transcript)
        summary = generate_summary(transcript)
        mermaid_diagram = generate_mermaid_diagram(utterances)
        st.session_state['utterances'] = utterances
        st.session_state['summary'] = summary
        st.session_state['mermaid_diagram'] = mermaid_diagram
else:
    transcript = st.session_state['transcript']
    utterances = st.session_state['utterances']
    summary = st.session_state['summary']
    mermaid_diagram = st.session_state['mermaid_diagram']

# --- Output Section ---
if transcript.strip() and utterances is not None:
    st.divider()
    st.subheader("Input Transcript")
    st.code(transcript, language="text")
    st.divider()
    st.subheader("Classified Utterances")
    if utterances:
        st.dataframe(utterances, use_container_width=True)
    else:
        st.info("No utterances classified.")
    st.divider()
    st.subheader("Summary")
    st.write(summary)
    st.divider()
    st.subheader("Dialogue Flow (Mermaid Diagram)")
    render_mermaid(mermaid_diagram)
else:
    st.info("Awaiting transcript input. Upload a file or paste text, then click 'Process Transcript'.")
