from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

base_url = "https://defricheur.marceau-h.fr/"
#base_url = "http://0.0.0.0:8000/"


driver.get(base_url)

input("Press Enter to continue...")

url = base_url + "annotate"

driver.get(url)

sleep(10)

while True:
    buttons = driver.find_elements(By.CSS_SELECTOR, "button.answer")

    for button in buttons:
        # button.click()
        wait.until(EC.element_to_be_clickable(button)).click()

    next = wait.until(EC.element_to_be_clickable((By.ID, "suivant")))

    next.click()




