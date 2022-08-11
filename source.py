
import configparser
import multiprocessing
import bot

import time

config = configparser.ConfigParser()
config.read("config.ini")

settings = {}
settings["streamer"] = config["default"]["streamer"]



if __name__ == "__main__":
    process = multiprocessing.Process(target=bot.SpawnBot,args=(settings,))
    process.start()

