import configparser

config = configparser.ConfigParser()
config.read("config.ini")

settings = {}
settings["streamer"] = config["default"]["streamer"]
settings["bots"] = config["default"]["bots"]
settings["proxy_type"] = config["default"]["proxy_type"]
settings["bots_should_chat"] = config["default"]["bots_should_chat"]