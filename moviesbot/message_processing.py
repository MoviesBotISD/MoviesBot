"""Module to process messages recieved by messegner chatbox
"""
import spacy
from . import utils as utl
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from statistics import mean

def create_next_message(step, message):
    next_message = ""
    if step == 0:
        next_message = ("Hello, I am MoviesBot :D, I can help you find a good movie according to you mood and likes!\n"
                "How are you feeling today ?")
        return next_message
    elif step == 1:
        sentences = sent_tokenize(message)
        avg_sentiment_score = compute_sentiment(sentences)
        answer_json = utl.read_json("data/answer.json")
        answer_json['answer']['mood'] = avg_sentiment_score
        utl.write_json("data/answer.json", answer_json)
        # if there is a sentence where he asks back, we answer him first before asking the next question
        if is_how_are_you(sentences):
            next_message = "I am doing great 😁, thanks for asking!\n"
        else:
            next_message = ""
        next_message += ("Can you give me the name of a movie for which I can suggest you similar ones?\n",
                        "if not, you can enter 'skip'")
        return next_message
    elif step == 2:
        pass
    elif step == 3:
        pass
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
    try:
        nlp = spacy.load("en_core_web_md")
    except: # If not present, we download
        spacy.cli.download("en_core_web_md")
        nlp = spacy.load("en_core_web_md")
    questions = ["how are you?", "and you?", "what about you?", "you?", "how are you doing?", "how are you feeling?"]
    for sentence in sentences:
        for qst_form in questions:
            if nlp(sentence).similarity(nlp(qst_form)) > 0.9:
                return True
            else:
                return False
