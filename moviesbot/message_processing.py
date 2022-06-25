"""Module to process messages recieved by messegner chatbox
"""
from pdb import pm
import spacy
try:
    spacy.load("en_core_web_md")
except: # If not present, we download
    spacy.cli.download("en_core_web_md")
from . import utils as utl
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from statistics import mean

def create_next_message(step, message):
    next_message = ""
    if step == 0:
        next_message = ("Hello, I am MoviesBot :D, I can help you find a good movie according to you mood and likes!\n"
                "How are you feeling today ?")
        return next_message, True
    elif step == 1:
        sentences = sent_tokenize(message)
        avg_sentiment_score = compute_sentiment(sentences)
        answer_json = utl.read_json("../data/answer.json")
        answer_json['answer']['mood'] = avg_sentiment_score
        utl.write_json("../data/answer.json", answer_json)
        # if there is a sentence where he asks back, we answer him first before asking the next question
        if is_how_are_you(sentences):
            next_message = "I am doing great 😁, thanks for asking!\n"
        else:
            next_message = ""
        next_message += ''.join(("Can you give me the name of a movie for which I can suggest you similar ones?\n",
                        "if not, you can type 'skip'"))
        return next_message, True
    elif step == 2:
        if message.strip().lower() == "skip":
            next_message = "Ok, is there a specific actor you want to see in the movie ?\nif not, you can type 'skip'"
            return next_message, True
        else:
            nlp = spacy.load("en_core_web_md")
            pmessage = nlp(message)
            [(t.text, t.label_) for t in pmessage.ents]

    elif step == 3:
        if message.strip().lower() == "skip":
            next_message = "Got it, any specific director in your mind?\nif not, you can type 'skip'"
            return next_message, True
        else:
            nlp = spacy.load("en_core_web_md")
            pmessage = nlp(message)
            actor_name = ""
            for t in pmessage.ents:
                if t.label_ == "PERSON":
                    answer_json = utl.read_json("../data/answer.json")
                    actor_name = "".join(t.text.strip().lower().split())
                    answer_json['answer']['actor'] = actor_name
                    utl.write_json("../data/answer.json", answer_json)
            if actor_name == "":
                next_message = "Sorry, I did not understand that :/ can you repeat please?"
                return next_message, False
            else:
                next_message = "Got it, any specific director in your mind?\nif not, you can type 'skip'"
                return next_message, True
    elif step == 4:
        pass
    elif step == 5:
        pass
    elif step == 6:
        pass

def compute_sentiment(sentences):
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = [sia.polarity_scores(sentence)["compound"] for sentence in sentences]
    avg_sentiment_score = mean(sentiment_scores)
    return avg_sentiment_score

def is_how_are_you(sentences):
    nlp = spacy.load("en_core_web_md")
    questions = ["how are you?", "and you?", "what about you?", "you?", "how are you doing?", "how are you feeling?"]
    for sentence in sentences:
        for qst_form in questions:
            if nlp(sentence).similarity(nlp(qst_form)) > 0.9:
                return True
            else:
                return False
