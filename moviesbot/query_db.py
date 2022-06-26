"""Functions to look for movies that suit the filters in answer.json
"""
import pandas as pd
from difflib import SequenceMatcher

df = pd.read_csv("data/clean_movies.csv")

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_director_similar(director) :
    max_sim = 0
    for t in df["director"]: 
        if similar(str(t),str(director)) > max_sim : 
            max_sim = similar(str(t),str(director))
            res = str(t)
    return res

def get_actor_similar(name):
    max_sim = 0
    for l in df["cast"] : 
        for n in l : 
            if similar(n,name) > max_sim: 
                max_sim = similar(n,name)
                res = n
    return res

def query_db(answer_json):
    answer = answer_json['answer']
    dfn = pd.DataFrame(columns=df.columns)
    if (answer['actor'] != ''):
        act = get_actor_similar(answer['actor'])
        dfn= df[[ act in l for l in df["cast"]]] 
    if (answer['director'] != ''):
        dirct = get_director_similar(answer['director'])
        d2= dfn.query("director == @dirct")
    d2.sort_values(by=['runtime'])
    s=d2.shape[0]
    if (answer['duration']=="short"):
        return d2[['tittle', 'homepage']][:s//2]
    return d2[['tittle', 'homepage']][s//2:]