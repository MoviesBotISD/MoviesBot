"""Module to process messages recieved by messegner chatbox
"""
import pandas as pd
import spacy
from . import utils as utl
from . import query_db
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from statistics import mean
from ast import literal_eval
from difflib import SequenceMatcher

def create_next_message(step, message):
    if step == 0:
        next_message = ("Hello, I am MoviesBot :D, I can help you find a good movie according to you mood and likes!\n"
                "How are you feeling today ?")
        return (next_message, True, False) # (next_message, advance, stop)
    elif step == 1:
        return mood_processing(message)
    elif step == 2:
        if message.strip().lower() == "skip":
            next_message = "Ok, is there a specific actor you want to see in the movie ?\nif not, you can type 'skip'"
            return (next_message, True, False)
        else:
            closest_title = title_processing(message)
            if not closest_title:
                next_message = "Sorry, I don't know the movies title you have written :/\n"
                next_message += "is there a specific actor you want to see in the movie ?\nif not, you can type 'skip'"
                return (next_message, True, False)
            else:
                next_message = f"These are the most similar movies to '{closest_title}' :\n"
                answer_json = utl.read_json("data/answer.json")
                movies_list = query_db.query_db(answer_json)
                next_message += movies_list
                return (next_message, True, True)
    elif step == 3:
        next_message = "Got it, any specific director in your mind?\nif not, you can type 'skip'"
        if message.strip().lower() == "skip":
            return (next_message, True, False)
        else:
            nlp = spacy_load_corpus()
            (next_message, advance, stop) = person_name_processing(message, next_message, nlp, 'actor')
            del nlp
            return (next_message, advance, stop)
    elif step == 4:
        next_message = "I see, do you have a preference for the spoken language in the movie\nif not, you can type 'skip'"
        if message.strip().lower() == "skip":
            return (next_message, True, False)
        else:
            nlp = spacy_load_corpus()
            (next_message, advance, stop) = person_name_processing(message, next_message, nlp, 'director')
            del nlp
            return (next_message, advance, stop)
    elif step == 5:
        next_message = ''.join(("Thank you! What about the duration? Do you want a short or a long movie?\n",
                        "if you have no preference, you can type 'skip'"))
        if message.strip().lower() == "skip":
            return (next_message, True, False)
        else:
            nlp = spacy_load_corpus()
            (next_message, advance, stop) = language_processing(message, next_message, nlp)
            del nlp
            return (next_message, advance, stop)
    elif step == 6:
        next_message = ''.join(("Perfect. If there is anything you want to add about the movie, feel free to write it\n",
                        "if not, you can type 'skip'"))
        if message.strip().lower() == "skip":
            return (next_message, True, False)
        else:
            nlp = spacy_load_corpus()
            (next_message, advance, stop) = duration_processing(message, next_message, nlp)
            del nlp
            return (next_message, advance, stop)
    elif step == 7:
        next_message = "These are the best movies for you :D :\n"
        if message.strip().lower() != "skip":
            keywords_processing(message)
        answer_json = utl.read_json("data/answer.json")
        movies_list = query_db.query_db(answer_json)
        next_message += movies_list
        return (next_message, True, True)

def mood_processing(message):
    sentences = sent_tokenize(message)
    avg_sentiment_score = compute_sentiment(sentences)
    answer_json = utl.read_json("data/answer.json")
    answer_json['answer']['mood'] = avg_sentiment_score
    utl.write_json("data/answer.json", answer_json)
    # if there is a sentence where he asks back, we answer him first before asking the next question
    nlp = spacy_load_corpus()
    next_message = answer_side_questions(sentences, nlp)
    next_message += ''.join(("can you give me the name of a movie for which I can suggest you similar ones?\n",
                    "if not, you can type 'skip'"))
    return (next_message, True, False)

def title_processing(message):
    sentences = sent_tokenize(message)
    df = pd.read_csv("data/clean_movies.csv")
    closest_title = df["title"][0]
    highest_similarity = 0
    for sentence in sentences:
        sim = SequenceMatcher(None, sentence, closest_title).ratio()
        if sim > highest_similarity:
            highest_similarity = sim
    for title in df["title"]:
        for sentence in sentences:
            sim = SequenceMatcher(None, sentence, title).ratio()
            if sim > highest_similarity:
                highest_similarity = sim
                closest_title = title
    del df
    if highest_similarity < 0.5:
        return None
    else:
        answer_json = utl.read_json("data/answer.json")
        answer_json['answer']['title'] = closest_title
        utl.write_json("data/answer.json", answer_json)
        return closest_title

