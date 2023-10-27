from peewee import *
from typing import List
import peewee
import inspect
import sys
import argparse

import datatables


def get_models(module) -> list:
    models = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, peewee.Model) and name != 'Model':
            model_name = f"<Model: {name}>"
            #print(model_name, obj)
            models.append(obj)
    return models


def find_model(models, table_name: str):
    table = None
    models = models
    for i in range(len(models)):
        if models[i].__name__ == table_name:
            table = models[i]
            return table
    return None



models = get_models(datatables)
datatables.global_database.connect()
for i in models:
    i.drop_table()
datatables.global_database.close()
