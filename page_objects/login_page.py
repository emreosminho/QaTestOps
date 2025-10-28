
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By



from page_objects.base_page import BasePage


class LoginPage(BasePage):
    __url = "https://www.saucedemo.com/"
    __username_field = (By.ID, "user-name")
    __password_field = (By.ID, "password")
    __submit_field = (By.ID, "login-button")
    __title_field = (By.XPATH, "//*[@id='header_container']/div[2]/span")
    __expected_url = "https://www.saucedemo.com/inventory.html"


    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def open(self):
        super()._open_url(self.__url)

    def execute_login(self, username: str, password: str):
        super()._type(self.__username_field, username)
        super()._type(self.__password_field, password)
        super()._click(self.__submit_field)

    def verify_successful_login(self):
        """Login sonrası URL doğru mu kontrol eder."""
        current_url = current_url = self._driver.current_url
        assert current_url == self.__expected_url, (
            f"❌ Beklenen URL '{self.__expected_url}', "
            f"ancak mevcut URL '{current_url}'"
        )
        print("✅ Login başarılı — doğru sayfaya yönlendirildi!")








