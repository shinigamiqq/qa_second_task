import csv
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


def parse_contacts(output_file: str):
    """
    Скрипт:
    1. Открывает onlyoffice.com
    2. Наводит на меню Resources -> Contacts
    3. Переходит на страницу контактов
    4. Парсит все офисы (Country, Company, Full Address)
    5. Сохраняет результат в CSV-файл
    """

    options = Options()
    options.add_argument("--headless")
    #options.binary_location = "/usr/bin/firefox"

    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        print("[*] Открываем сайт onlyoffice.com ...")
        driver.get("https://www.onlyoffice.com/")
        driver.maximize_window()

        try:
            print("[*] Проверяем баннер cookies ...")
            cookie_accept_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="cookieMessCloseCross"]'))
            )
            cookie_accept_button.click()
            print("[+] Баннер cookies закрыт.")
        except:
            print("[*] Баннер cookies не найден, продолжаем ...")

        resources_menu = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="navitem_about"]'))
        )
        ActionChains(driver).move_to_element(resources_menu).perform()
        time.sleep(1)

        contacts_link = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="navitem_about_contacts"]')
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", contacts_link)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", contacts_link)


        print("[*] Ждём загрузки страницы контактов ...")
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.companydata")))

        time.sleep(2)

        print("[*] Парсим данные ...")
        all_companies = driver.find_elements(By.CSS_SELECTOR, "div.companydata")
        companies = [c for c in all_companies if "Contact us" not in c.text]

        data = []

        for company in companies:
            try:
                country = company.find_element(By.CSS_SELECTOR, ".region").text.strip()
            except:
                country = ""

            try:
                name = company.find_element(By.CSS_SELECTOR, "b").text.strip()
            except:
                name = ""

            try:
                address_parts = company.find_elements(By.CSS_SELECTOR, "span[itemprop]")
                address = " ".join([part.text.strip() for part in address_parts if part.text.strip()])
            except:
                address = ""

            data.append([country, name, address])

        print(f"[*] Найдено {len(data)} офисов. Сохраняем в файл {output_file} ...")

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Country", "CompanyName", "FullAddress"])
            writer.writerows(data)

        print("[+] Данные успешно сохранены!")

    finally:
        driver.quit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python main.py <путь_к_CSV>")
        sys.exit(1)

    output_path = sys.argv[1]
    parse_contacts(output_path)

