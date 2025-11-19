import shap
import numpy as np
import base64
import io
import matplotlib.pyplot as plt
from app.model import booster

explainer = shap.Explainer(booster)


def explain_prediction(features_dict):
    features = np.array([list(features_dict.values())])
    shap_values = explainer(features)
    plt.figure()
    shap.plots.waterfall(shap_values[0], show=False)
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    return img_base64  # Peut aussi renvoyer d'autres infos/explains
