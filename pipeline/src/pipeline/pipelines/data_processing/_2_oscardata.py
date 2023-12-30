import unicodedata

import pandas as pd

import functions_project



def prepare_oscars(oscars):
    oscars['film'] = oscars['film'].astype(str)

    # Standardizing title (with two different standardization functions, two is better than one :-) )
    oscars['film'] = oscars['film'].apply(
        lambda val: unicodedata.normalize('NFKD', val).encode('ascii', 'ignore').decode()).str.lower()
    functions_project.map_cleaned_strings(oscars, 'film')

    # Taking sum of oscras
    oscars = oscars.groupby(['year_film', 'film'], as_index=False)['winner'].sum()

    return oscars

def prepare_emmys(emmys):
    emmys['nominee'] = emmys['nominee'].astype(str)

    # Standardizing title (with two different standardization functions, two is better than one :-) )
    emmys['nominee'] = emmys['nominee'].apply(
        lambda val: unicodedata.normalize('NFKD', val).encode('ascii', 'ignore').decode()).str.lower()
    functions_project.map_cleaned_strings(emmys, 'nominee')

    # taking sum again
    emmys = emmys.groupby(['year', 'nominee'], as_index=False)['win'].sum()
    return emmys

def prepare_wiki(wiki):
    # Standardizing title (with two different standardization functions, two is better than one :-) )
    wiki['Title'] = wiki['Title'].apply(
        lambda val: unicodedata.normalize('NFKD', val).encode('ascii', 'ignore').decode()).str.lower()
    functions_project.map_cleaned_strings(wiki, 'Title')

    # Variable Transformations
    wiki = wiki.groupby('Title', as_index=False).first()
    wiki = wiki[['Release Year', 'Title', 'Origin/Ethnicity', 'Genre']]
    wiki.columns = ['year', 'title', 'origin', 'genre']
    wiki['genre'] = wiki['genre'].str.split(r' ').str.get(0)
    wiki['genre'] = wiki['genre'].str.split(r'/').str.get(0)

    # Standardizing genre (with two different standardization functions, two is better than one :-) )
    wiki['genre'] = wiki['genre'].apply(
        lambda val: unicodedata.normalize('NFKD', val).encode('ascii', 'ignore').decode()).str.lower()
    functions_project.map_cleaned_strings(wiki, 'genre')

    # Getting dummies
    wiki = pd.get_dummies(wiki, columns=['origin', 'genre'])

    # Remove columns which only produced one movie
    counts = wiki.drop(['year', 'title'], axis=1).apply(sum, axis=0)
    importants = list(counts[counts >= 20].keys()) + ['year', 'title']
    wiki = wiki[importants]

    return wiki

def prepare_movie_data(df):
    # Data wrangling dataset
    budget_df = df[df['Release Date'] != 'Unknown']
    budget_df = budget_df.drop(['Unnamed: 0'], axis=1)
    budget_df['Release Date'] = pd.to_datetime(budget_df['Release Date'])
    budget_df['Release Year'] = budget_df['Release Date'].dt.year

    # Standardizing title (with two different standardization functions, two is better than one :-) )
    budget_df['Movie'] = budget_df['Movie'].apply(
        lambda val: unicodedata.normalize('NFKD', val).encode('ascii', 'ignore').decode()).str.lower()
    functions_project.map_cleaned_strings(budget_df, 'Movie')

    # Transforming budget to int
    functions_project.map_cleaned_strings(budget_df, 'Worldwide Gross')
    functions_project.map_cleaned_strings(budget_df, 'Domestic Gross')
    functions_project.map_cleaned_strings(budget_df, 'Production Budget')

    budget_df['Worldwide Gross'] = budget_df['Worldwide Gross'].astype(int)
    budget_df['Domestic Gross'] = budget_df['Domestic Gross'].astype(int)
    budget_df['Production Budget'] = budget_df['Production Budget'].astype(int)

    # Renaming
    budget_df = budget_df.rename(
        columns={"Release Date": "release_date", "Movie": "movie", "Production Budget": "production_budget",
                 "Domestic Gross": "domestic_gross", "Worldwide Gross": "worldwide_gross",
                 "Release Year": "release_year"})

    return budget_df