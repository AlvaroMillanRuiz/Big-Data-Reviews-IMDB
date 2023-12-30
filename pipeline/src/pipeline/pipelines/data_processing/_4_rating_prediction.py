import logging

import duckdb
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.feature_selection import SelectPercentile, chi2
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import confusion_matrix, r2_score, accuracy_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
import logging
from typing import Dict, Tuple

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from kedro.config import ConfigLoader
from kedro.framework.project import settings
from sklearn.pipeline import make_union, make_pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.base import BaseEstimator
from sklearn.base import TransformerMixin

def define_columns_used(data, x1, parameters):
    writers = list(data.filter(like="writer_", axis=1).columns)
    directors = list(data.filter(like='director_', axis=1).columns)
    conts = parameters['features_continuous']
    cats = writers + directors

    print('Columns used')
    print(conts)
    print(cats)

    return conts, cats

def split_data(data, x, x2, x3, x4, x5, parameters):
    """Splits data into features and targets training and test sets.

    Args:
        data: Data containing features and target.
        parameters: Parameters defined in parameters/data_science.yml.
    Returns:
        Split data.
    """
    data = data.fillna(-1)
    X = data.drop('label', axis=1)
    y = data["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=parameters["test_size"], random_state=parameters["random_state"]
    )
    print('XTrain shape:', X.shape)
    return X_train, X_test, y_train, y_test

def train_model(X_train: pd.DataFrame, y_train: pd.Series, parameters):
    """Trains the sklearn based model.

    Args:
        X_train: Training data of independent features.
        y_train: Training data for price.

    Returns:
        Trained model.
    """
    # Transformers

    writers = list(X_train.filter(like='writer_').columns)
    directors = list(X_train.filter(like='director_').columns)
    genre = list(X_train.filter(like='genre_').columns)
    origin = list(X_train.filter(like='origin_').columns)
    conts = ['endYear', 'yeardif', 'runtimeMinutes', 'numVotes', 'winner', 'emmys', 'domestic_gross',
             'worldwide_gross']

    varss = writers + directors + genre + origin + conts

    assert all(X_train[writers+directors+genre+origin+conts].dtypes != 'object'), 'There are object columns in the dataset. Please drop or replace'
    assert len(writers) > 100, f'Writers not long enough: {writers}'
    assert len(directors) > 100, f'Directors not long enough: {directors}'
    assert len(genre) > 10, 'genre not long enough'
    assert len(origin) > 3, 'origin not long enough'

    preprocessor = Pipeline([
        ("selector", ColumnTransformer([
            ("selector", "passthrough", varss)
        ], remainder="drop"))
    ])

    # the optimisation parameters for each of the above models
    params = {
            'classifier__n_estimators': [300, 500, 700],
            'classifier__max_depth': [3, 5, 7],
            'classifier__min_samples_split': [15, 25, 50],
            'classifier__max_features': [0.1, 0.4, 0.8]
        }

    est = GradientBoostingClassifier()
    clf = Pipeline(
        steps=[("preprocessor", preprocessor), ("classifier", est)]
    )

    if parameters['debugging'] == True:
        params = {'classifier__max_depth': [3, 5, 7]}

    clfcv = GridSearchCV(estimator=clf, param_grid=params, cv=4, verbose=3, scoring='accuracy', n_jobs=-1)
    clfcv.fit(X_train, y_train.values.ravel())
    print(clfcv.best_params_)
    return clfcv

def predict_test_validation(df_test, clf, x, parameters):
    df_test = df_test.fillna(-1)

    predictions_test = clf.predict(df_test)

    test_end = predictions_test.astype(bool)  # Transform integer to boolean
    test_end = pd.DataFrame(test_end)

    # Checking that the length of validation and testsets are correct
    assert len(df_test) in [955, 1086], 'Length of validation or test datasets not correct'

    return test_end

def evaluate_model(
    mymodel, X_test: pd.DataFrame, y_test: pd.Series
):
    """Calculates and logs the coefficient of determination.

    Args:
        mymodel: Trained model.
        X_test: Testing data of independent features.
        y_test: Testing data for price.
    """

    y_pred = mymodel.predict(X_test)
    TN, FP, FN, TP = confusion_matrix(y_test, y_pred).ravel()

    print(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)

    print('Accuracy  = ', accuracy)
    print('True Positive(TP)  = ', TP)
    print('False Positive(FP) = ', FP)
    print('True Negative(TN)  = ', TN)
    print('False Negative(FN) = ', FN)

    return pd.DataFrame(confusion_matrix(y_test, y_pred))

