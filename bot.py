from ast import arg
from email import message
from email.mime import audio
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pickle
from os import listdir, getcwd
from os.path import isfile,join
import requests
import random
import threading
import speech_recognition
import pyttsx3
import sounddevice as sd
from scipy.io.wavfile import write
from settings import settings

TYPING = False

def MessageSender(driver,message):
    TYPING = True
    time.sleep(1)
    element = driver.find_element(By.CLASS_NAME,"chat-input")
    element.click()
    cypher = 1
    while cypher<=10:
        try:
            element = driver.find_element(By.XPATH,f"//*[@id='live-page-chat']/div/div/div/div/div/section/div/div[{cypher}]/div[2]/div[1]/div[2]/div/div/div[1]/div/div/div/div/div[2]")
            break
        except:
            cypher +=1
    for letter in message:
        element.send_keys(letter)
        time.sleep(random.uniform(0,0.5))
    element.send_keys(Keys.ENTER)
    TYPING = False

def SpeechRecognitionHandler(driver,cookie):
    recognizer = speech_recognition.Recognizer()

    while True:
        try:
            fs = 44100  
            seconds = 3 
            sound_sample = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()  
            write('tools/sound_sample.wav', fs, sound_sample)#Convert file to be speech recognition ready?
            with speech_recognition.AudioFile("tools/sound_sample.wav") as rec:
                audio = recognizer.record(rec)
                recognized = recognizer.recognize_google(audio)
                recognized = recognized.lower()
                print("Text recognized:",recognized)
        except Exception as e:
            print("ERROR",e)


def MentionHandler(driver,cookie):
    responses = {}
    question = ""
    with open("tools/chatting/mention_responses.txt","r") as f:
        raw = f.readlines()
        for i in range(len(raw)):
            raw[i] = raw[i].strip()
            if ":" in raw[i]:
                question = raw[i].split(':')[1].split(':')[0]
                responses[question] = []
                continue
            responses[question].append(raw[i])
    #print(responses)
    

    while True:
        time.sleep(.2)
        try:
            mention = driver.find_elements(By.CLASS_NAME,"mention-fragment")[-1]
            mention = mention.text.lower()
            driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """,driver.find_elements(By.CLASS_NAME,"mention-fragment")[-1])
        except:
            mention = ""
        try:
            message = driver.find_elements(By.CLASS_NAME,"text-fragment")[-1]
            message = message.text
            try:
                message = message.split("?")[0]
            except:
                pass
            driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """,driver.find_elements(By.CLASS_NAME,"text-fragment")[-1])
        except:
            message = ""
        if mention != "":
            if mention.split("@")[-1] == cookie.split(".dump")[0].lower():
                print("[!] Somebody mentioned the bot, trying to find a response...")
                print("[!] Mention detected:",mention,"-",message)
                if message in responses:
                    #print("[!] Response needed...")
                    if not TYPING:
                        MessageSender(driver,responses[message][random.randint(0,len(responses[message])-1)])
                else:
                    #print("[!] Generic response needed")
                    if not TYPING:
                        MessageSender(driver,responses["GENERIC"][random.randint(0,len(responses["GENERIC"])-1)])
                
def GetRandomMessages():
    with open("tools/chatting/messages_to_send.txt") as f:
        messages = f.readlines()
        for i in range(len(messages)):
            messages[i] = messages[i].strip()
    return messages


def BotLogic(logged_in,driver,cookie):
    if logged_in:
        #Get all random messages
        messages = GetRandomMessages()
        #try to activate chat

        element = driver.find_element(By.CLASS_NAME,"chat-wysiwyg-input__editor") #wtf
        element.click()

        time.sleep(random.uniform(.5,2))
        cypher = 1
        while cypher <=10:
            try:
                element = driver.find_element(By.XPATH,f"/html/body/div[{cypher}]/div/div/div/div/div/div/div[3]/button")
                element.click()
            except:
                cypher+=1
                
            

    # spawn a thread to listen for @ts and for speech recognition
    if logged_in:
        mention_listener_thread = threading.Thread(target=MentionHandler,args=(driver,cookie))
        mention_listener_thread.start()

        speech_listener_thread = threading.Thread(target=SpeechRecognitionHandler,args=(driver,cookie))
        speech_listener_thread.start()

    actions = ["chat"]

    while True:
        time.sleep(60)
        if logged_in:
            action_selected = actions[random.randint(0,len(actions)-1)]
            if action_selected == "chat":
                if settings["bots_should_chat"] == "yes":
                    message_to_send = messages[random.randint(0,len(messages)-1)]
                    messages.remove(message_to_send)
                    if not TYPING:
                        MessageSender(driver,message_to_send) # CHECK TO SEE IF ALREADY TYPING SOMETHING SO YOU DON'T OVERLAP
        

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
    return ["","","",""] #proxy_list 

def GetAllCookies():
    cookies = [f for f in listdir(getcwd()+"/tools/cookies/") if isfile(join(getcwd()+ "/tools/cookies/",f))]
    return cookies



def SpawnBot(cookie,proxy):
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
    
    BotLogic(logged_in,driver,cookie)
