from fastapi import APIRouter

from app.api.v1 import catalog, games, leaderboard

api_router = APIRouter()
api_router.include_router(catalog.router)
api_router.include_router(leaderboard.router)
api_router.include_router(games.router)
