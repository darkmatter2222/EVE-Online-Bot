import sys, os, decimal, json, socket, uuid, time
from AI_Pilot.Bot_Engine import Bot_Engine
from AI_Pilot.Audit_History import History
from loguru import logger

config_dir = r'../AI_Pilot/ai_pilot_config_v2.json'

Bot = Bot_Engine(config_dir=config_dir)
host = socket.gethostname()
Bot.ag.log = History()
logger.add(Bot.ag.this_config['general']['log_dir'] + '\\' + host + "Audit_History" + sys.argv[0].split('/')[-1:][0] + "Audit_History{time}.log")

Bot.start_mining()