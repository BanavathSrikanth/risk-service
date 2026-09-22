from fastapi import FastAPI

from app.api.routes.risk_routes import router as risk_router

app = FastAPI(title="Risk Service API")
app.include_router(risk_router)
