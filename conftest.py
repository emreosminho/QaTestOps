import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



@pytest.fixture()
def driver():
    print("Starting driver")
    my_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    yield my_driver
    print("Shutting down driver")
    my_driver.quit()