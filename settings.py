import configparser

config = configparser.ConfigParser()
config.read("config.ini")

settings = {}
settings["streamer"] = config["default"]["streamer"]
settings["bots"] = config["default"]["bots"]
settings["proxy_type"] = config["default"]["proxy_type"]
settings["bots_should_chat"] = config["default"]["bots_should_chat"]
settings["bots_should_follow"] = config["default"]["bots_should_follow"]
settings["bot_spawn_rate"] = config["default"]["bot_spawn_rate"]
settings["bot_event_rate"] = config["default"]["bot_event_rate"]
settings["bots_chat_amongst"] = config["default"]["bots_chat_amongst"]
