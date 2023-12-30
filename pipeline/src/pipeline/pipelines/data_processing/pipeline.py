"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.18.4
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import *
from ._1_data_eda_storage import *
from ._2_oscardata import *
from ._4_rating_prediction import *

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            # Load and save everything first in the database
            node(func=scrape_movie_data,
                 inputs=None,
                 outputs='budgetint',
                 name='Scrape_movie_data'),
            node(func=load_save_main,
                 inputs=['train1', 'train2', 'train3', 'train4', 'train5', 'train6', 'train7', 'train8'],
                 outputs='mainint',
                 name='Save_Main_in_DB'),
            node(func=load_save,
                 inputs='writing',
                 outputs='writersint',
                 name='Save_writers_in_DB'),
            node(func=load_save,
                 inputs='oscarsraw',
                 outputs='oscarsint',
                 name='Save_oscars_in_DB'),
            node(func=load_save,
                 inputs='directing',
                 outputs='directorsint',
                 name='Save_directors_in_DB'),
            node(func=load_save,
                 inputs='linksraw',
                 outputs='linksint',
                 name='Save_links_in_DB'),
            node(func=load_save,
                 inputs='moviesraw',
                 outputs='moviesint',
                 name='Save_movies_in_DB'),
            node(func=load_save,
                 inputs='emmysraw',
                 outputs='emmysint',
                 name='Save_emmys_in_DB'),
            node(func=load_save,
                 inputs='wikiraw',
                 outputs='wikiint',
                 name='Save_wiki_in_DB'),
            # Data EDA + Storage
            node(func=prepare_movie_data,
                 inputs='budgetint',
                 outputs='budgetprim',
                 name='Preapre_movie_data'),
            node(func=prepare_oscars,
                 inputs='oscarsint',
                 outputs='oscarsprim',
                 name='Prepare_Oscars'),
            node(func=prepare_emmys,
                 inputs='emmysint',
                 outputs='emmysprim',
                 name='Prepare_Emmys'),
            node(func=dataeda_storage_director,
                 inputs='directorsint',
                 outputs='directorsprim',
                 name='Prepare_Directors'),
            node(func=dataeda_storage_writer,
                 inputs='writersint',
                 outputs='writersprim',
                 name='Prepare_Writers'),
            node(func=prepare_wiki,
                 inputs='wikiint',
                 outputs='wikiprim',
                 name='Prepare_Wiki'),

            # Train, validation, and testset preprocessing
            node(func=standard_data_preprocessing,
                 inputs='mainint',
                 outputs='mainprim',
                 name='Prepare_MainData'),
            node(func=standard_data_preprocessing,
                 inputs='validationhiddenraw',
                 outputs='validationmodel',
                 name='Prepare_ValidationData'),
            node(func=standard_data_preprocessing,
                 inputs='testhiddenraw',
                 outputs='testmodel',
                 name='Prepare_TestData'),

            # Exploration Movielens Data + saving in DB
            # node(func=explore_movielens,
            #      inputs=['moviesint', 'linksint', 'ratingsraw'],
            #      outputs='movielensprim',
            #      name='Clean_movielens_data'),
            # Train model
            # node(
            #     func = define_columns_used,
            #     inputs = ['train', 'mainprim', "params:model_options"],
            #     outputs = ['conts', 'cats'],
            #     name='define_used_columns'
            # ),

            node(
                func=split_data,
                inputs=["train", "mainprim", 'directorsprim', 'writersprim', "oscarsprim", "emmysprim", "params:model_options"],
                outputs=["X_train", "X_test", "y_train", "y_test"],
                name="split_data"
            ),
            node(
                func=train_model,
                inputs=['X_train', 'y_train', "params:model_options"],
                outputs='mymod',
                name='train_model'
            ),
            node(
                func=evaluate_model,
                inputs=["mymod", 'X_test', 'y_test'],
                outputs='results',
                name="evaluate_model"
            ),
            node(
                func=predict_test_validation,
                inputs=['validation', 'mymod', 'validationmodel', "params:model_options"],
                outputs='predictedvalid',
                name='predict_validationset'
            ),
            node(
                func=predict_test_validation,
                inputs=['test', 'mymod', 'testmodel', "params:model_options"],
                outputs='predictedtest',
                name='predict_testset'
            )
        ]
    )