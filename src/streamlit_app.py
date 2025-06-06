import streamlit as st
from classify import classify_utterances
from summarise import generate_summary
from main import generate_mermaid_diagram

st.set_page_config(page_title="Dialogue Analysis Platform", layout="wide")
st.markdown("""
    <style>
        .container {max-width: 900px; margin: 0 auto 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); padding: 32px 36px 36px 36px;}
        .stDataFrame {background: #fff; border-radius: 8px;}
        .summary {background: #e8f7e4; padding: 18px 16px; margin-top: 28px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);}
        .dialogue-box {background: #f9f9f9; border: 1px solid #e0e6ed; border-radius: 8px; padding: 16px; margin-bottom: 24px;}
        .confidence-high { color: #388e3c; font-weight: 700; }
        .confidence-medium { color: #fbc02d; font-weight: 700; }
        .confidence-low { color: #d32f2f; font-weight: 700; }
        .mermaid {background: #fff; border-radius: 8px; padding: 16px; margin-top: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);}
        .stApp {padding-top: 0rem !important;}
    </style>
""", unsafe_allow_html=True)

st.title("Dialogue Analysis Platform ")
st.markdown("<h3 style='margin-top:0;'>Created by Ravindra Wijenayake</h3><p>for RGU DiSCoAI PhD Coding Task</p>", unsafe_allow_html=True)

with st.form("dialogue_form"):
    transcript = st.text_area("Paste transcript or upload file:", height=200, key="transcript")
    uploaded_file = st.file_uploader("Upload a transcript file", type=["txt"])
    submitted = st.form_submit_button("Analyse")
    clear = st.form_submit_button("Clear")

if uploaded_file:
    transcript = uploaded_file.read().decode("utf-8")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state['transcript'] = transcript
    st.experimental_rerun()
    st.stop()

if clear:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()
    st.stop()

if submitted and transcript:
    st.session_state['transcript'] = transcript
    st.session_state['analyse'] = True
    st.experimental_rerun()
    st.stop()

if transcript:
    # Show dialogue line by line
    st.markdown('<div class="dialogue-box"><h2>Input Dialogue</h2>' +
        ''.join(f'<div style="border-bottom:1px solid #eee;padding:2px 0;"><b>{line.split(":",1)[0]}</b>: {line.split(":",1)[1] if ":" in line else line}</div>' for line in transcript.strip().splitlines() if line.strip()) +
        '</div>', unsafe_allow_html=True)
    utterances = classify_utterances(transcript)
    summary = generate_summary(transcript)
    st.subheader("Classified Utterances")
    def confidence_style(val):
        if isinstance(val, float):
            if val >= 0.9:
                return 'confidence-high'
            elif val >= 0.6:
                return 'confidence-medium'
            else:
                return 'confidence-low'
        return ''
    import pandas as pd
    df = pd.DataFrame([
        {
            "Speaker": u['speaker'],
            "Utterance": u['utterance'],
            "Dialogue Function": u['function'],
            "Confidence/Rationale": u['confidence'] if u.get('confidence') else u.get('rationale', '-')
        } for u in utterances
    ])
    st.dataframe(df, use_container_width=True)
    st.markdown(f'<div class="summary"><h2>Structured Summary</h2><p>{summary}</p></div>', unsafe_allow_html=True)
    mermaid_diagram = generate_mermaid_diagram(utterances)
    st.markdown(f'<div class="summary"><h2>Dialogue Flow Diagram</h2></div>', unsafe_allow_html=True)
    # Render Mermaid diagram as an actual diagram using streamlit-mermaid if available, else fallback to code block
    try:
        import streamlit_mermaid as st_mermaid
        st_mermaid.st_mermaid(mermaid_diagram)
    except ImportError:
        st.code(mermaid_diagram, language="mermaid")
