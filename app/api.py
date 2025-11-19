from fastapi import APIRouter, HTTPException
from app.model import predict_attrition
from app.db import get_employee_features
from app.explainer import explain_prediction

router = APIRouter()


@router.get("/health")
def healthcheck():
    return {"status": "ok"}


@router.post("/predict")
def predict(employee_id: int):
    features = get_employee_features(employee_id)
    if features is None:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    score = predict_attrition(features)
    explanation = explain_prediction(features)
    return {"score": score, "explanation": explanation}
