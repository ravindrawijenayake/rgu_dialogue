# Dialogue Classification and Summarisation System

This project provides both a Streamlit and Flask web interface for classifying utterances, generating summaries, and visualizing dialogue flows from transcript files. It uses Google Gemini for high-quality, function-aware summarisation and rule-based logic for dialogue classification.

## Features
- Summarises dialogues into narrative form, highlighting dialogue functions (e.g., proposal, challenge, agreement, suggestion, commitment)
- Uses rule-based classification logic in `src/classify.py` for dialogue function detection
- Visualises dialogue flow and displays confidence scores or rationales for classifications
- Download summary as PDF (Streamlit)
- Supports both Streamlit and Flask web interfaces
- Mermaid.js diagram rendering (Streamlit: via streamlit-mermaid, Flask: via CDN)

## Requirements
- Python 3.8+
- pip
- All dependencies in `requirements.txt` (see below)

## Installation
Clone the repository:
```sh
git clone https://github.com/ravindrawijenayake/rgu_dialogue.git
cd rgu_dialogue
```
Install dependencies:
```sh
pip install -r requirements.txt
```

## Google Gemini API Key Setup
To use Google Gemini for summarisation, set your API key as an environment variable:

**Windows:**
- Open the Start menu and search for “Environment Variables”.
- Click “Edit the system environment variables”.
- Click “Environment Variables…”.

Under “System variables”, click “New…”.

- Set the variable name as `GOOGLE_API_KEY` and the value as your Gemini API key.
- Click OK and restart your terminal.

**MacOS/Linux:**
- Open a terminal.
- Run `export GOOGLE_API_KEY='your_api_key'`.
- To make this permanent, add the above line to your `~/.bashrc`, `~/.zshrc`, or `~/.profile`.

**Streamlit Cloud:**
- Add `GOOGLE_API_KEY` as a secret in your app’s settings.

**GitHub Actions or CI/CD:**
- Go to your repository’s Settings > Secrets and variables > Actions.
- Add a new secret named `GOOGLE_API_KEY`.
- Reference it in your workflow as an environment variable.

**Google Cloud (App Engine, Cloud Run, etc.):**
- Set the environment variable in your deployment configuration.

**Security:**
- Never commit your API key to the repository or store it in code, .env, or any file in the repository.
- Always use environment variables or platform secrets for deployment.

## Usage

### Streamlit App
Run the Streamlit interface:
```sh
streamlit run src/streamlit_app.py
```
- Use the sidebar to toggle summary and diagram options.
- Upload a transcript file or paste text, then process and download results.

### Flask App
Run the Flask web app:
```sh
python src/main.py
```
- Visit http://localhost:5000 in your browser.
- Use the web form to upload or paste a transcript and view results.

## Dialogue Classification
The system uses rule-based heuristics to classify each utterance in the transcript into dialogue functions such as Proposal, Commitment, Deferral, Challenge, Justification, Agreement, Disagreement, Acknowledgement, Inform, and more. Each utterance is shown with a confidence score or rationale for its classification. The classification logic is implemented in `src/classify.py` and can be extended or replaced with a machine learning model if desired.

## Visualisation & Confidence
- The web interface visualises the dialogue as a flow diagram using Mermaid.js.
- The Streamlit app uses the streamlit-mermaid package to always render the dialogue flow visually as a diagram.
- Each utterance is shown with a confidence score or rationale for its classification.

## Project Structure
```
requirements.txt
src/
    API.txt
    classify.py
    main.py
    summarise.py
    streamlit_app.py
    unclassified_utterances.log
    static/
        style.css
    templates/
        index.html
```
- `main.py`: Entry point for running the Flask web interface (for local or WSGI deployment).
- `streamlit_app.py`: Entry point for the Streamlit web interface (for Streamlit Cloud or local Streamlit use).
- `summarise.py`: Contains the summarisation logic (uses Google Gemini for long dialogues).
- `classify.py`: Rule-based classification of utterances/dialogue acts.
- `templates/`: Contains HTML templates for the Flask web interface.
- `static/`: Contains CSS for the Flask web interface.

## Customisation
- You can modify the prompt in `summarise.py` to adjust the style or detail of the summaries.
- To use a different LLM or local model, update the relevant code in `summarise.py`.

## Approach
This project combines rule-based natural language processing and large language model (LLM) summarization to analyse and summarise multi-party dialogues. Each utterance in a transcript is classified into a dialogue function (such as Proposal, Commitment, Challenge, etc.) using a set of carefully designed heuristics. For short dialogues, a narrative summary is generated using these classifications and logical rules. For longer dialogues, the system leverages Google Gemini (via the google-generativeai API) to produce a high-quality, context-aware summary. The web interface also visualizes the dialogue flow and provides confidence scores or rationales for each classification, supporting both transparency and interpretability.

## Contact
For questions or contributions, please open an issue or pull request on GitHub.

## Credits
Created by Ravindra Wijenayake for RGU DiSCoAI.
