# Dialogue Classification and Summarisation System

This project provides a system for summarising multi-party dialogues into concise, narrative summaries that capture the structure and evolution of the conversation. It uses Google Gemini for high-quality, function-aware summarisation and rule-based logic for dialogue classification.

## Features

- Summarises dialogues into narrative form, highlighting dialogue functions (e.g., proposal, challenge, agreement, suggestion, commitment).
- Uses rule-based classification logic in `src/classify.py` for dialogue function detection.
- Visualises dialogue flow and displays confidence scores or rationales for classifications.

## Requirements

- Python 3.8+
- pip

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/ravindrawijenayake/rgu_dialogue.git
   cd rgu_dialogue
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## Google Gemini API Key Setup

To use Google Gemini for summarisation, set your API key as an environment variable:

### Windows

1. Open the Start menu and search for “Environment Variables”.
2. Click “Edit the system environment variables”.
3. Click “Environment Variables…”.
4. Under “System variables”, click “New…”.
5. Set the variable name as `GOOGLE_API_KEY` and the value as your Gemini API key.
6. Click OK and restart your terminal.

### macOS/Linux

1. Open a terminal.
2. Run `export GOOGLE_API_KEY='your_api_key'`.
3. To make this permanent, add the above line to your `~/.bashrc`, `~/.zshrc`, or `~/.profile`.

**Never share your API key or commit it to version control.**

## API Key Security and Deployment Best Practices

**Never commit your API key to the repository.**

- The code expects the Google Gemini API key to be set as an environment variable named `GOOGLE_API_KEY`.
- For local development, set the variable in your terminal before running the app:
  - Windows:
    ```sh
    set GOOGLE_API_KEY=your-actual-api-key
    ```
  - macOS/Linux:
    ```sh
    export GOOGLE_API_KEY=your-actual-api-key
    ```
- For GitHub Actions or CI/CD:
  - Go to your repository’s Settings > Secrets and variables > Actions.
  - Add a new secret named `GOOGLE_API_KEY`.
  - Reference it in your workflow as an environment variable.
- For Google Cloud (App Engine, Cloud Run, etc.):
  - Set the environment variable in your deployment configuration (see Deployment section above).
- For Streamlit Cloud:
  - Add `GOOGLE_API_KEY` as a secret in your app’s settings.

**Summary:**
- Do not store or commit your API key in code, .env, or any file in the repository.
- Always use environment variables or platform secrets for deployment.
- This keeps your credentials secure and your project safe.

## Usage

1. Place your dialogue transcript in a text file (e.g., `transcript1.txt`).
2. Run the main script:
   ```sh
   python src/main.py
   ```
3. The system will process the transcript and output a narrative summary using Google Gemini and rule-based classification.

## Dialogue Classification

The system uses rule-based heuristics to classify each utterance in the transcript into dialogue functions such as Proposal, Commitment, Deferral, Challenge, Justification, Agreement, Disagreement, Acknowledgement, Inform, and more. Each utterance is shown with a confidence score or rationale for its classification. The classification logic is implemented in `src/classify.py` and can be extended or replaced with a machine learning model if desired.

## Deployment

### Google Cloud (App Engine or Cloud Run)

- For App Engine: create an `app.yaml` and deploy with `gcloud app deploy`.
- For Cloud Run: create a Dockerfile or use source deploy with `gcloud run deploy --source .`.
- Set the `GOOGLE_API_KEY` environment variable in your cloud environment.

### Streamlit

- Create a `streamlit_app.py` (or use `src/main.py` if compatible).
- Deploy to [Streamlit Community Cloud](https://streamlit.io/cloud) or run locally:
  ```sh
  streamlit run src/main.py
  ```

## Visualisation & Confidence

- The web interface visualises the dialogue as a flow diagram using Mermaid.js.
- Each utterance is shown with a confidence score or rationale for its classification.

## Project Structure

```
requirements.txt
transcript1.txt
src/
    API.txt
    classify.py
    main.py
    summarise.py
    unclassified_utterances.log
    static/
        style.css
    templates/
        index.html
```

- `main.py`: Entry point for running the summarisation.
- `summarise.py`: Contains the summarisation logic (uses Google Gemini for long dialogues).
- `classify.py`: Rule-based classification of utterances/dialogue acts.
- `templates/`: Contains HTML templates for the web interface.

## Security

- **API keys are never stored in the repository.**
- Users must set their own `GOOGLE_API_KEY` environment variable.
- Do not share or commit sensitive credentials.

## Customisation

- You can modify the prompt in `summarise.py` to adjust the style or detail of the summaries.
- To use a different LLM or local model, update the relevant code in `summarise.py`.

## Approach

This project combines rule-based natural language processing and large language model (LLM) summarization to analyse and summarise multi-party dialogues. Each utterance in a transcript is classified into a dialogue function (such as Proposal, Commitment, Challenge, etc.) using a set of carefully designed heuristics. For short dialogues, a narrative summary is generated using these classifications and logical rules. For longer dialogues, the system leverages Google Gemini (via the `google-generativeai` API) to produce a high-quality, context-aware summary. The web interface also visualizes the dialogue flow and provides confidence scores or rationales for each classification, supporting both transparency and interpretability.

## Contact

For questions or contributions, please open an issue or pull request on GitHub.
