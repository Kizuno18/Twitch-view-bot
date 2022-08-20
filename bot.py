import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import pickle
from os import execv, listdir, getcwd
from os.path import isfile,join
import requests
import random
import threading
import speech_recognition
import sounddevice as sd
from scipy.io.wavfile import write
import soundfile as sf
from settings import settings




def GetBotsThatCanBeMentioned():
    with open("tools/chatting/active_bots.txt","r") as f:
        active_bots = f.readlines()
        for i in range(len(active_bots)):
            active_bots[i] = active_bots[i].strip()
    return active_bots

def GetMessages(file):
    responses = {}
    question = ""
    with open(f"tools/chatting/{file}","r") as f:
        raw = f.readlines()
        for i in range(len(raw)):
            raw[i] = raw[i].strip()
            if ":" in raw[i]:
                question = raw[i].split(':')[1].split(':')[0]
                responses[question] = []
                continue
            responses[question].append(raw[i])
    return responses


BOT_MENTION_QUESTIONS = GetMessages("mention_responses.txt")

# To make bots chat just use mentions you already have in the mention_responses.txt
def MentionAnotherBot(driver,cookie):#Cookie to check to not mention yourself... Also need to find a way of what cookies are used...
    bots_available = GetBotsThatCanBeMentioned()
    bots_available.remove(cookie)
    bot_to_mention = bots_available[random.randint(0,len(bots_available)-1)].split(".")[0]
    
    BOT_MENTION_QUESTIONS.pop("GENERIC",None) # Remove GENERIC because that does not make sense...

    message_to_send = "@"+bot_to_mention+f" {list(BOT_MENTION_QUESTIONS.keys())[random.randint(0,len(BOT_MENTION_QUESTIONS.keys())-1)]}"
    print("Sending message",message_to_send)
    MessageSender(driver,message_to_send)

def RefreshAfterFollow(driver): # Needed so we can remove the Follower only chat that is a hinderence to MessageSender function
    driver.refresh()
    
    time.sleep(5)
    
    try:
        element = driver.find_element(By.XPATH,"//*[@id='root']/div/div[2]/div/main/div[1]/div[3]/div/div/div[2]/div/div[2]/div/div[2]/div/div/div[6]/div/div[3]/button")
        element.click()
    except:
        print("[!] Streamer can we watched without aggreeing.")

    driver.execute_script("document.getElementsByClassName('persistent-player')[0].style='';")
    driver.execute_script("window.onblur = function() { window.onfocus(); }")

def EnterStream(driver,override = None):

    if override == None:
        ways_to_enter = ["search","followed","direct"]
        way_chosen = ways_to_enter[random.randint(0,len(ways_to_enter)-1)]
    else:
        way_chosen = override

    if  way_chosen == "search":
        driver.get("https://www.twitch.tv/search?term=%s" % settings["streamer"])
        time.sleep(2)
        try:
            elements = driver.find_elements(By.TAG_NAME,"a")

            for element in elements:
                if element.text.lower() == settings["streamer"].lower():
                    element.click()
                    break
        except:
            print("[!] Failed to search for the streamer, going direct...")
            EnterStream(driver,"direct")

    elif way_chosen == "followed":
        driver.get("https://www.twitch.tv/directory/following")
        time.sleep(5)
        a_tags = driver.find_elements(By.TAG_NAME,"a")
        for a_tag in a_tags:
            p_tags = a_tag.find_elements(By.TAG_NAME,"p")
            for p_tag in p_tags:
                if p_tag.text.lower() == settings["streamer"].lower():
                    try:
                        element.click()
                        return
                    except:
                        print("[!] Failed entering the stream via followed tab, using search...")
                        EnterStream(driver,"search")
        print("[!] Not following streamer, entering via search...")
        EnterStream(driver,"search")
    elif way_chosen == "direct":
        driver.get("https://www.twitch.tv/%s" % settings["streamer"])


    

def SendFollow(driver):
    try:
        element = driver.find_element(By.XPATH,"//*[@id='live-channel-stream-information']/div/div/div[2]/div/div[2]/div[1]/div[2]/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/button")
        if element.get_attribute("aria-label") == "Follow":
            element.click()
            time.sleep(1)
            RefreshAfterFollow(driver)
        else:
            print("[!] Already following streamer...")
            return
    except:
        print("[!] Cannot find the follow button...\nTrying alternate button location...")
        try:
            element = driver.find_element(By.XPATH,"//*[@id='live-channel-stream-information']/div/div/div/div/div[2]/div[1]/div[2]/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/button")
            if element.get_attribute("aria-label") == "Follow":
                element.click()
                time.sleep(1)
                RefreshAfterFollow(driver)
            else:
                print("[!] Already following streamer...")
                return    
        except:
            pass
def MessageSender(driver,message):

    try:
        element = driver.find_element(By.XPATH,"//*[@id='live-page-chat']/div/div/div/div/div/section/div/div[5]/div[2]/div[1]/div[1]/div/div/div/div[2]/p")
        print("[!] Followers only chat, skipping message...")
        return
    except:
        pass

    try:
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
    except:
        print("[!] Message send failed, retrying in 10 seconds...")
        time.sleep(10)
        MessageSender(driver,message)

