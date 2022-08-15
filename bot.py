import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pickle
from os import listdir, getcwd
from os.path import isfile,join
import requests
import random

def RandomEvents(driver):
    actions = ["chat"]
    action_selected = actions[random.randint(0,len(actions)-1)]

    if action_selected == "chat":
        time.sleep(1)
        element = driver.find_element(By.CLASS_NAME,"chat-input")
        element.click()
        cypher = 1
        while cypher<=10:
            try:
                element = driver.find_element(By.XPATH,f"//*[@id='live-page-chat']/div/div/div/div/div/section/div/div[{cypher}]/div[2]/div[1]/div[2]/div/div/div[1]/div/div/div/div/div[2]")
                break
            except:
                print("[!] Chatbox cannot be found, bruteforcing...")
                cypher +=1
        
        to_say = "Hello, how is your day?" # make it so you can read stuff from a file here instead
        for letter in to_say:
            element.send_keys(letter)
            time.sleep(random.uniform(0,0.5))
        element.send_keys(Keys.ENTER)


def BotLogic(logged_in,driver):

    if logged_in:
        #try to activate chat
        try:
            element = driver.find_element(By.CLASS_NAME,"chat-input")
            element.click()
            time.sleep(random.uniform(0,2))
            element = driver.find_element(By.XPATH,"/html/body/div[5]/div/div/div/div/div/div/div[3]/button")
            element.click()
        except:
            print("[!] No chat rulez...")

    # spawn a thread to listen for @ts and for speech recognition
    while True:
        if logged_in:
            RandomEvents(driver)
        time.sleep(10)

def GetProxyList(proxy_type):
    if proxy_type == "dynamic":
        proxy_list = requests.get("https://proxy.webshare.io/proxy/list/download/ennfuqskpmcpnpjepzjhwknhmpibfqbnfmqibakl/-/http/port/direct/").content.decode("UTF-8")
        proxy_list = proxy_list.split("\n")
        for i in range(len(proxy_list)):
            proxy_list[i] = proxy_list[i].rstrip()
        proxy_list.remove("")
    elif proxy_type == "static":
        with open("tools/proxies.txt","r") as f:
            proxy_list = f.readlines()
            for i in range(len(proxy_list)):
                proxy_list[i] = proxy_list[i].strip()
    return proxy_list#["","","",""]

def GetAllCookies():
    cookies = [f for f in listdir(getcwd()+"/tools/cookies/") if isfile(join(getcwd()+ "/tools/cookies/",f))]
    return cookies



def SpawnBot(settings,cookie,proxy):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument(f"--proxy-server={proxy}")
    driver = uc.Chrome(options=chrome_options)
    driver.get("https://www.twitch.tv/")
    logged_in = False
    # log in
    if cookie != None:
        cookie_loaded = pickle.load(open(f"tools/cookies/{cookie}","rb"))
        for part in cookie_loaded:
            if 'sameSite' in part:
                if part["sameSite"] == "None":
                    part["sameSite"] = "Strict"
                driver.add_cookie(part)
        
        time.sleep(1)
        driver.refresh()
        logged_in = True


    search_box = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/nav/div/div[2]/div/div/div/div/div[1]/div/div/div/input")

    search_box.send_keys(settings["streamer"])
    search_box.send_keys(Keys.ENTER)

    time.sleep(2)

    elements = driver.find_elements(By.TAG_NAME,"a")

    for element in elements:
        if element.text.lower() == settings["streamer"].lower():
            element.click()
            break
    
    
    time.sleep(3)

    try:
        element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/div/main/div[1]/div[3]/div/div/div[2]/div/div[2]/div/div[2]/div/div/div[4]/div/div[3]/button")
        element.click()
    except:
        print("[!] Streamer can we watched without aggreeing.")

    driver.execute_script("document.getElementsByClassName('persistent-player')[0].style='';")
    driver.execute_script("window.onblur = function() { window.onfocus() }")
    
    BotLogic(logged_in,driver)
