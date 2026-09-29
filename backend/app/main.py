from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings

app = FastAPI(
    title="FanGap",
    description=(
        "Hybrid FanGap: IGDB catalog with live critic/fan scores, "
        "plus Featured Top 10 monthly snapshot history in Postgres."
    ),
    version="0.1.0",
    openapi_tags=[
        {
            "name": "games",
            "description": "Catalog of games, including search, filters, and CRUD.",
        },
        {
            "name": "ratings",
            "description": "Latest scores and full snapshot history per game.",
        },
        {
            "name": "divergence",
            "description": "Absolute gap between latest critic and fan averages.",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", summary="Service identity")
def root():
    return {"name": "FanGap", "status": "ok"}


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}
