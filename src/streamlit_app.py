import streamlit as st
from classify import classify_utterances
from summarise import generate_summary
from main import generate_mermaid_diagram
import pandas as pd

# --- Sidebar ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=60)
st.sidebar.title("Dialogue Analysis Platform")
st.sidebar.markdown("""
**Instructions:**
- Paste or upload a dialogue transcript.
- Click **Analyse** to process.
- View results in the tabs.
""")
if st.sidebar.button("Show Sample Transcript"):
    st.session_state['transcript'] = "Alice: Hello! How are you?\nBob: I'm good, thanks! And you?\nAlice: Doing well!"

# --- Main Card Layout ---
st.markdown('<div class="container">', unsafe_allow_html=True)
st.markdown("""
    <style>
        .container {max-width: 900px; margin: 0 auto 40px auto; background: #fff; border-radius: 16px; box-shadow: 0 6px 32px rgba(44,62,80,0.10); padding: 36px 40px 40px 40px;}
        .stTabs [data-baseweb="tab"] {font-size:1.1rem; font-weight:600;}
        .chip {display:inline-block;padding:2px 10px;border-radius:12px;font-size:0.95em;margin-right:4px;}
        .chip-func {background:#e3f2fd;color:#1976d2;}
        .chip-high {background:#e8f5e9;color:#388e3c;}
        .chip-medium {background:#fffde7;color:#fbc02d;}
        .chip-low {background:#ffebee;color:#d32f2f;}
        .footer {text-align:center;color:#888;font-size:0.97rem;margin-top:32px;}
    </style>
""", unsafe_allow_html=True)

# --- Input Section ---
tabs = st.tabs(["Paste", "Upload", "Sample"])
with tabs[0]:
    transcript = st.text_area(
        "Paste your dialogue transcript here...",
        value=st.session_state.get('transcript', ''),
        height=180,
        key="transcript",
        placeholder="E.g. Alice: Hello! How are you?\nBob: I'm good, thanks! And you?",
        help="Each line should start with the speaker's name, followed by a colon."
    )
    st.caption(f"{len(transcript)} characters, {len(transcript.splitlines())} lines")
with tabs[1]:
    uploaded_file = st.file_uploader(
        "Upload a .txt transcript file",
        type=["txt"],
        help="Upload a plain text file with the dialogue transcript."
    )
    if uploaded_file:
        transcript = uploaded_file.read().decode("utf-8")
        st.session_state['transcript'] = transcript
        st.experimental_rerun()
with tabs[2]:
    if st.button("Insert Sample Transcript"):
        st.session_state['transcript'] = "Alice: Hello! How are you?\nBob: I'm good, thanks! And you?\nAlice: Doing well!"
        st.experimental_rerun()

# --- Analyse Button ---
if st.button("\U0001F50D Analyse", help="Analyse the transcript and generate results."):
    if not st.session_state.get('transcript', '').strip():
        st.error("Please provide a transcript to analyse.")
    else:
        with st.spinner("Analysing dialogue, please wait..."):
            utterances = classify_utterances(st.session_state['transcript'])
            summary = generate_summary(st.session_state['transcript'])
            mermaid_diagram = generate_mermaid_diagram(utterances)
        st.session_state['utterances'] = utterances
        st.session_state['summary'] = summary
        st.session_state['mermaid'] = mermaid_diagram
        st.success("Analysis complete! See results below.")

# --- Results Section ---
if st.session_state.get('utterances'):
    result_tabs = st.tabs(["Utterances Table", "Summary", "Flow Diagram"])
    with result_tabs[0]:
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
    with result_tabs[1]:
        st.markdown(f'<div class="summary"><h2>Structured Summary</h2><p>{st.session_state["summary"]}</p></div>', unsafe_allow_html=True)
    with result_tabs[2]:
        st.markdown(f'<div class="summary"><h2>Dialogue Flow Diagram</h2></div>', unsafe_allow_html=True)
        try:
            import streamlit_mermaid as st_mermaid
            st_mermaid.st_mermaid(st.session_state['mermaid'])
        except ImportError:
            st.code(st.session_state['mermaid'], language="mermaid")

# --- Footer ---
st.markdown('<div class="footer">Made with <span style="color:#1976d2;">Streamlit</span> &middot; <a href="https://github.com/ravindrawijenayake" style="color:#1976d2;">GitHub</a></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
