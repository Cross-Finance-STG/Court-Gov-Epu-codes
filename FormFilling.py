import time
import os
import fitz
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from Db import insertXmlInfo
import xml.etree.ElementTree as ET
from xml.dom import minidom

download_path = r"\\kaszta\os\STG\kody_klauzuli"


def autofill(driver, captchaValue, code):

    try:
        captcha_input = driver.find_element(
            By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_txtValidCode"]'
        )
        captcha_input.send_keys(captchaValue)

        kodDostepuInput = driver.find_element(
            By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_TextBoxKod"]'
        )
        kodDostepuInput.send_keys(code)

        time.sleep(0.5)

        showImage = driver.find_element(
            By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_Button2"]'
        )

        # Zapisywanie uchwytów okien przed kliknięciem
        original_window = driver.current_window_handle
        existing_windows = driver.window_handles
        showImage.click()

        # Czekanie na otwarcie nowej karty
        WebDriverWait(driver, 10).until(EC.new_window_is_opened(existing_windows))

        # Pobranie uchwytu nowej karty
        new_windows = driver.window_handles
        new_window = [
            window for window in new_windows if window not in existing_windows
        ][0]

        # Przełączenie na nową kartę
        driver.switch_to.window(new_window)
        print(f"Przełączono na nową kartę: {new_window}")

        # Oczekiwanie na pełne załadowanie strony
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Pobranie URL PDF-a
        pdf_url = driver.current_url
        print(f"URL PDF dla ID klauzuli {code}: {pdf_url}")

        # Pobranie ciasteczek z przeglądarki
        cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}

        # Pobranie PDF-a za pomocą requests
        response = requests.get(pdf_url, cookies=cookies)

        if response.status_code == 200 and "application/pdf" in response.headers.get(
            "Content-Type", ""
        ):
            pdf_content = response.content
            pdf_path = os.path.join(download_path, f"{code}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(pdf_content)
            print(f"Zapisano PDF dla ID {code} jako {pdf_path}")
        else:
            print(
                f"Nie udało się pobrać pliku dla ID {code}, status code: {response.status_code}"
            )
            # Zamknięcie nowej karty i powrót do oryginalnej
            driver.close()
            driver.switch_to.window(original_window)
            return

        # Zamknięcie nowej karty i powrót do oryginalnej
        driver.close()
        driver.switch_to.window(original_window)
        print(f"Zamknięto kartę z PDF-em dla ID {id}")

        # Przetwarzanie PDF-a
        xml_content = pdf_to_xml_string(pdf_path)
        if xml_content:
            print(f"Pobrano XML dla ID {id}")
            insertXmlInfo(code, xml_content, pdf_path)
        else:
            delete_file(pdf_path)
            print(f"Nie znaleziono XML-a w pliku PDF dla ID {id}")

    except TimeoutException:
        print(f"Nie znaleziono przycisku pobierania dla ID {id}")
        return
    except Exception as e:
        print(f"Błąd przy pobieraniu danych dla ID {id}: {e}")
        if pdf_path and os.path.exists(pdf_path):
            delete_file(pdf_path)
        # Zamknięcie nowej karty i powrót do oryginalnej, jeśli to konieczne
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)
        return  # Przechodzimy do następnego ID


def pdf_to_xml_string(pdf_path):
    """
    Konwertuje plik PDF na format XML i zwraca jako string.

    :param pdf_path: Ścieżka do pliku PDF.
    :return: XML jako string.
    """
    # Tworzymy korzeń XML
    root = ET.Element("PDFDocument")

    with fitz.open(pdf_path) as pdf_doc:
        for page_num, page in enumerate(pdf_doc, start=1):
            page_element = ET.SubElement(root, "Page", number=str(page_num))

            # Wyodrębniamy tekst z bieżącej strony
            text = page.get_text("text")

            # Dodajemy tekst strony jako element XML
            page_text_element = ET.SubElement(page_element, "Text")
            page_text_element.text = text

    # Konwertujemy drzewo XML na string
    xml_string = ET.tostring(root, encoding="unicode")

    # Opcjonalne formatowanie XML, aby był bardziej czytelny
    parsed_xml = minidom.parseString(xml_string)
    pretty_xml = parsed_xml.toprettyxml(indent="  ")

    return pretty_xml


def delete_file(file_path):
    """
    Usuwa plik na podanej ścieżce, jeśli istnieje.

    :param file_path: Ścieżka do pliku, który ma zostać usunięty.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Plik {file_path} został usunięty.")
    else:
        print(f"Plik {file_path} nie istnieje.")
