import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import configparser
import multiprocessing

import time

config = configparser.ConfigParser()
config.read("config.ini")

settings = {}
settings["streamer"] = config["default"]["streamer"]

def SpawnBot():
    driver = uc.Chrome()
    driver.get("https://www.twitch.tv/")
    search_box = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/nav/div/div[2]/div/div/div/div/div[1]/div/div/div/input")

    search_box.send_keys(settings["streamer"])
    search_box.send_keys(Keys.ENTER)

    time.sleep(2)

    elements = driver.find_elements(By.TAG_NAME,"a")

    for element in elements:
        if element.text == settings["streamer"]:
            element.click()
            break

    while True:
        pass

if __name__ == "__main__":
    process = multiprocessing.Process(target=SpawnBot)
    process.start()

