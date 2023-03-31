import numpy as np
from prophet.serialize import model_from_json
import os

def load_model():
    base = os.path.dirname(__file__)
    full_uri = os.path.join(base, '../../models/serialized_model.json')
    with open(full_uri, 'r') as fin:
        m = model_from_json(fin.read())  # Load model
    return m
