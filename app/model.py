import xgboost as xgb
import numpy as np

# Adapter le chemin du modèle selon le contexte
MODEL_PATH = "model.xgb"

booster = xgb.Booster()
booster.load_model(MODEL_PATH)


def predict_attrition(features_dict):
    features_array = np.array([list(features_dict.values())])
    dmatrix = xgb.DMatrix(features_array)
    pred = booster.predict(dmatrix)[0]
    return float(pred)
