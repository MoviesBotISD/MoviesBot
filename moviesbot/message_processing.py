"""Module to process messages recieved by messegner chatbox
"""
import spacy
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from statistics import mean

def create_question(step, message):
    if step == 0:
        return "Hello, I am MoviesBot :D, I can help you find a good movie according to you mood and likes!\n\
            How are you feeling today ?"
    elif step == 1:
        sia = SentimentIntensityAnalyzer()
        sentences = sent_tokenize(message)
        sentiment_scores = [sia.polarity_scores(sentence)["compound"] for sentence in sentences]
        avg_sentiment_score = mean(sentiment_scores)
        try:
            nlp = spacy.load("en_core_web_md")
        except: # If not present, we download
            spacy.cli.download("en_core_web_md")
            nlp = spacy.load("en_core_web_md")
        questions = ["how are you?", "and you?", "what about you?", "you?", "how are you doing?", "how are you feeling?"]
        for sentence in sentences:
            for qst_form in questions:
                if nlp(sentence).similarity(nlp(qst_form)) > 0.9:
                    return "I am doing very good, thank you so much!"

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

def detect_mood(message):
    pass