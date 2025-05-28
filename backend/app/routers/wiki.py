from fastapi import APIRouter, Query
from app.controllers.wiki_controllers import scrape_wikipedia_title  

router = APIRouter(prefix="/scrape", tags=["scrape"])

@router.get("/")
def scrape(title: str = Query(..., description="Wikipedia title (e.g., Albert_Einstein)")):
    return scrape_wikipedia_title(title)
