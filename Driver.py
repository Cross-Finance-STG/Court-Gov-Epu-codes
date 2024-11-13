from seleniumwire import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options


def driver_start():
    driver_path = r"C:\WEBDRV\msedgedriver.exe"
    url = "https://www.e-sad.gov.pl/"
    service = Service(executable_path=driver_path)
    options = Options()
    options.add_argument("--log-level=3")
    options.use_chromium = True
    driver = webdriver.Edge(service=service, options=options)
    driver.get(url)
    driver.refresh()
    return driver
