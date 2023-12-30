import logging

import chardet
import pandas as pd
import numpy as np
import re
import unicodedata

import functions_project


def standard_data_preprocessing(data: pd.DataFrame):
    # Asserting that the length of the dataset did not change in the meantime
    beginlen = len(data)

    # Doing what you guys did
    imdb_review = data
    imdb_review = imdb_review.replace('\\N', np.nan)

    # Filling original title with primary title if NA
    imdb_review['originalTitle'] = imdb_review['originalTitle'].fillna(imdb_review['primaryTitle'])

    # Treating end year and start year
    imdb_review['endYear'] = imdb_review['endYear'].fillna(imdb_review['startYear']).astype(int)
    imdb_review['startYear'] = imdb_review['startYear'].fillna(imdb_review['endYear']).astype(int)

    # Filling NA values for runtime Minutes and numVotes (taking average by year)
    imdb_review['runtimeMinutes'] = imdb_review['runtimeMinutes'].astype(float)
    fillers = imdb_review.dropna().groupby('startYear', as_index=False)[['runtimeMinutes', 'numVotes']].mean()
    imdb_review = pd.merge(imdb_review, fillers, how='left', on='startYear', suffixes=('', "_filler"))
    imdb_review['numVotes'] = imdb_review['numVotes'].fillna(imdb_review['numVotes_filler'])
    imdb_review['numVotes'] = imdb_review['numVotes'].fillna(imdb_review['numVotes'].mean())
    imdb_review['runtimeMinutes'] = imdb_review['runtimeMinutes'].fillna(imdb_review['runtimeMinutes_filler'])
    imdb_review['runtimeMinutes'] = imdb_review['runtimeMinutes'].fillna(imdb_review['runtimeMinutes'].mean())

    # Standardizing original title and primary title (with two different standardization functions, two is better than one :-) )
    imdb_review['originalTitle'] = imdb_review['originalTitle'].apply(
        lambda val: unicodedata.normalize('NFKD', val).encode('ascii', 'ignore').decode()).str.lower()
    functions_project.map_cleaned_strings(imdb_review, 'originalTitle')
    imdb_review['primaryTitle'] = imdb_review['primaryTitle'].apply(
        lambda val: unicodedata.normalize('NFKD', val).encode('ascii', 'ignore').decode()).str.lower()
    functions_project.map_cleaned_strings(imdb_review, 'primaryTitle')

    # Dropping unused columns
    imdb_review = imdb_review.drop(columns=['Unnamed: 0', 'numVotes_filler', 'runtimeMinutes_filler'])

    # Some assertions to be sure everything went well
    assert all(imdb_review.apply(lambda x: len(x.dropna()) / len(x)) == 1), 'Empty values found after preprocessing'
    assert beginlen == len(imdb_review), 'Length differs between return and input dataset'

    return imdb_review

def dataeda_storage_director(directing):
    # Replace missing values by legit missing values
    directing = directing.replace('\\N', np.nan)
    # Remove movies with missing director (= 2 movies)
    directing = directing.dropna()

    dummie_all_director = pd.get_dummies(directing, columns=['director'])
    dummie_all_director = dummie_all_director.groupby('movie', as_index=False).sum()
    dummie_all_director = dummie_all_director.fillna(0)
    counts = dummie_all_director.drop('movie', axis=1).apply(sum, axis=0)

    # Remove directors which only produced one movie
    importants = list(counts[counts >= 2].keys()) + ['movie']
    dummie_all_director = dummie_all_director[importants]

    return dummie_all_director

def dataeda_storage_writer(movie_writer):
    # Replace missing values by legit missing values
    movie_writer = movie_writer.replace('\\N', np.nan)
    # Remove movies with missing writer (= 297 movies)
    movie_writer = movie_writer.dropna()

    dummie_all_writers = pd.get_dummies(movie_writer, columns=['writer'])
    dummie_all_writers = dummie_all_writers.groupby('movie', as_index=False).sum()
    dummie_all_writers = dummie_all_writers.fillna(0)
    counts = dummie_all_writers.drop('movie', axis=1).apply(sum, axis=0)

    # Remove directors which only produced one movie
    importants = list(counts[counts >= 2].keys()) + ['movie']
    dummie_all_writers = dummie_all_writers[importants]

    return dummie_all_writers