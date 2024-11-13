import base64
from anticaptchaofficial.imagecaptcha import imagecaptcha
from selenium.webdriver.common.by import By

API_KEY = "APIKEY"


def solve(driver):
    driver.get("https://www.e-sad.gov.pl/kod.aspx")
    # Znajdź element obrazu captcha i pobierz jego URL
    captcha_element = driver.find_element(
        By.XPATH,
        '//*[@id="ctl00_ContentPlaceHolder1_CaptchaUpdatePanel"]/div[1]/span[1]/div/img',
    )
    # Pobierz źródło obrazu (URL)
    captcha_url = captcha_element.get_attribute("src")

    # Otwórz nową kartę
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])

    # Przejdź do URL z obrazem
    driver.get(captcha_url)

    # Pobierz dane obrazu jako Base64 (jeśli src to 'data:image/...', musisz użyć tego podejścia)
    image_element = driver.find_element(By.TAG_NAME, "img")
    image_base64 = image_element.screenshot_as_base64

    # Konwertuj Base64 do obrazu i zapisz
    with open("tmp.image", "wb") as image_file:
        image_file.write(base64.b64decode(image_base64))

    print("Obraz captchy zapisany jako 'tmp.image'")

    # Zamknij nową kartę i wróć do oryginalnej
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # Rozwiąż captcha za pomocą biblioteki anticaptcha
    solver = imagecaptcha()
    solver.set_key(API_KEY)

    solved_text = solver.solve_and_return_solution("tmp.image")

    if solved_text != 0:
        print("Captcha rozwiązana:", solved_text)
        return solved_text
    else:
        print("Captcha nie została rozwiązana. Błąd:", solver.error_code)
        return None
