import configparser
import multiprocessing
import bot
import time
import random

config = configparser.ConfigParser()
config.read("config.ini")

settings = {}
settings["streamer"] = config["default"]["streamer"]
settings["bots"] = config["default"]["bots"]


if __name__ == "__main__":
    
    cookies = bot.GetAllCookies()

    for i in range(int(settings["bots"])):
        if len(cookies) > 0:
            cookie = cookies[random.randint(0,len(cookies)-1)]
            cookies.remove(cookie)
            process = multiprocessing.Process(target=bot.SpawnBot,args=(settings,cookie))
        else:
            process = multiprocessing.Process(target=bot.SpawnBot,args=(settings,None))
        process.start()

