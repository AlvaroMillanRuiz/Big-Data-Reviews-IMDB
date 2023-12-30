"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.18.4
"""

# Import necessary libraries
import pandas as pd
import glob

from kedro.pipeline import node
from selenium import webdriver
from selenium.webdriver.common.by import By
from ydata_profiling import ProfileReport
import numpy as np
import json
import duckdb
import string
import re
import numpy as np
from sqlalchemy import create_engine
import sqlalchemy

import sqlite3
import duckdb
import time

import pandas as pd
import numpy as np
import psycopg2
from kedro.extras.datasets.pandas import SQLTableDataSet
import pandas as pd
from ._1_data_eda_storage import *

#### General nodes not belonging to any scripts
def load_save_main(x1: pd.DataFrame,
                   x2: pd.DataFrame,
                   x3: pd.DataFrame,
                   x4: pd.DataFrame,
                   x5: pd.DataFrame,
                   x6: pd.DataFrame,
                   x7: pd.DataFrame,
                   x8: pd.DataFrame) -> pd.DataFrame:
    # Read imdb labeled train data
    imdb_review = pd.concat((file for file in [x1,x2,x3,x4,x5,x6,x7,x8]))
    return imdb_review

def load_save(df):
    return df

def scrape_movie_data():
    # Scrape first page
    driver = webdriver.Chrome('./chromedriver')
    driver.get("https://www.the-numbers.com/movie/budgets/all")
    html = driver.page_source
    df = pd.read_html(html)[0]
    next_urls = driver.find_element(By.CLASS_NAME, "pagination")
    next_page = re.findall("(.movie.+)\"", next_urls.get_attribute("outerHTML"))[1]

    # Scrape all other pages
    end_of_scraping = False

    while end_of_scraping == False:
        driver.get("https://www.the-numbers.com" + next_page)
        html = driver.page_source
        budget = pd.read_html(html)[0]
        df = df.append(budget)
        driver.find_element(By.CLASS_NAME, "pagination")
        next_urls = driver.find_element(By.CLASS_NAME, "pagination")
        s = next_urls.get_attribute("outerHTML")
        s = s[s.find('active'):]
        try:
            next_page = re.findall("(.movie.+)\"", s)[0]
        except:
            end_of_scraping = True

    # Close scraper
    driver.close()
    return df