def person_name_processing(message, next_message, nlp, role):
    sentences = sent_tokenize(message)
    pmessage = nlp(message)
    person_name = ""
    for t in pmessage.ents:
        if t.label_ == "PERSON":
            answer_json = utl.read_json("data/answer.json")
            person_name = "".join(t.text.strip().lower().split())
            answer_json['answer'][role] = person_name
            utl.write_json("data/answer.json", answer_json)
    if person_name == "":
        next_message = answer_side_questions(sentences, nlp)
        next_message += "sorry, I did not understand your answer to my question :/ can you repeat please?"
        return (next_message, False, False)
    else:
        return (next_message, True, False)

def language_processing(message, next_message, nlp):
    sentences = sent_tokenize(message)
    message = message.lower() # because the language does not require upper or lower case
    pmessage = nlp(message)
    language = ""
    for t in pmessage.ents:
        if t.label_ == "LANGUAGE":
            answer_json = utl.read_json("data/answer.json")
            language = t.text
            answer_json['answer']['language'] = language
            utl.write_json("data/answer.json", answer_json)
    if language == "":
        next_message = answer_side_questions(sentences, nlp)
        next_message += "sorry, I did not understand your answer to my question :/ can you repeat please?"
        return (next_message, False, False)
    else:
        return (next_message, True, False)

def duration_processing(message, next_message, nlp):
    sentences = sent_tokenize(message)
    pmessage = nlp(message)
    adj = []
    time = []
    cardinal = []
    for t in pmessage.ents:
        if t.label_ == "TIME":
            time.append(t.text.strip().lower())
        if t.label_ == "CARDINAL":
            cardinal.append(t.text.strip().lower())
    for t in pmessage:
        if t.pos_ == "ADJ":
            adj.append(t.text.strip().lower())
    is_short = any(a.strip().lower() == "short" for a in adj)
    is_long = any(a.strip().lower() == "long" for a in adj)
    if not time and not cardinal and not is_short and not is_long:
        next_message += answer_side_questions(sentences, nlp)
        next_message += "sorry, I did not understand your answer to my question :/ can you repeat please?"
        return (next_message, False, False)
    if not is_short and not is_long:
        for t in time.extend(cardinal):
            if (any(word in t for word in ["hour", "h", "hours", "heure", "heures"]) and
                any(word in t for word in ["more", ">", "above"])):
                is_long = True
                is_short = False
            else:
                is_long = False
                is_short = True
    answer_json = utl.read_json("data/answer.json")
    if is_short:
        answer_json['answer']['duration'] = "short"
    else:
        answer_json['answer']['duration'] = "long"
    utl.write_json("data/answer.json", answer_json)
    return (next_message, True, False)

def keywords_processing(message):
    keywords = []
    df = pd.read_csv("data/clean_movies.csv")
    kw_lists = df["keywords"].apply(literal_eval)
    del df
    kw_set = set()
    def aux(i):
        for x in i:
            kw_set.add(x)
    kw_lists.apply(aux)
    del kw_lists
    message = message.lower()
    for w in message.split():
        if w in kw_set:
            keywords.append(w)
    answer_json = utl.read_json("data/answer.json")
    answer_json['answer']['keywords'] = keywords
    utl.write_json("data/answer.json", answer_json)

def compute_sentiment(sentences):
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = [sia.polarity_scores(sentence)["compound"] for sentence in sentences]
    del sia
    avg_sentiment_score = mean(sentiment_scores)
    return avg_sentiment_score

def answer_side_questions(sentences, nlp):
    next_message = ""
    if is_what_is_your_name(sentences, nlp):
        next_message += "My name is MoviesBot 🤖 it's always a pleasure to suggest you great movies 🎞!\nand "
    if is_how_are_you(sentences, nlp):
        next_message += "I am doing great 😁, thanks for asking!\nand "
    return next_message

def is_how_are_you(sentences, nlp):
    questions = ["how are you ?", "and you ?", "what about you ?", "you ?", "how are you doing ?", "how are you feeling ?"]
    for sentence in sentences:
        for qst_form in questions:
            if nlp(sentence).similarity(nlp(qst_form)) > 0.97:
                return True
            else:
                return False

def is_what_is_your_name(sentences, nlp):
    questions = ["what is your name ?", "tell me your name", "remind me of your name", "your name ?"]
    for sentence in sentences:
        for qst_form in questions:
            if nlp(sentence).similarity(nlp(qst_form)) > 0.97:
                return True
            else:
                return False

def spacy_load_corpus():
    try:
        nlp = spacy.load("en_core_web_md")
    except: # If not present, we download
        spacy.cli.download("en_core_web_md")
        nlp = spacy.load("en_core_web_md")
    return nlp