import pickle
import time
import undetected_chromedriver as uc

if __name__ == "__main__":
    driver = uc.Chrome()
    driver.get("https://www.twitch.tv/login")

    input("Press enter when you have logged in.")
    cookie_name = input("What is the name of the account? ")
    pickle.dump(driver.get_cookies(),open(f"{cookie_name}.dump","wb"))