from Login import logging_into_account
from CaptchaSolver import solve
from FormFilling import autofill
from Db import getIDs


def main():
    # logowanie sie do portalu
    driver = logging_into_account()
    # pobranie wyfiltrowanych kodow klauzuli
    kodyKluzuli = getIDs()
    print(f"Pobrano {len(kodyKluzuli)} spraw")
    for code in kodyKluzuli:
        # dla kazdego kodu klauzuli rozwiazanie captchy oraz pobranie akt i zapisanie do bazy
        captcha_value = solve(driver)
        if captcha_value:
            autofill(driver, captcha_value, code)


if __name__ == "__main__":
    main()
