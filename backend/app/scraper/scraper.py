import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re
from typing import List, Dict, Optional, Union
import logging
from datetime import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RERAScraperController:
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.wait = None
        self.projects = []
        self.detail_urls = []
        
    def setup_drive(self):
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Chrome driver setup successful")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up driver: {e}")
            return False
    
    def _cleanup_driver(self):
        """Clean up the driver resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver cleanup successful")
            except Exception as e:
                logger.error(f"Error during driver cleanup: {e}")
    
    def get_projects(self, url: str = "https://rera.odisha.gov.in/projects/project-list", 
                    max_proj: Optional[int] = None) -> Dict[str, Union[List[Dict], str, int]]:
    #    main
        start_time = datetime.now()
        
        try:
            
            if not self.setup_drive():
                return {
                    "success": False,
                    "message": "Failed to initialize web driver",
                    "data": [],
                    "total_projects": 0,
                    "total_urls": 0,
                    "execution_time": 0
                }
            
            logger.info("Starting project scraping...")
            self.driver.get(url)
            
            
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "project-card")))
            
            
            self.scrape_6_project(6)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "message": f"Successfully scraped {len(self.projects)} projects",
                "data": self.projects,
                "total_projects": len(self.projects),
                "total_urls": len(self.detail_urls),
                "detail_urls": self.detail_urls,
                "execution_time": execution_time,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": False,
                "message": f"Scraping failed: {str(e)}",
                "data": self.projects,  
                "total_projects": len(self.projects),
                "total_urls": len(self.detail_urls),
                "execution_time": execution_time,
                "error": str(e)
            }
            
        finally:
            self._cleanup_driver()
    
    def get_project_by_registration(self, registration_number: str) -> Dict[str, Union[Dict, str, bool]]:
        """
        Get a specific project by registration number
        
        Args:
            registration_number: The project registration number
            
        Returns:
            Dictionary containing project data or error message
        """
        try:
            
            result = self.get_projects()
            
            if not result["success"]:
                return result
            
            
            for project in result["data"]:
                if project.get("registration_number", "").strip() == registration_number.strip():
                    return {
                        "success": True,
                        "message": "Project found",
                        "data": project
                    }
            
            return {
                "success": False,
                "message": f"Project with registration number '{registration_number}' not found",
                "data": None
            }
            
        except Exception as e:
            logger.error(f"Error getting project by registration: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": None
            }
    
    def get_projects_by_developer(self, developer_name: str) -> Dict[str, Union[List[Dict], str, bool, int]]:
        """
        Get all projects by a specific developer
        
        Args:
            developer_name: The developer/promoter name
            
        Returns:
            Dictionary containing matching projects or error message
        """
        try:
            
            result = self.get_projects()
            
            if not result["success"]:
                return result
            
            
            matching_projects = []
            for project in result["data"]:
                project_developer = project.get("developer", "").lower()
                if developer_name.lower() in project_developer:
                    matching_projects.append(project)
            
            return {
                "success": True,
                "message": f"Found {len(matching_projects)} projects by developer '{developer_name}'",
                "data": matching_projects,
                "total_found": len(matching_projects)
            }
            
        except Exception as e:
            logger.error(f"Error getting projects by developer: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": [],
                "total_found": 0
            }
    
    def get_projects_summary(self) -> Dict[str, Union[Dict, str, bool]]:
        """
        Get summary statistics of all projects
        
        Returns:
            Dictionary containing project statistics
        """
        try:
            
            result = self.get_projects()
            
            if not result["success"]:
                return result
            
            projects = result["data"]
            
            
            total_projects = len(projects)
            developers = set()
            project_types = {}
            locations = {}
            
            for project in projects:
                
                if project.get("developer"):
                    developers.add(project["developer"])
                
                
                ptype = project.get("project_type", "Unknown")
                project_types[ptype] = project_types.get(ptype, 0) + 1
                
                
                address = project.get("address", "")
                if address:
                    
                    location = address.split(",")[-1].strip() if "," in address else "Unknown"
                    locations[location] = locations.get(location, 0) + 1
            
            return {
                "success": True,
                "message": "Summary generated successfully",
                "data": {
                    "total_projects": total_projects,
                    "total_developers": len(developers),
                    "project_types": project_types,
                    "locations": locations,
                    "top_developers": list(developers)[:10],  
                    "scraped_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": {}
            }
    
    def export_to_format(self, format_type: str = "json", filename: Optional[str] = None) -> Dict[str, Union[str, bool]]:
        """
        Export scraped data to different formats
        
        Args:
            format_type: 'json', 'csv', or 'excel'
            filename: Optional custom filename
            
        Returns:
            Dictionary containing export status and filename
        """
        try:
            if not self.projects:
                result = self.get_projects()
                if not result["success"]:
                    return {
                        "success": False,
                        "message": "No data to export",
                        "filename": None
                    }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_type.lower() == "csv":
                filename = filename or f"rera_projects_{timestamp}.csv"
                df = pd.DataFrame(self.projects)
                df.to_csv(filename, index=False)
                
            elif format_type.lower() == "excel":
                filename = filename or f"rera_projects_{timestamp}.xlsx"
                df = pd.DataFrame(self.projects)
                df.to_excel(filename, index=False)
                
            elif format_type.lower() == "json":
                import json
                filename = filename or f"rera_projects_{timestamp}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        "projects": self.projects,
                        "metadata": {
                            "total_projects": len(self.projects),
                            "total_urls": len(self.detail_urls),
                            "exported_at": datetime.now().isoformat()
                        }
                    }, f, indent=2, ensure_ascii=False)
            else:
                return {
                    "success": False,
                    "message": "Unsupported format. Use 'json', 'csv', or 'excel'",
                    "filename": None
                }
            
            return {
                "success": True,
                "message": f"Data exported successfully to {filename}",
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return {
                "success": False,
                "message": f"Export failed: {str(e)}",
                "filename": None
            }
    
    def scrape_6_project(self, max_proj: Optional[int] = None):
        """Scrape all pages with optional limit"""
        project_num = 1
        
        while True:
            if max_proj and project_num > max_proj:
                logger.info(f"Reached maximum pages limit: {max_proj}")
                break
                
            logger.info(f"Scraping page {project_num}...")
            
            
            self.scrape_active_proj()
            
            
            try:
                next_button = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Next') or contains(@class, 'next')]")
                if next_button.is_enabled():
                    next_button.click()
                    time.sleep(2)
                    project_num += 1
                else:
                    break
            except:
                break
    
    def scrape_active_proj(self):
        for i in range(6):
            try:
                current_cards = self.driver.find_elements(By.CLASS_NAME, "project-card")
                
                if i < len(current_cards):
                    project_data = self.extract_proj_data(current_cards[i], i)
                    if project_data:
                        self.projects.append(project_data)
                        logger.info(f"Extracted {i+1}/{6}: {project_data['project_name']}")
                        
            except Exception as e:
                logger.error(f"Error extracting project {i+1}: {e}")
                continue
    
    def extract_proj_data(self, card, card_index: int) -> Optional[Dict]:
        """Extract data from a single project card"""
        try:
            
            basic_data = self._extract_basic_info(card)
            
            
            detailed_info = self._get_detailed_info(card_index)
            
            
            if detailed_info:
                basic_data.update(detailed_info)
            
            return basic_data
            
        except Exception as e:
            logger.error(f"Error extracting project: {e}")
            return None
    
    def _extract_basic_info(self, card) -> Dict:
        try:
            
            project_name = card.find_element(By.CSS_SELECTOR, ".card-title").text.strip()
            
            
            developer = card.find_element(By.TAG_NAME, "small").text.replace("by ", "").strip()
            
            
            labels = card.find_elements(By.CLASS_NAME, "label-control")
            data_dict = {}
            
            for label in labels:
                label_text = label.text.strip()
                try:
                    value_element = label.find_element(By.XPATH, "./following-sibling::strong")
                    data_dict[label_text] = value_element.text.strip()
                except:
                    continue
            
            
            units_info = ""
            try:
                units_element = card.find_element(By.CSS_SELECTOR, ".apartment-unit strong")
                units_info = units_element.text.strip()
            except:
                pass
            
            
            reg_number = ""
            try:
                reg_element = card.find_element(By.CSS_SELECTOR, ".fw-bold")
                reg_number = reg_element.text.strip()
            except:
                pass
            
            
            cert_link = ""
            try:
                cert_element = card.find_element(By.CSS_SELECTOR, ".icon-pdf")
                cert_link = cert_element.get_attribute("href")
            except:
                pass
            
            return {
                'project_name': project_name,
                'developer': developer,
                'address': data_dict.get('Address', ''),
                'project_type': data_dict.get('Project Type', ''),
                'started_from': data_dict.get('Started From', ''),
                'possession_by': data_dict.get('Possession by', ''),
                'units': units_info,
                'registration_number': reg_number,
                'certificate_link': cert_link
            }
            
        except Exception as e:
            logger.error(f"Error extracting basic info: {e}")
            return {}
    
    def _get_detailed_info(self, card_index: int) -> Dict:
        detailed_info = {}
        original_window = self.driver.current_window_handle
        detail_url = ""
        
        try:
            current_cards = self.driver.find_elements(By.CLASS_NAME, "project-card")
            
            if card_index >= len(current_cards):
                return {}
            
            card = current_cards[card_index]
            view_details_btn = card.find_element(By.XPATH, ".//a[contains(text(), 'View Details')]")
            current_url = self.driver.current_url
            
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", view_details_btn)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", view_details_btn)
            time.sleep(3)
            
            
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                detail_url = self.driver.current_url
                detailed_info = self.detail_info_page()
                self.driver.close()
                self.driver.switch_to.window(original_window)
                
            elif self.driver.current_url != current_url:
                detail_url = self.driver.current_url
                detailed_info = self.detail_info_page()
                self.driver.back()
                time.sleep(2)
                
            else:
                detail_url = current_url
                detailed_info = self._extract_modal_info()
            
            if detail_url:
                detailed_info['detail_page_url'] = detail_url
                self.detail_urls.append(detail_url)
            
        except Exception as e:
            logger.error(f"Error getting detailed info: {e}")
            try:
                if len(self.driver.window_handles) > 1:
                    for handle in self.driver.window_handles:
                        if handle != original_window:
                            self.driver.switch_to.window(handle)
                            self.driver.close()
                    self.driver.switch_to.window(original_window)
            except:
                pass
        
        return detailed_info
    
    def detail_info_page(self) -> Dict:
        detailed_info = {}
        
        try:
            time.sleep(2)
            
            
            promoter_info = self._extract_promoter_details()
            if promoter_info:
                detailed_info.update(promoter_info)
            
            
            try:
                desc_element = self.driver.find_element(By.CSS_SELECTOR, ".project-description, .description")
                detailed_info['description'] = desc_element.text.strip()
            except:
                pass
            
            try:
                area_element = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Total Area')]/following-sibling::*")
                detailed_info['total_area'] = area_element.text.strip()
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error extracting detailed page info: {e}")
        
        return detailed_info
    
    def _extract_promoter_details(self) -> Dict:
        promoter_info = {}
        
        try:
            
            promoter_selectors = [
                "//a[contains(text(), 'Promoter Details')]",
                "//a[contains(text(), 'Promoters Details')]",
                "//li[@class='nav-item']//a[contains(text(), 'Promoter')]"
            ]
            
            promoter_link = None
            for selector in promoter_selectors:
                try:
                    promoter_link = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue
            
            if promoter_link and "active" not in promoter_link.get_attribute("class"):
                self.driver.execute_script("arguments[0].click();", promoter_link)
                time.sleep(3)
            
            
            promoter_info = self._extract_promoter_content()
                
        except Exception as e:
            logger.error(f"Error extracting promoter details: {e}")
        
        return promoter_info
    
    def _extract_promoter_content(self) -> Dict:
        """Extract promoter content from card-body elements"""
        promoter_data = {}
        
        try:
            promoter_selectors = [".promoter", "div.promoter", ".card-body"]
            
            promoter_section = None
            for selector in promoter_selectors:
                try:
                    promoter_section = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if promoter_section:
                card_bodies = promoter_section.find_elements(By.CSS_SELECTOR, ".card-body")
                
                for i, card_body in enumerate(card_bodies):
                    try:
                        card_text = card_body.text.strip()
                        if card_text:
                            promoter_data[f'promoter_card_{i+1}'] = card_text
                        
                        
                        lines = card_text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if ':' in line and len(line.split(':')) == 2:
                                key, value = line.split(':', 1)
                                clean_key = f"promoter_{key.strip().lower().replace(' ', '_')}"
                                promoter_data[clean_key] = value.strip()
                                
                    except Exception as e:
                        logger.error(f"Error extracting from card body {i+1}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error extracting promoter content: {e}")
        
        return promoter_data
    
    def _extract_modal_info(self) -> Dict:
        """Extract information from modal/popup"""
        detailed_info = {}
        
        try:
            modal_selectors = [".modal-content", ".popup-content", ".detail-modal", "[role='dialog']"]
            
            modal = None
            for selector in modal_selectors:
                try:
                    modal = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if modal:
                detailed_info['modal_content'] = modal.text
                
                
                promoter_info = self._extract_promoter_details()
                if promoter_info:
                    detailed_info.update(promoter_info)
                
                
                try:
                    close_btn = modal.find_element(By.CSS_SELECTOR, ".close, .btn-close, [data-dismiss='modal']")
                    close_btn.click()
                    time.sleep(1)
                except:
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(1)
        
        except Exception as e:
            logger.error(f"Error extracting modal info: {e}")
        
        return detailed_info

def main():
    controller = RERAScraperController(headless=False)
    
    
    result = controller.get_projects(max_proj=2)  
    print(f"Status: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Total Projects: {result['total_projects']}")
    
    if result['success'] and result['data']:
        
        summary = controller.get_projects_summary()
        print(f"\nSummary: {summary['data']}")
        
        
        export_result = controller.export_to_format('json')
        print(f"Export: {export_result['message']}")


if __name__ == "__main__":
    main()