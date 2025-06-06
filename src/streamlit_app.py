import streamlit as st
from classify import classify_utterances
from summarise import generate_summary
from io import BytesIO
from reportlab.pdfgen import canvas

# === Page config ===
st.set_page_config(page_title="Dialogue Classifier & Summariser", layout="wide")

# === Sidebar for settings ===
with st.sidebar:
    st.header("⚙️ Settings")
    show_summary = st.checkbox("Show Summary", value=True)
    show_mermaid = st.checkbox("Show Dialogue Flow (Mermaid)", value=True)
    mermaid_direction = st.radio(
        "Mermaid Flow Direction",
        options=["TD (Top-Down)", "LR (Left-Right)"],
        index=0,
        key="mermaid_direction_radio"
    )

# === Custom CSS for colors and styling ===
st.markdown('''
<style>
body { background: #021418; }
.stApp { background-color: #9ddffb; padding: 1rem; }
.stButton>button.process-btn {
    background-color: #8684f5; color: white; border-radius: 6px; font-weight: bold;
}
.stButton>button.process-btn:hover {
    background-color: #615fd9;
}
.stButton>button.clear-btn {
    background-color: #f29cbe; color: white; border-radius: 6px; font-weight: bold;
}
.stButton>button.clear-btn:hover {
    background-color: #d6718a;
}
.stTextArea textarea, .stFileUploader, .stDataFrame {
    background: #e6f2ff; border-radius: 8px; padding: 5px;
}
.summary-box {
    background-color: #f0f8ff; border: 2px solid #8684f5; border-radius: 8px;
    padding: 16px; color: #1B2845; font-size: 1.1em; margin-bottom: 10px;
}
.section-header {
    border-bottom: 2px solid #8684f5; padding-bottom: 5px; margin-top: 20px; margin-bottom: 10px;
    color: #1B2845; font-weight: bold; font-size: 1.3em;
}
</style>
''', unsafe_allow_html=True)

# === Helper functions ===
def render_mermaid(mermaid_code):
    try:
        from streamlit_mermaid import st_mermaid
        st_mermaid(mermaid_code)
    except ImportError:
        st.info("Install streamlit-mermaid or copy code to Mermaid live editor.")
        st.code(mermaid_code, language="mermaid")

def generate_mermaid_diagram(utterances, direction="TD"):
    nodes = []
    edges = []
    for i, u in enumerate(utterances):
        node_id = f"U{i}"
        label = f"{u['speaker']}: {u['function']}"
        nodes.append(f'{node_id}["{label}"]')
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

# === Initialize session state keys if missing ===
default_keys = ['transcript', 'uploaded_file', 'utterances', 'summary', 'mermaid_diagram']
for key in default_keys:
    if key not in st.session_state:
        st.session_state[key] = '' if key != 'utterances' else None

# === Title ===
st.markdown('<h1>🗣️ Dialogue Analysis Platform</h1>', unsafe_allow_html=True)
st.markdown("Upload a transcript file or paste your transcript below. The app will classify utterances, generate a summary, and visualize the dialogue flow.")

# === Input Section ===
st.markdown('<div class="section-header">Input Transcript</div>', unsafe_allow_html=True)

with st.form("transcript_form", clear_on_submit=False):
    uploaded_file = st.file_uploader("Upload transcript file (UTF-8 text)", type=["txt"], key="uploaded_file")
    transcript_input = st.text_area("Or paste transcript here", value=st.session_state['transcript'], height=200, key="transcript_text_area")
    col1, col2 = st.columns([1,1])
    with col1:
        submitted = st.form_submit_button("🔍 Process Transcript", help="Classify utterances and generate summary", kwargs=None, type="primary")
    with col2:
        clear_clicked = st.form_submit_button("🗑️ Clear All", help="Clear all inputs and outputs", kwargs=None, type="secondary")

# === Clear functionality ===
if clear_clicked:
    for key in default_keys:
        st.session_state[key] = '' if key != 'utterances' else None
    st.session_state['uploaded_file'] = None
    st.session_state['transcript'] = ''
    st.experimental_rerun()

# === Process transcript ===
if submitted:
    transcript = ''
    if uploaded_file is not None:
        try:
            transcript = uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.error("Error reading uploaded file. Please upload a valid UTF-8 text file.")
            transcript = ''
    elif transcript_input.strip():
        transcript = transcript_input.strip()
    else:
        st.warning("⚠️ Please upload a file or paste transcript text.")
        transcript = ''

    if transcript:
        try:
            utterances = classify_utterances(transcript)
            summary = generate_summary(transcript)
            mermaid_dir = mermaid_direction.split()[0]  # "TD" or "LR"
            mermaid_diagram = generate_mermaid_diagram(utterances, direction=mermaid_dir)

            # Update session state only after successful processing
            st.session_state['transcript'] = transcript
            st.session_state['utterances'] = utterances
            st.session_state['summary'] = summary
            st.session_state['mermaid_diagram'] = mermaid_diagram

        except Exception as e:
            st.error("⚠️ Failed to process the transcript. Please check input format.")
            st.exception(e)

# === Output Section ===
transcript = st.session_state['transcript']
utterances = st.session_state['utterances']
summary = st.session_state['summary']
mermaid_diagram = st.session_state['mermaid_diagram']

if transcript.strip() and utterances is not None:
    st.markdown('<div class="section-header">Output</div>', unsafe_allow_html=True)

    st.subheader("📄 Transcript")
    st.code(transcript, language="text")

    st.subheader("🧠 Classified Utterances")
    st.dataframe(utterances, use_container_width=True)

    if show_summary:
        st.subheader("📑 Summary")
        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
        pdf_buffer = generate_pdf(summary)
        st.download_button("📥 Download Summary as PDF", data=pdf_buffer, file_name="summary.pdf", mime="application/pdf")

    if show_mermaid:
        st.subheader("🔄 Dialogue Flow")
        render_mermaid(mermaid_diagram)
else:
    st.info("Awaiting transcript input. Upload a file or paste text, then click 'Process Transcript'.")
