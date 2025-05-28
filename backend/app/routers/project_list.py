from fastapi import APIRouter
from typing import Optional
from app.scraper.scraper import RERAScraperController

router = APIRouter()

controller = RERAScraperController(headless=True)

@router.get("/api/projects")
async def get_projects(max_proj: Optional[int] = None):
    return controller.get_projects(max_proj=max_proj)
