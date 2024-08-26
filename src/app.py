from time import sleep
import dotenv
import logging
import threading
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from constants import *
from webhook import app, get_latest_data

dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)

PHONE_NUMBER = "8887140378"

BASE_URL = "https://www.cashify.in/sell-old-mobile-phone/used-apple-iphone-xr-128-gb"
GET_EXACT_VAL = "/html/body/main/main/div/div[2]/div[2]/div[1]/div/div[2]/div[3]/div[4]/div/div/button"
POPUP_GOT_IT="/html/body/div/div[2]/div/div/div/div[3]/div/div/button"
POPUP_GOT_IT_TEXT="got it"
SECTION="/html/body/main/main/div/div/div[2]/div[2]/div/section/div/div[1]/div/div[3]/section"
CONTINUE = {
    "DETAILS": "/html/body/main/main/div/div/div[2]/div[2]/div/section/div/div[1]/div/div[4]/div/div/div/button",
        "SCREEN":"/html/body/main/main/div/div/div[2]/div[2]/div/section/div/div[1]/div/div[4]/div/div/div/button",
    "FUNCTIONAL":"/html/body/main/main/div/div/div[2]/div[2]/div/section/div/div[1]/div/div[4]/div/div/div/button",
    "ACCESSORIES":"/html/body/main/main/div/div/div[2]/div[2]/div/section/div/div[1]/div/div[4]/div/div/div/button",
    "PHONE":"/html/body/div/div[2]/div/div/div/section/div[2]/div[2]/div[2]/div[2]/div/button"

}
PHONE_INPUT='//*[@id="mobile-no"]'
OTP_INPUT="/html/body/div/div[2]/div/div/div/section/div[2]/div[2]/div[1]/div[2]/div[4]/div/div[1]/div/input"
OTP_SUBMIT="/html/body/div/div[2]/div/div/div/section/div[2]/div[2]/div[2]/div/button"

OTP_REGEX = r"\b\d{6}\b"


def getOTP():
    max_attempts = 12
    attempt = 0
    while attempt < max_attempts:
        sleep(5)
        attempt+=1
        logging.info(f"Attemptng to get OTP:{attempt}")
        status, data = get_latest_data(60)
        if(status):
            logging.log(logging.INFO, "OTP received")
            otp = re.findall(OTP_REGEX, data["data"]["text"])
            return otp[0] if otp else None
        else :
            logging.log(logging.INFO, "No OTP received")
    return None

def init_driver():
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome()
    return driver

def get_elements(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((by, value)))

FLOWS = [
    [0,0,0], [0,0,1], [0,1,0],[0,1,1], [1,0,0], [1,0,1], [1,1,0], [1,1,1]
]


def main():
        driver = init_driver()
        wait = WebDriverWait(driver, 10)
        try:
            for flow in FLOWS:
                print(f'Flow: {flow}')
                driver.get(BASE_URL)
                wait.until(EC.presence_of_element_located((By.XPATH, GET_EXACT_VAL)))
                button = driver.find_element(By.XPATH, GET_EXACT_VAL)
                while(not button.is_enabled()):
                    sleep(1)
                button.click()
                sleep(2)
                try:
                    got_it = driver.find_element(By.XPATH, POPUP_GOT_IT)
                    if got_it.text.lower() == POPUP_GOT_IT_TEXT:
                        print("Popup found and handled")
                        got_it.click()
                    else :
                        print("Popup found but not handled")
                except Exception as e:
                    logging.info("No popup found")
                all_sections = get_elements(driver, By.XPATH, SECTION)
                all_options = []
                for section in all_sections:
                    options_box = section.find_element(By.XPATH, './div[2]')
                    options = options_box.find_elements(By.XPATH, './div')
                    all_options.append(options)
                    for i in range(len(all_options)):
                        options[flow[i]].click()
                driver.find_element(By.XPATH, CONTINUE["DETAILS"]).click()
                sleep(2)
                driver.find_element(By.XPATH, CONTINUE["SCREEN"]).click()
                sleep(2)
                driver.find_element(By.XPATH, CONTINUE["FUNCTIONAL"]).click()
                sleep(2)
                driver.find_element(By.XPATH, CONTINUE["ACCESSORIES"]).click()
                sleep(2)
                try:
                    phone_input = driver.find_element(By.XPATH, PHONE_INPUT)
                    phone_input.send_keys(PHONE_NUMBER)
                    driver.find_element(By.XPATH, CONTINUE["PHONE"]).click()
                    sleep(2)
                    otp_input = driver.find_element(By.XPATH, OTP_INPUT)
                    otp = getOTP()
                    if not otp:
                        logging.error("OTP not received")
                        continue
                    otp_input.send_keys(otp)
                    sleep(10)
                    # driver.find_element(By.XPATH, OTP_SUBMIT).click()
                except Exception as e:
                    print("Phone input not found")
                sleep(5)
            driver.close()
        except Exception as e:
            logging.error(f'An error occurred: {e}')
            driver.quit()

if __name__ == "__main__":
    logging.info("Starting webhook server")
    server_thread = threading.Thread(target=lambda: app.run(port=5000))
    server_thread.start()
    logging.info("Webhook server started")
    logging.info("Starting main function")
    main()
    logging.info("Main function completed")

