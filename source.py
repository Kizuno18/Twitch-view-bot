import multiprocessing
import bot
import time
import random
from settings import settings

 
cookies = bot.GetAllCookies()
proxies = bot.GetProxyList(settings["proxy_type"])

bot_instances = []

def BotStarter(id,cookie_override):
    proxy = proxies[random.randint(0,len(proxies)-1)]
    proxies.remove(proxy)
    if cookie_override == None:
        if len(cookies) > 0:
            cookie = cookies[random.randint(0,len(cookies)-1)]
            cookies.remove(cookie)

            process = multiprocessing.Process(target=bot.SpawnBot,args=(cookie,proxy))
        else:
            process = multiprocessing.Process(target=bot.SpawnBot,args=(None,proxy))
            cookie = None
            
    else:
        process = multiprocessing.Process(target=bot.SpawnBot,args=(cookie_override,proxy))
        cookie = cookie_override
    process.start()
    bot_instances.append([process,id,cookie])



if __name__ == "__main__":
    for i in range(int(settings["bots"])):
        BotStarter(i,None)
        time.sleep(random.randint(1,10) * int(settings["bot_spawn_rate"]))
    
    while True:
        for i in range(int(settings["bots"])):
            if bot_instances[i][0].is_alive() == False:
                print("[!] Bot has died...","Restarting with cookie",bot_instances[i][2])
                bot_instances[i][0].close()
                if bot_instances[i][2] != None:
                    BotStarter(bot_instances[i][1],bot_instances[i][2])
                else:
                    BotStarter(bot_instances[i][1],None)
                bot_instances.remove(bot_instances[i])

        time.sleep(1)

