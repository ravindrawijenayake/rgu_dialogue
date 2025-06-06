import streamlit as st
from classify import classify_utterances
from summarise import generate_summary
import base64
import os

# Inject custom CSS from static/style.css
with open(os.path.join(os.path.dirname(__file__), "static", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
st.markdown('<div class="container">', unsafe_allow_html=True)
st.title("Dialogue Classifier & Summariser")
st.write("""
Upload a transcript file or paste your transcript below. The app will classify utterances, generate a summary, and visualize the dialogue flow.
""")

# Session state for clearing
if 'transcript' not in st.session_state:
    st.session_state['transcript'] = ''
if 'utterances' not in st.session_state:
    st.session_state['utterances'] = None
if 'summary' not in st.session_state:
    st.session_state['summary'] = ''
if 'mermaid_diagram' not in st.session_state:
    st.session_state['mermaid_diagram'] = ''

with st.form("transcript_form"):
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload transcript file (UTF-8 text)", type=["txt"])
    transcript_text = st.text_area("Or paste transcript here", value=st.session_state['transcript'], height=200)
    st.markdown('</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        submitted = st.form_submit_button("Process Transcript")
    with col2:
        cleared = st.form_submit_button("Clear All")

if submitted:
    if uploaded_file is not None:
        transcript = uploaded_file.read().decode("utf-8")
    elif transcript_text.strip():
        transcript = transcript_text
    else:
        st.warning("Please upload a file or paste transcript text.")
        transcript = ''
    st.session_state['transcript'] = transcript
    if transcript.strip():
        utterances = classify_utterances(transcript)
        summary = generate_summary(transcript)
        mermaid_diagram = generate_mermaid_diagram(utterances)
        st.session_state['utterances'] = utterances
        st.session_state['summary'] = summary
        st.session_state['mermaid_diagram'] = mermaid_diagram
    else:
        st.session_state['utterances'] = None
        st.session_state['summary'] = ''
        st.session_state['mermaid_diagram'] = ''

if cleared:
    st.session_state['transcript'] = ''
    st.session_state['utterances'] = None
    st.session_state['summary'] = ''
    st.session_state['mermaid_diagram'] = ''
    st.experimental_rerun()

if st.session_state['transcript'].strip() and st.session_state['utterances'] is not None:
    st.markdown('<div class="dialogue-box">', unsafe_allow_html=True)
    st.subheader("Classified Utterances")
    st.dataframe(st.session_state['utterances'])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="summary">', unsafe_allow_html=True)
    st.subheader("Summary")
    st.write(st.session_state['summary'])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="mermaid">', unsafe_allow_html=True)
    st.subheader("Dialogue Flow (Mermaid Diagram)")
    render_mermaid(st.session_state['mermaid_diagram'])
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Awaiting transcript input.")
st.markdown('</div>', unsafe_allow_html=True)
