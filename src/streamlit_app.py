import streamlit as st
from classify import classify_utterances
from summarise import generate_summary
from main import generate_mermaid_diagram

st.set_page_config(page_title="Dialogue Analysis Platform", layout="wide", page_icon="💬")
st.markdown("""
    <style>
        .container {max-width: 900px; margin: 0 auto 40px auto; background: #fff; border-radius: 16px; box-shadow: 0 6px 32px rgba(44,62,80,0.10); padding: 36px 40px 40px 40px;}
        .stDataFrame {background: #fff; border-radius: 10px;}
        .summary {background: #e8f7e4; padding: 22px 18px; margin-top: 32px; border-radius: 10px; box-shadow: 0 2px 8px rgba(44,62,80,0.06);}
        .dialogue-box {background: #f9f9f9; border: 1px solid #e0e6ed; border-radius: 10px; padding: 18px; margin-bottom: 28px;}
        .confidence-high { color: #388e3c; font-weight: 700; }
        .confidence-medium { color: #fbc02d; font-weight: 700; }
        .confidence-low { color: #d32f2f; font-weight: 700; }
        .mermaid {background: #fff; border-radius: 10px; padding: 18px; margin-top: 12px; box-shadow: 0 2px 8px rgba(44,62,80,0.04);}
        .stApp {padding-top: 0rem !important;}
        .stButton>button {background: #2a4d69; color: #fff; border-radius: 6px; border: none; padding: 10px 24px; font-size: 1rem; font-weight: 600; transition: background 0.2s;}
        .stButton>button:hover {background: #1e3550;}
        .stTextArea textarea {font-size: 1.1rem; border-radius: 6px;}
        .stFileUploader {margin-bottom: 10px;}
        .stDataFrame {margin-top: 18px;}
        .stMarkdown h2 {color: #2a4d69;}
        .stMarkdown h3 {color: #4b6584;}
        .stMarkdown pre {background: #f4f8fb; border-radius: 6px;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="container">', unsafe_allow_html=True)
st.markdown("""
# 💬 Dialogue Analysis Platform
#### Created by Ravindra Wijenayake
""", unsafe_allow_html=True)

with st.form("dialogue_form"):
    st.markdown("<b>Paste transcript or upload file:</b>", unsafe_allow_html=True)
    transcript = st.text_area("", height=180, key="transcript", placeholder="Paste your dialogue transcript here...")
    uploaded_file = st.file_uploader("Upload a transcript file", type=["txt"])
    col1, col2 = st.columns([1,1])
    with col1:
        submitted = st.form_submit_button("Analyse")
    with col2:
        clear = st.form_submit_button("Clear")

if clear:
    st.experimental_rerun()

if uploaded_file:
    transcript = uploaded_file.read().decode("utf-8")

if transcript:
    st.markdown('<div class="dialogue-box"><h2>Input Dialogue</h2>' +
        ''.join(f'<div style="border-bottom:1px solid #eee;padding:2px 0;"><b>{line.split(":",1)[0]}</b>: {line.split(":",1)[1] if ":" in line else line}</div>' for line in transcript.strip().splitlines() if line.strip()) +
        '</div>', unsafe_allow_html=True)
    utterances = classify_utterances(transcript)
    summary = generate_summary(transcript)
    st.markdown("<h2>Classified Utterances</h2>", unsafe_allow_html=True)
    import pandas as pd
    df = pd.DataFrame([
        {
            "Speaker": u['speaker'],
            "Utterance": u['utterance'],
            "Dialogue Function": u['function'],
            "Confidence/Rationale": u['confidence'] if u.get('confidence') else u.get('rationale', '-')
        } for u in utterances
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown(f'<div class="summary"><h2>Structured Summary</h2><p>{summary}</p></div>', unsafe_allow_html=True)
    mermaid_diagram = generate_mermaid_diagram(utterances)
    st.markdown(f'<div class="summary"><h2>Dialogue Flow Diagram</h2></div>', unsafe_allow_html=True)
    try:
        import streamlit_mermaid as st_mermaid
        st_mermaid.st_mermaid(mermaid_diagram)
    except ImportError:
        st.code(mermaid_diagram, language="mermaid")
st.markdown('</div>', unsafe_allow_html=True)
