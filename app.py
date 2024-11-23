from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os

# Selenium beállítások
chrome_options = Options()
chrome_options.add_argument("--headless")  # Futtatás fej nélkül, hogy ne nyíljon meg a böngésző
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--start-maximized")  # Teljes méretű ablak indítása

# Proxy hozzáadása
proxy = os.getenv("PROXY_ADDRESS")  # A proxy cím betöltése környezeti változóból
if proxy:
    chrome_options.add_argument(f"--proxy-server={proxy}")

# ChromeDriver útvonala
service = Service("/path/to/chromedriver")  # Ezt cseréld le a saját ChromeDriver útvonaladra

# CAPTCHA megoldó API kulcs
captcha_api_key = os.getenv("CAPTCHA_API_KEY")  # 2Captcha API kulcs betöltése környezeti változóból

# Böngésző indítása
browser = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Lépj be az adott weboldalra
    url = "https://example-sneaker-shop.com"  # Cseréld le a valós sneaker bolt URL-jére
    browser.get(url)

    # Várd meg, hogy a keresőmező betöltődjön
    wait = WebDriverWait(browser, 10)
    search_box = wait.until(EC.presence_of_element_located((By.NAME, "search")))  # Testreszabás szükséges

    # Keresés indítása
    sneaker_name = "Air Jordan 1"  # Cseréld le a keresett cipő nevére
    search_box.send_keys(sneaker_name)
    search_box.send_keys(Keys.RETURN)

    # Várj a keresési eredmények betöltésére
    sneaker_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.product-link")))  # Testreszabás szükséges
    sneaker_link.click()

    # Várj az adott termékoldal betöltésére
    add_to_cart_button = wait.until(EC.presence_of_element_located((By.ID, "add-to-cart")))  # Testreszabás szükséges
    add_to_cart_button.click()

    # CAPTCHA kezelés (ha szükséges)
    captcha_iframe = browser.find_elements(By.TAG_NAME, "iframe")  # CAPTCHA iframe keresése
    if captcha_iframe:
        browser.switch_to.frame(captcha_iframe[0])  # Az első iframe-be való belépés
        captcha_site_key = browser.find_element(By.CLASS_NAME, "g-recaptcha").get_attribute("data-sitekey")

        # 2Captcha megoldás lekérése
        captcha_request = requests.post("https://2captcha.com/in.php", data={
            "key": captcha_api_key,
            "method": "userrecaptcha",
            "googlekey": captcha_site_key,
            "pageurl": url
        })
        if captcha_request.status_code != 200 or "OK" not in captcha_request.text:
            raise Exception(f"CAPTCHA request failed: {captcha_request.text}")

        captcha_id = captcha_request.text.split('|')[1]
        time.sleep(20)  # Várakozás a CAPTCHA megoldására

        captcha_response = requests.get("https://2captcha.com/res.php", params={
            "key": captcha_api_key,
            "action": "get",
            "id": captcha_id
        })
        if captcha_response.status_code != 200 or "OK" not in captcha_response.text:
            raise Exception(f"CAPTCHA solution retrieval failed: {captcha_response.text}")

        captcha_solution = captcha_response.text.split('|')[1]

        # CAPTCHA megoldás beillesztése
        browser.execute_script("document.getElementById('g-recaptcha-response').value=arguments[0]", captcha_solution)
        browser.switch_to.default_content()

    # Várj, hogy megbizonyosodj róla, hogy kosárba helyezte
    confirmation_message = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cart-confirmation")))  # Testreszabás szükséges
    print("A terméket sikeresen kosárba helyezte!")

    # Fizetési folyamat (példa, testreszabás szükséges)
    payment_button = wait.until(EC.presence_of_element_located((By.ID, "proceed-to-checkout")))  # Testreszabás szükséges
    payment_button.click()

    # Fizetési adatok megadása (testre szabás)
    card_number_field = wait.until(EC.presence_of_element_located((By.NAME, "card_number")))
    card_number_field.send_keys("4111111111111111")  # Példa bankkártya szám (teszt adatok)

    expiration_field = browser.find_element(By.NAME, "expiration_date")
    expiration_field.send_keys("12/25")

    cvv_field = browser.find_element(By.NAME, "cvv")
    cvv_field.send_keys("123")

    submit_payment_button = browser.find_element(By.ID, "submit-payment")
    submit_payment_button.click()

    print("Fizetés sikeresen elindítva!")

except Exception as e:
    print(f"Hiba történt: {e}")

finally:
    # Böngésző bezárása
    browser.quit()