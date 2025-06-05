from flask import Flask, request, render_template
from classify import classify_utterances
from summarise import generate_summary
import os

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

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    transcript = ''
    utterances = []
    summary = ''
    mermaid_diagram = ''
    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            transcript = file.read().decode('utf-8')
        else:
            transcript = request.form.get('transcript', '')
        if transcript.strip():
            utterances = classify_utterances(transcript)
            summary = generate_summary(transcript)
            mermaid_diagram = generate_mermaid_diagram(utterances)
    return render_template('index.html', transcript=transcript, utterances=utterances, summary=summary, mermaid_diagram=mermaid_diagram)

if __name__ == '__main__':
    app.run(debug=True)