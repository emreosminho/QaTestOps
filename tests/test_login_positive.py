import time

import pytest

from page_objects.login_page import LoginPage


class TestLoginPagePositive:
    @pytest.mark.login
    @pytest.mark.positive_login
    def test_login_positive(self, driver):
        login_page = LoginPage(driver)
        login_page.open()
        driver.maximize_window()
        login_page.execute_login("standard_user", "secret_sauce" )
        time.sleep(2)
        login_page.verify_successful_login()

