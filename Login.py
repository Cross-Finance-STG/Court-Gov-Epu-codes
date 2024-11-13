from Driver import driver_start
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import (
    NoAlertPresentException,
)


def logging_into_account():
    driver = driver_start()
    driver.add_cookie({"name": "acceptCookies", "value": "1"})
    name = driver.find_element(
        By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_UserName"]'
    )
    name.send_keys("login")
    password = driver.find_element(
        By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_Password"]'
    )
    password.send_keys("pass")
    button = driver.find_element(
        By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_LoginButton"]'
    )
    button.click()
    time.sleep(2)

    # Sprawdza i zamkyka alert, jeśli się pojawi
    try:
        alert = driver.switch_to.alert
        alert.accept()
        print("Alert zamknięty.")
    except NoAlertPresentException:
        print("Alert nie był otwarty.")

    return driver