def SpeechRecognitionHandler(driver,cookie):
    recognizer = speech_recognition.Recognizer()
    responses = GetMessages("speech_recognition_responses.txt") # Change this to speech_recognition_resposnes.txt
    while True:
        try:
            fs = 44100  
            seconds = 5
            sound_sample = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()  
            write('tools/sound_sample.wav', fs, sound_sample)
            data, fs = sf.read('tools/sound_sample.wav')
            sf.write('tools/sound_sample.flac', data, fs)   
            with speech_recognition.AudioFile("tools/sound_sample.flac") as rec:
                audio = recognizer.record(rec)
                recognized = recognizer.recognize_google(audio)
                recognized = recognized.lower()
                #print("Text recognized:",recognized)
                if recognized in responses:
                    MessageSender(driver,responses[recognized][random.randint(0,len(responses[recognized])-1)])
        except:
            pass # If we don't know what is being said or we can't decode just skip

def MentionHandler(driver,cookie):
    responses = GetMessages("mention_responses.txt")
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
                    MessageSender(driver,responses[message][random.randint(0,len(responses[message])-1)])
                else:
                    #print("[!] Generic response needed")
                    MessageSender(driver,responses["GENERIC"][random.randint(0,len(responses["GENERIC"])-1)])
                
def GetRandomMessages():
    with open("tools/chatting/messages_to_send.txt") as f:
        messages = f.readlines()
        for i in range(len(messages)):
            messages[i] = messages[i].strip()
    return messages

MESSAGES = GetRandomMessages()

def BotLogic(logged_in,driver,cookie):

    EnterStream(driver)
    
    time.sleep(2)
    
    try:
        element = driver.find_element(By.XPATH,"//*[@id='root']/div/div[2]/div/main/div[1]/div[3]/div/div/div[2]/div/div[2]/div/div[2]/div/div/div[6]/div/div[3]/button")
        element.click()
    except:
        print("[!] Streamer can we watched without aggreeing.")
    driver.execute_script("document.getElementsByClassName('persistent-player')[0].style='';")
    driver.execute_script("window.onblur = function() { window.onfocus(); }")


    if logged_in:
        #try to activate chat

        element = driver.find_element(By.CLASS_NAME,"chat-wysiwyg-input__editor") 
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
        if settings["mention_recognition"] == "yes":
            mention_listener_thread = threading.Thread(target=MentionHandler,args=(driver,cookie))
            mention_listener_thread.start()

        if settings["speech_recognition"] == "yes":
            speech_listener_thread = threading.Thread(target=SpeechRecognitionHandler,args=(driver,cookie))
            speech_listener_thread.start()

    actions = ["chat","follow","mention_another_bot"]
    while True:
        time.sleep(random.randint(1,10)* int(settings["bot_event_rate"]))
        if logged_in:
            action_selected = actions[random.randint(0,len(actions)-1)]
            if action_selected == "chat":
                if settings["bots_should_chat"] == "yes":
                    if len(MESSAGES) > 0:
                        message_to_send = MESSAGES[random.randint(0,len(MESSAGES)-1)]
                        MESSAGES.remove(message_to_send)#This is to ensure that the bot does not send the same message twice...
                        MessageSender(driver,message_to_send)
                    else:
                        print("[!] No more unique messages... Skipping message send.")# add override for this
                else:
                    print("[!] Bot wanted to chat, stopped because bots_should_chat = no")
            if action_selected == "follow":
                if settings["bots_should_follow"] == "yes":
                    SendFollow(driver)
                else:
                    print("[!] Bot wanted to follow, stopped because bots_should_follow = no")
            if action_selected == "mention_another_bot":
                if settings["bots_chat_amongst"] == "yes":
                    if len(BOT_MENTION_QUESTIONS) > 0:
                        MentionAnotherBot(driver,cookie)
                    else:
                        print("[!] No more unique mentions... Skipping bot mention")#add override for this
                else:
                    print("[!] Bot wanted to mention another bot, stopped because bots_chat_amongst = no")
                
        

def GetProxyList(proxy_type):
    if proxy_type == "dynamic":
        proxy_list = requests.get("PROXY DOWNLOAD LINK GOES HERE").content.decode("UTF-8")
        proxy_list = proxy_list.split("\n")
        for i in range(len(proxy_list)):
            proxy_list[i] = proxy_list[i].rstrip()
        proxy_list.remove("")
    elif proxy_type == "static":
        with open("tools/proxies.txt","r") as f:
            proxy_list = f.readlines()
            for i in range(len(proxy_list)):
                proxy_list[i] = proxy_list[i].strip()
    return proxy_list 

def GetAllCookies():
    cookies = [f for f in listdir(getcwd()+"/tools/cookies/") if isfile(join(getcwd()+ "/tools/cookies/",f))]
    return cookies



def SpawnBot(cookie,proxy,should_mute):
    chrome_options = uc.ChromeOptions()
    if should_mute:
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
    
    with open("tools/chatting/active_bots.txt","a") as f:
        f.write(f"{cookie}\n")

    BotLogic(logged_in,driver,cookie)
