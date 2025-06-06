import streamlit as st
from classify import classify_utterances
from summarise import generate_summary
from io import BytesIO
from reportlab.pdfgen import canvas

# ========== Page Configuration ==========
st.set_page_config(page_title="Dialogue Classifier & Summariser", layout="wide")

# ========== Sidebar Settings ==========
with st.sidebar:
    st.header("⚙️ Settings")
    show_summary = st.checkbox("Show Summary", value=True)
    show_mermaid = st.checkbox("Show Dialogue Flow (Mermaid)", value=True)
    mermaid_direction = st.radio(
        "Mermaid Flow Direction",
        options=["TD (Top-Down)", "LR (Left-Right)"],
        index=0
    )

# ========== Custom CSS ==========
st.markdown('''<style>
body { background: #a2f5fb; }
.stApp { background-color: #ffffff; padding: 1rem; }
.stButton>button { background-color: #1f3b4d; color: white; border-radius: 6px; font-weight: bold; }
.stButton>button:hover { background-color: #0e2433; }
.stTextArea textarea, .stFileUploader, .stDataFrame { background: #ffebeb; border-radius: 8px; }
.summary-box { background-color: #f7dbff; border: 2px solid #fda085; border-radius: 8px; padding: 16px; color: #1B2845; font-size: 1.1em; }
</style>''', unsafe_allow_html=True)

# ========== Helper Functions ==========
def render_mermaid(mermaid_code):
    try:
        from streamlit_mermaid import st_mermaid
        st_mermaid(mermaid_code)
    except ImportError:
        st.info("Install streamlit-mermaid or copy to Mermaid live editor.")
        st.code(mermaid_code, language="mermaid")

def generate_mermaid_diagram(utterances, direction="TD"):
    nodes = []
    edges = []
    for i, u in enumerate(utterances):
        node_id = f"U{i}"
        label = f"{u['speaker']}: {u['function']}"
        nodes.append(f"{node_id}[{label}]")
        if i > 0:
            edges.append(f"U{i-1} --> U{i}")
    return f"graph {direction}\n" + "\n".join(nodes + edges)

def generate_pdf(summary_text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica", 12)
    width, height = c._pagesize
    lines = summary_text.split("\n")
    y = height - 50
    for line in lines:
        c.drawString(40, y, line)
        y -= 20
        if y < 40:
            c.showPage()
            y = height - 50
    c.save()
    buffer.seek(0)
    return buffer

# ========== Session State ==========
def_keys = ['transcript', 'uploaded_file', 'utterances', 'summary', 'mermaid_diagram']
for key in def_keys:
    if key not in st.session_state:
        st.session_state[key] = '' if key not in ['utterances', 'uploaded_file'] else None

# ========== Title ==========
st.markdown('<h1>🗣️ Dialogue Analysis Platform</h1><br><h4>Created by Ravindra Wijenayake-for RGU DiSCoAI', unsafe_allow_html=True)
st.markdown("""
Upload a transcript file or paste your transcript below. The app will classify utterances, generate a summary, and visualize the dialogue flow.
""")

st.divider()

# ========== Transcript Input ==========
with st.form("transcript_form", clear_on_submit=False):
    uploaded_file = st.file_uploader("Upload transcript file (UTF-8 text)", type=["txt"])
    transcript_input = st.text_area("Or paste transcript here", value=st.session_state.get('transcript', ''), height=200, key="transcript")
    submitted = st.form_submit_button("🔍 Process Transcript", use_container_width=True)

# ========== Clear Button ==========
if st.button("🗑️ Clear All", use_container_width=True):
    for key in def_keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ========== Process Input ==========
if submitted:
    if uploaded_file is not None:
        transcript = uploaded_file.read().decode("utf-8")
        st.session_state['transcript'] = transcript
    elif transcript_input.strip():
        transcript = transcript_input
        st.session_state['transcript'] = transcript
    else:
        st.warning("⚠️ Please upload a file or paste transcript text.")
        transcript = ''

    if transcript.strip():
        try:
            utterances = classify_utterances(transcript)
            summary = generate_summary(transcript)
            mermaid_diagram = generate_mermaid_diagram(utterances, direction=mermaid_direction.split()[0])

            st.session_state['utterances'] = utterances
            st.session_state['summary'] = summary
            st.session_state['mermaid_diagram'] = mermaid_diagram

        except Exception as e:
            st.error("⚠️ Failed to process the transcript. Please check the input or try again.")
            st.exception(e)

# ========== Display Outputs ==========
transcript = st.session_state['transcript']
utterances = st.session_state['utterances']
summary = st.session_state['summary']
mermaid_diagram = st.session_state['mermaid_diagram']

if transcript.strip() and utterances is not None:
    st.divider()
    st.subheader("📄 Transcript")
    st.code(transcript, language="text")

    st.divider()
    st.subheader("🧠 Classified Utterances")
    st.dataframe(utterances, use_container_width=True)

    if show_summary:
        st.divider()
        st.subheader("📑 Summary")
        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

        pdf_buffer = generate_pdf(summary)
        st.download_button("📥 Download Summary as PDF", data=pdf_buffer, file_name="summary.pdf", mime="application/pdf")

    if show_mermaid:
        st.divider()
        st.subheader("🔄 Dialogue Flow")
        render_mermaid(mermaid_diagram)
else:
    st.info("Awaiting transcript input. Upload a file or paste text, then click 'Process Transcript'.")
