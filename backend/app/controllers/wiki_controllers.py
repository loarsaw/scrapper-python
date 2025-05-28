from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def scrape_wikipedia_title(title: str) -> dict:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = f"https://en.wikipedia.org/wiki/{title}"
        driver.get(url)

        paragraph = driver.find_element(By.CSS_SELECTOR, "div.mw-parser-output > p").text

        return {
            "title": title.replace("_", " "),
            "summary": paragraph,
            "url": url
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()
