import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture()
def driver():
    print("Starting driver")
    
    # Chrome options
    chrome_options = Options()
    
    # CI/CD ortamında headless çalışsın
    headless = os.getenv('HEADLESS', 'false').lower() == 'true'
    if headless:
        print("🤖 Running in HEADLESS mode")
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    else:
        print("🖥️ Running in NORMAL mode")
    
    # Docker için gerekli argümanlar
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    # Chrome binary path (Docker'da)
    chrome_options.binary_location = '/usr/bin/google-chrome'
    
    my_driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    yield my_driver
    
    print("Shutting down driver")
    my_driver.quit()