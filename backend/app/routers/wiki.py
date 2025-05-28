from fastapi import APIRouter, Query
router = APIRouter(prefix="/scrape", tags=["scrape"])

@router.get("/")
def scrape(title: str = Query(..., description="Wikipedia title (e.g., Albert_Einstein)")):
    return scrape_wikipedia_title(title)
