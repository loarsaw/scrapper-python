from fastapi.responses import JSONResponse
from typing import Optional, Dict, List
from app.scraper.scraper import Scrapper  

def scrape_rera_projects(headless: bool = True, max_proj: Optional[int] = None) -> Dict:
    try:
        scraper = Scrapper(headless=headless)
        projects = scraper.scrape_projects(max_proj=max_proj)

        return {
            "success": True,
            "total_projects": len(projects),
            "projects": projects,
            "message": f"Successfully scraped {len(projects)} projects"
        }
        
    except Exception as e:
        return {
            "success": False,
            "total_projects": 0,
            "projects": [],
            "error": str(e),
            "message": "Failed to scrape projects"
        }
