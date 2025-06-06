import streamlit as st
from classify import classify_utterances
from summarise import generate_summary

st.set_page_config(page_title="Dialogue Analysis Platform", layout="wide")
st.title("Dialogue Analysis Platform")

st.markdown("""
<style>
    .stDataFrame {background: #fff; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

transcript = st.text_area("Paste transcript here:", height=200)
uploaded_file = st.file_uploader("Or upload a transcript file")

if uploaded_file:
    transcript = uploaded_file.read().decode("utf-8")

if transcript:
    utterances = classify_utterances(transcript)
    summary = generate_summary(transcript)
    st.subheader("Classified Utterances")
    st.dataframe([
        {
            "Speaker": u['speaker'],
            "Utterance": u['utterance'],
            "Function": u['function'],
            "Confidence/Rationale": u.get('confidence', u.get('rationale', '-'))
        } for u in utterances
    ])
    st.subheader("Structured Summary")
    st.write(summary)
    # Mermaid diagram (Streamlit does not natively support mermaid, but you can show the code block)
    from main import generate_mermaid_diagram
    mermaid_diagram = generate_mermaid_diagram(utterances)
    st.subheader("Dialogue Flow Diagram (Mermaid.js)")
    st.code(mermaid_diagram, language="mermaid")
