import re
import os


nlp = None
textcat = None

def classify_utterances(transcript):
    """
    Parses the transcript and classifies each utterance by dialogue function.
    Uses simple rule-based heuristics (can be replaced with a model).
    Returns a list of dicts: [{speaker, utterance, function}]
    """
    utterances = []
    for line in transcript.strip().split('\n'):
        match = re.match(r'^(.*?):\s+(.*)$', line)
        if not match:
            continue
        speaker, utterance = match.groups()
        function = classify_function(utterance)
        # Example: Add confidence/rationale (rule-based: always 1.0, or a short explanation)
        confidence = 1.0
        rationale = f"Classified as {function} based on keywords/rules."
        utterances.append({
            'speaker': speaker.strip(),
            'utterance': utterance.strip(),
            'function': function,
            'confidence': confidence,
            'rationale': rationale
        })
    return utterances

def classify_function_with_confidence(utterance):
    # Only rule-based logic, no spaCy model
    function = classify_function(utterance)
    return function, None

def classify_function(utterance):

    """
    Rule-based dialogue function classifier.
    Enhanced rule-based logic for more realistic/accurate fallback.
    Flags utterances that fall to the default 'Statement' label for review.
    """
    utt = utterance.lower().strip()
    # --- Enhanced rules ---
    if not utt:
        return 'Statement'
    # Questions, queries and Requests
    if utt.endswith('?'):
        if any(q in utt for q in ['can you', 'could you', 'would you', 'will you', 'shall we', 'please', 'would it be possible']):
            return 'Request'
        if any(q in utt for q in ['why', 'what', 'how', 'when', 'where', 'who', 'is it', 'are you', 'do you', 'does it', 'can it', 'could it', 'would it', 'will it', 'shall we', 'may I', 'might I']):
            return 'Question'
        return 'Query'
    # Commitment (ensure this check comes before Disagreement and Agreement)
    negative_starts = [
        "i'm not", "i am not", "i will not", "i won't", "i can't", "i shouldn't", "i couldn't", "i wouldn't", "i might", "i may", "i hope", "i plan", "i want", "i wish", "i would like", "i intend", "i expect", "i think", "i don't", "i guess", "i suppose", "i doubt", "i wonder"
    ]
    if not any(neg in utt for neg in negative_starts):
        commitment_phrases = [
            "i'm", "i am", "i will", "i'll", "i shall", "we will", "we'll", "we shall", "i can",
            "i'll handle", "i'll take", "i'll do", "i'll get", "i'll make", "i'll see", "i'll ensure",
            "i'll address", "i'll manage", "i'll finish", "i'll update", "i'll confirm", "i'll follow",
            "i'll complete", "i'll work", "i'll start", "i'll lead", "i'll get started", "i'll get that",
            "i'll make sure", "i'll take care", "i'll see to it", "i'll follow through", "i'll address it soon",
            "i'll get started now", "i'll finish it soon", "i'll take the lead", "i'll update you",
            "i'll confirm when finished", "i'll prepare", "i'll prepare a status update", "fair enough", "i'll help",
            "we can", "we'll handle", "we'll take", "we'll do", "we'll get", "we'll make", "we'll see", "we'll ensure",
            "we'll address", "we'll manage", "we'll finish", "we'll update", "we'll confirm", "we'll follow",
            "we'll complete", "we'll work", "we'll start", "we'll lead", "we'll get started", "we'll get that",
            "we'll make sure", "we'll take care", "we'll see to it", "we'll follow through", "we'll address it soon",
            "we'll get started now", "we'll finish it soon", "we'll take the lead", "we'll update you",
            "we'll confirm when finished", "we'll prepare", "we'll prepare a status update", "we'll help"
            
        ]
        for phrase in commitment_phrases:
            if phrase in utt:
                return 'Commitment'
    # Proposal
    proposal_phrases = [
        "how about", "let's", "maybe we could", "i propose", "shall we", "i suggest", "why don't we", "perhaps we should", 
        "i recommend", "let us", "i'd like to propose", "i'd suggest", "i'd recommend", "i think we should", "maybe we hold off", 
        "maybe we should", "then maybe we", "i think we could", "i think we can", "i think we might", "i think we may",
        "i think we shall", "i think we will", "i think we ought to", "i think we need to", "i think we have to", "i think we must"
    ]
    if any(phrase in utt for phrase in proposal_phrases):
        return 'Proposal'
    # Deferral
    deferral_phrases = [
        "not yet", "on the roadmap", "let's come back", "we can discuss this next time", "let's postpone", "we'll revisit", 
        "let's defer", "we'll talk about this later", "let's address this in the future", "we'll handle this next time", 
        "let's leave this for now", "we'll return to this", "let's put this on hold", "we'll get back to this", "let's delay this", 
        "we'll pick this up later", "let's save this for later", "we'll continue this later", "let's revisit this", "we'll postpone this", 
        "let's discuss this later", "we'll come back to this"
    ]
    if any(phrase in utt for phrase in deferral_phrases):
        return 'Deferral'
    # Challenge
    challenge_phrases = [
        "are you sure", "can you prove", "is that really", "can you back that up", "are you certain", "can you show proof", 
        "is that correct", "can you demonstrate", "are you positive", "can you verify", "is that true", "can you confirm", 
        "can you justify", "is there evidence", "can you support", "is that verifiable", "can you show evidence", "is that provable", 
        "i'd like to see evidence", "is that accurate", "is that right", "is that the case", "is that so", "is that confirmed", 
        "is that valid", "is that supported"
    ]
    if any(phrase in utt for phrase in challenge_phrases):
        return 'Challenge'
    # Justification
    justification_phrases = [
        "because", "the reason", "due to", "as a result", "since", "that's why", "the cause", "the explanation", "the rationale", 
        "the logic", "the basis", "the underlying reason", "the consequence", "the result", "the explanation is", "the reason is", 
        "it's because", "it's due to", "it's a result of", "it's a consequence of", "it's the result of", "it's the cause of", 
        "it's the reason for", "true, but", "the latest version uses"
    ]
    if any(phrase in utt for phrase in justification_phrases):
        return 'Justification'
    # Thanking
    thanking_phrases = [
        "thank", "thanks", "appreciate", "grateful", "gratitude", "much obliged", "owe you", "sincere thanks", "greatly appreciated", 
        "immense thanks", "heartfelt thanks", "endless gratitude", "really appreciate", "thanks a ton", "thanks a million", 
        "thank you for your time", "thanks again", "i owe you one"
    ]
    if any(phrase in utt for phrase in thanking_phrases):
        return 'Thanking'
    # Apology
    apology_phrases = [
        "sorry", "apolog", "pardon", "my apologies", "i apologize", "forgive me", "i didn't mean", "regret", "my fault", "my mistake", 
        "inconvenience", "trouble", "oversight", "delay", "mix-up", "take responsibility"
    ]
    if any(phrase in utt for phrase in apology_phrases):
        return 'Apology'
    # Greeting
    greeting_phrases = [
        "hi", "hello", "good morning", "good afternoon", "good evening", "hey", "greetings", "welcome", "salutations", "nice to see you", 
        "pleased to meet you", "how are you", "how's it going", "yo", "what's up", "hi all", "hi team", "hi everyone", "hi folks", "hi buddy", 
        "hi friend", "hi pal", "hi fam", "hi again", "hello mate", "hello again", "hello folks", "hello team", "hello everyone", "hello all", 
        "hello friend", "hello pal", "hello fam", "good to see you", "good day", "good night"
    ]
    if any(phrase in utt for phrase in greeting_phrases):
        return 'Greeting'
    # Closing
    closing_phrases = [
        "goodbye", "bye", "see you", "take care", "farewell", "catch you later", "see you soon", "see you around", "until next time", 
        "later", "goodbye for now", "see you later", "all the best", "bye for now", "take it easy", "see you tomorrow", "goodbye everyone", 
        "have a good one", "see you then"
    ]
    if any(phrase in utt for phrase in closing_phrases):
        return 'Closing'
    # Agreement
    agreement_phrases = [
        "i agree", "that makes sense", "absolutely", "i think you're right", "i support that", "i'm with you", "i concur", "that's true", 
        "i believe so", "i'm in agreement", "i share your view", "i agree completely", "that's correct", "i agree 100%", "i'm on board", 
        "i agree wholeheartedly", "that's my view too", "i see it the same way", "i agree entirely", "i'm in full agreement", "sure", 
        "of course", "definitely", "yes"
    ]
    if any(phrase in utt for phrase in agreement_phrases):
        return 'Agreement'
    # Disagreement 
    disagreement_phrases = [
        "i'm not convinced", "i don't think", "i see it differently", "i'm not sure i agree", "i have a different opinion", "i disagree", 
        "that's not how i see it", "i can't agree", "i don't share that view", "i beg to differ", "that's not my understanding", 
        "i see things another way", "i don't believe that's right", "i have to disagree", "i respectfully disagree", "that's not accurate", 
        "i don't think that's the case", "i don't see it that way", "i must disagree", "i can't support that", "no", "not really", "unfortunately"
    ]
    if any(phrase in utt for phrase in disagreement_phrases):
        return 'Disagreement'
    # Acknowledgement
    acknowledgement_phrases = [
        "okay", "ok", "alright", "got it", "understood", "noted", "i see", "thanks for letting me know", "i understand", "alright, thanks", 
        "okay, got it", "i acknowledge", "alright, noted", "okay, understood", "i got it", "alright, i see", "okay, i understand", "alright, got it", 
        "okay, thanks for the info", "i see, thanks"
    ]
    if any(phrase in utt for phrase in acknowledgement_phrases):
        return 'Acknowledgement'
    # Inform
    inform_phrases = [
        "i think", "i believe", "let me", "the reason", "because", "just to let you know", "for your information", "fyi", "just so you know", 
        "this is to inform you", "just a heads up", "please be aware", "i thought you should know", "for your awareness", "just making you aware", 
        "i wanted to inform you", "just to keep you posted", "for your reference", "just to update you", "i wanted to update you", "just to notify you", 
        "for your records", "just to keep you informed"
    ]
    if any(phrase in utt for phrase in inform_phrases):
        return 'Inform'
    # Statement (default)
    # Log or flag utterances that fall to default for review
    if utt:
        with open(os.path.join(os.path.dirname(__file__), 'unclassified_utterances.log'), 'a', encoding='utf-8') as logf:
            logf.write(f"[DEFAULT Statement] {utterance}\n")
    return 'Statement'