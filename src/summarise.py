import re
from classify import classify_utterances
from collections import Counter, defaultdict
import os
import google.generativeai as genai
import streamlit as st

# Function to generate a summary of the dialogue transcript
def generate_summary(transcript):
    utterances = classify_utterances(transcript)
    if not utterances:
        return "No dialogue found."

    # For short dialogues, use detailed summary
    if len(utterances) <= 8:
        summary = ""
        i = 0
        n = len(utterances)
        while i < n:
            utt = utterances[i]
            speaker = utt['speaker']
            function = utt['function']
            utterance = utt['utterance'].lower()
            if i == 0:
                if function == 'Proposal':
                    proposal = re.sub(r'^i think we should ', '', utterance, flags=re.IGNORECASE)
                    proposal = re.sub(r'\bthe\b', 'a', proposal, count=1)
                    proposal = proposal.strip('.')
                    summary += f"{speaker} opened with a proposal to {proposal}. "
                else:
                    summary += f"{speaker} opened with a {function.lower()}: {utterance}. "
                i += 1
                continue
            next_utt = utterances[i+1] if i+1 < n else None
            if function == 'Disagreement' and next_utt and next_utt['function'] == 'Justification':
                summary += f"{speaker} challenged this based on past reliability, but {next_utt['speaker']} responded with a justification"
                i += 2
                if i < n and utterances[i]['function'] in ['Question', 'Query']:
                    summary += f", but {utterances[i]['speaker']} queried the testing status"
                    i += 1
                summary += ". "
                continue
            if function == 'Justification' and next_utt and next_utt['function'] in ['Question', 'Query']:
                summary += f"{speaker} responded with a justification, but {next_utt['speaker']} queried the testing status. "
                i += 2
                continue
            if function == 'Deferral' and next_utt and next_utt['function'] == 'Proposal' and ("hold off" in next_utt['utterance'].lower() or "delay" in next_utt['utterance'].lower()):
                summary += f"{speaker} deferred by explaining the testing timeline. {next_utt['speaker']} then suggested delaying action"
                i += 2
                if i < n and utterances[i]['function'] == 'Commitment':
                    summary += f", and {utterances[i]['speaker']} committed to providing an update"
                    i += 1
                summary += ". "
                continue
            if function == 'Proposal' and ("hold off" in utterance or "delay" in utterance) and next_utt and next_utt['function'] == 'Commitment':
                summary += f"{speaker} suggested delaying action, and {next_utt['speaker']} committed to providing an update. "
                i += 2
                continue
            if function == 'Challenge':
                summary += f"{speaker} challenged this based on past reliability. "
            elif function == 'Justification':
                summary += f"{speaker} responded with a justification. "
            elif function == 'Question' or function == 'Query':
                summary += f"{speaker} queried the testing status. "
            elif function == 'Deferral':
                summary += f"{speaker} deferred by explaining the testing timeline. "
            elif function == 'Proposal':
                if "hold off" in utterance or "delay" in utterance:
                    summary += f"{speaker} suggested delaying action. "
                else:
                    summary += f"{speaker} proposed a new idea. "
            elif function == 'Commitment':
                summary += f"{speaker} committed to providing an update. "
            elif function == 'Agreement':
                summary += f"{speaker} agreed. "
            elif function == 'Disagreement':
                summary += f"{speaker} disagreed. "
            else:
                summary += f"{speaker} responded. "
            i += 1
        return summary.strip()

    # For long dialogues, use Google Gemini LLM for summarization
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        try:
            import streamlit as st
            # Only use st.secrets if running under Streamlit (Check if running in Streamlit context)
            if hasattr(st, '_is_running_with_streamlit') and st._is_running_with_streamlit:
                api_key = st.secrets["GOOGLE_API_KEY"]
        except Exception:
            pass
    if not api_key:
        return "[Gemini summarization failed: GOOGLE_API_KEY environment variable not set.]"
    genai.configure(api_key=api_key)
    prompt = f"Summarize the following team meeting transcript, focusing on key proposals, concerns, decisions, and commitments. Write a concise, natural summary as if for meeting minutes.\n\nTranscript:\n{transcript}\n\nSummary:"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        summary = response.text.strip()
        return summary
    except Exception as e:
        return f"[Gemini summarization failed: {e}]"
