from fastapi import FastAPI
from app.api import router

app = FastAPI(
    title="Attrition ESN API",
    description="API de prédiction d’attrition des salariés d’ESN"
)
app.include_router(router)
