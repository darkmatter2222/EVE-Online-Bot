import sys, os

sys.path.append(os.path.realpath('..'))

from MiningBot.EveInterface.Interface import Interface
from MiningBot.BotActions.Actions import Actions
import json
import socket

config_dir = r'../MiningBot/Configs/configs.json'
config = json.load(open(config_dir))[socket.gethostname()]
game = Interface(config_dir=config_dir)
bot = Actions(config_dir=config_dir)

while True:
    try:
        bot.find_mining_spot(game)
        bot.mine_till_full(game)
        bot.unload(game)
    except Exception as e:
        print(e)
        pass
