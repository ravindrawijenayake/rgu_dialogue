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
st.title("Dialogue Classifier & Summariser")
st.write("""
Upload a transcript file or paste your transcript below. The app will classify utterances, generate a summary, and visualize the dialogue flow.
""")

with st.form("transcript_form"):
    uploaded_file = st.file_uploader("Upload transcript file (UTF-8 text)", type=["txt"])
    transcript_text = st.text_area("Or paste transcript here", height=200)
    submitted = st.form_submit_button("Process Transcript")

transcript = ""
if submitted:
    if uploaded_file is not None:
        transcript = uploaded_file.read().decode("utf-8")
    elif transcript_text.strip():
        transcript = transcript_text
    else:
        st.warning("Please upload a file or paste transcript text.")

if transcript.strip():
    utterances = classify_utterances(transcript)
    summary = generate_summary(transcript)
    mermaid_diagram = generate_mermaid_diagram(utterances)

    st.subheader("Classified Utterances")
    if utterances:
        st.dataframe(utterances)
    else:
        st.info("No utterances classified.")

    st.subheader("Summary")
    st.write(summary)

    st.subheader("Dialogue Flow (Mermaid Diagram)")
    render_mermaid(mermaid_diagram)
else:
    st.info("Awaiting transcript input.")
