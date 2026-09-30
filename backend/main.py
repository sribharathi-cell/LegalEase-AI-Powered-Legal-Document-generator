from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router


app = FastAPI(
    title="LegalEase API",
    description=(
        "AI-assisted legal document drafting API"
    ),
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(router)


@app.get("/")
def root():

    return {
        "status": "ok",
        "service": "LegalEase API",
        "docs": "/docs"
    }