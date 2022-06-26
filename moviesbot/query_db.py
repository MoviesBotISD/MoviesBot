"""Functions to look for movies that suit the filters in answer.json
"""
import pandas as pd
from difflib import SequenceMatcher
# #Import TfIdfVectorizer from scikit-learn
# from sklearn.feature_extraction.text import TfidfVectorizer
# # Import linear_kernel
# from sklearn.metrics.pairwise import linear_kernel

# #Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
# tfidf = TfidfVectorizer(stop_words='english')
# #Replace NaN with an empty string
# df2['overview'] = df2['overview'].fillna('')
# #Construct the required TF-IDF matrix by fitting and transforming the data
# tfidf_matrix = tfidf.fit_transform(df2['overview'])
# # Compute the cosine similarity matrix
# cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
# #Construct a reverse map of indices and movie titles
# indices = pd.Series(df2.index, index=df2['title']).drop_duplicates()

df = pd.read_csv("data/movies.csv")

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_recommendations(title, cosine_sim=None):#cosine_sim):
    # # Get the index of the movie that matches the title
    # idx = indices[title]
    # # Get the pairwsie similarity scores of all movies with that movie
    # sim_scores = list(enumerate(cosine_sim[idx]))
    # # Sort the movies based on the similarity scores
    # sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # # Get the scores of the 10 most similar movies
    # sim_scores = sim_scores[1:11]
    # # Get the movie indices
    # movie_indices = [i[0] for i in sim_scores]
    # # Return the top 10 most similar movies
    # return df['title'].iloc[movie_indices]
    pass

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

def isEmpty(answer):
    return (answer["title"] == "" and
            answer["actor"] == "" and
            answer["director"] == "" and
            answer["language"] == "" and
            answer["description"] == "")

def query_db(answer_json):
    answer = answer_json['answer']
    dfn = pd.DataFrame(columns=df.columns)
    if isEmpty(answer):
        movies_list = str(df.iloc[:3].values.tolist())
        return movies_list
    if (answer['title'] != ''):
        movies_list = str(get_recommendations(answer['title']).values.tolist())
        return movies_list
    if (answer['actor'] != ''):
        act = get_actor_similar(answer['actor'])
        dfn= df[[ act in l for l in df["cast"]]] 
    if (answer['director'] != ''):
        dirct = get_director_similar(answer['director'])
        dfn = dfn.query("director == @dirct")
    dfn.sort_values(by=['runtime'])
    s = dfn.shape[0]
    if (answer['duration']=="short"):
        df_results = dfn[['tittle', 'homepage']][:s//2]
        movies_list = str(df_results.values.tolist())
        return movies_list
    df_results = dfn[['tittle', 'homepage']][s//2:]
    movies_list = str(df_results.values.tolist())
    return movies_list