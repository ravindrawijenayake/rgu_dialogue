import streamlit as st
from classify import classify_utterances
from summarise import generate_summary
from main import generate_mermaid_diagram

st.set_page_config(page_title="Dialogue Analysis Platform", layout="wide", page_icon="💬")
st.markdown("""
    <style>
        body, .stApp {background: #eaf4fb !important; padding-top: 0 !important;}
        .container {max-width: 900px; margin: 0 auto 40px auto; background: #fff; border-radius: 16px; box-shadow: 0 6px 32px rgba(44,62,80,0.10); padding: 36px 40px 40px 40px;}
        .stDataFrame {background: #fff; border-radius: 10px;}
        .summary {background: #e3f2fd; padding: 22px 18px; margin-top: 32px; border-radius: 10px; box-shadow: 0 2px 8px rgba(44,62,80,0.06);}
        .dialogue-box {background: #f4faff; border: 1px solid #b3d8f7; border-radius: 10px; padding: 18px; margin-bottom: 28px;}
        .confidence-high { color: #388e3c; font-weight: 700; }
        .confidence-medium { color: #fbc02d; font-weight: 700; }
        .confidence-low { color: #d32f2f; font-weight: 700; }
        .mermaid {background: #fff; border-radius: 10px; padding: 18px; margin-top: 12px; box-shadow: 0 2px 8px rgba(44,62,80,0.04);}
        .stButton>button {background: #1976d2; color: #fff; border-radius: 6px; border: none; padding: 10px 24px; font-size: 1rem; font-weight: 600; transition: background 0.2s; margin-right: 8px;}
        .stButton>button:hover {background: #1565c0;}
        .stTextArea textarea {font-size: 1.1rem; border-radius: 6px;}
        .stFileUploader {margin-bottom: 10px;}
        .stDataFrame {margin-top: 18px;}
        .stMarkdown h2 {color: #1976d2;}
        .stMarkdown h3 {color: #4b6584;}
        .stMarkdown pre {background: #eaf4fb; border-radius: 6px;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="container">', unsafe_allow_html=True)
st.markdown('''
    <div style="display:flex;align-items:center;gap:18px;margin-bottom:18px;">
        <img src="https://cdn-icons-png.flaticon.com/512/3062/3062634.png" width="60" style="border-radius:12px;box-shadow:0 2px 8px #1976d233;"/>
        <div>
            <h1 style="margin-bottom:0;color:#1976d2;">Dialogue Analysis Platform</h1>
            <div style="color:#4b6584;font-size:1.1rem;">for RGU DiSCoAI PhD Coding Task</div>
            <div style="font-size:0.95rem;color:#888;">Created by Ravindra Wijenayake</div>
        </div>
    </div>
''', unsafe_allow_html=True)

with st.form("dialogue_form"):
    st.markdown("<b>Paste transcript or upload file:</b>", unsafe_allow_html=True)
    transcript = st.text_area(
        "Paste your dialogue transcript here...",
        height=180,
        key="transcript",
        placeholder="E.g. Alice: Hello! How are you?\nBob: I'm good, thanks! And you?",
        help="Paste the dialogue transcript here. Each line should start with the speaker's name, followed by a colon."
    )
    uploaded_file = st.file_uploader(
        "Or upload a .txt transcript file",
        type=["txt"],
        help="Upload a plain text file with the dialogue transcript."
    )
    col1, col2, _ = st.columns([1,1,6])
    with col1:
        submitted = st.form_submit_button("\U0001F50D Analyse", help="Analyse the transcript and generate results.")
    with col2:
        clear = st.form_submit_button("\U0001F5D1 Clear", help="Clear the form and start again.")

if clear:
    st.experimental_rerun()

if uploaded_file:
    transcript = uploaded_file.read().decode("utf-8")

if transcript:
    st.markdown('<div class="dialogue-box"><h2>Input Dialogue</h2>' +
        ''.join(f'<div style="border-bottom:1px solid #eee;padding:2px 0;"><b>{line.split(":",1)[0]}</b>: {line.split(":",1)[1] if ":" in line else line}</div>' for line in transcript.strip().splitlines() if line.strip()) +
        '</div>', unsafe_allow_html=True)
    with st.spinner("Analysing dialogue, please wait..."):
        utterances = classify_utterances(transcript)
        summary = generate_summary(transcript)
    st.markdown("<h2>Classified Utterances</h2>", unsafe_allow_html=True)
    import pandas as pd
    def confidence_tag(val):
        if isinstance(val, str) and val.lower().startswith("high"):
            return f'<span class="confidence-high">\u25CF High</span>'
        elif isinstance(val, str) and val.lower().startswith("medium"):
            return f'<span class="confidence-medium">\u25CF Medium</span>'
        elif isinstance(val, str) and val.lower().startswith("low"):
            return f'<span class="confidence-low">\u25CF Low</span>'
        return val
    df = pd.DataFrame([
        {
            "Speaker": u['speaker'],
            "Utterance": u['utterance'],
            "Dialogue Function": u['function'],
            "Confidence/Rationale": confidence_tag(u['confidence']) if u.get('confidence') else u.get('rationale', '-')
        } for u in utterances
    ])
    st.write('<style>td span.confidence-high{color:#388e3c;font-weight:700;}td span.confidence-medium{color:#fbc02d;font-weight:700;}td span.confidence-low{color:#d32f2f;font-weight:700;}</style>', unsafe_allow_html=True)
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.markdown(f'<div class="summary"><h2>Structured Summary</h2><p>{summary}</p></div>', unsafe_allow_html=True)
    mermaid_diagram = generate_mermaid_diagram(utterances)
    st.markdown(f'<div class="summary"><h2>Dialogue Flow Diagram</h2></div>', unsafe_allow_html=True)
    try:
        import streamlit_mermaid as st_mermaid
        st_mermaid.st_mermaid(mermaid_diagram)
    except ImportError:
        st.code(mermaid_diagram, language="mermaid")

# Footer with credits and links
st.markdown('''<hr style="margin:32px 0 12px 0;"/>
<div style="text-align:center;color:#888;font-size:0.97rem;">
    <span>Made with <span style="color:#1976d2;">Streamlit</span> &middot; <a href="https://github.com/ravindrawijenayake" style="color:#1976d2;">GitHub</a></span>
</div>
''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
