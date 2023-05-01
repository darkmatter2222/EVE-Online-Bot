repo = 'https://github.com/darkmatter2222/EVE-Online-Bot'

# baseline startup
import argparse
import sys
import os
#from pathlib import Path
# logging w/o a log directory until sup app determines
from loguru import logger

#this_file_path = Path(__file__).parent.parent
#logger.info(f"Adding: {this_file_path} to path")
#Ssys.path.append(os.path.dirname(this_file_path))

this_file_path = os.path.abspath(__file__)
logger.info(f"Adding: {this_file_path} to path")
sys.path.append(os.path.dirname(this_file_path))

# AI Pilot Atrium Imports
from AI_Pilot.Objectives.Mining.StartMining import start_mining
from AI_Pilot.UI.Main_UI import AI_Pilot

# parse arguments
parser = argparse.ArgumentParser(prog='Start_AI_Pilot.py')
parser.add_argument("--config_file", metavar="config_file", type=str)
parser.add_argument("--headless_miner", metavar="headless_miner", type=str)
params = parser.parse_args()

if params.config_file is None:
    exception_message = f"Expecting valid '--config_file' path to be passed as an argument."
    exception_message += " The key '--config_file' was not found to be passed."
    exception_message += f" Visit '{repo}' for instructions."
    logger.exception(exception_message)
    raise Exception(exception_message)
elif not os.path.isfile(params.config_file):
    exception_message = f"Expecting valid '--config_file' path to be passed as an argument."
    exception_message += f" No file exists at:'{params.config_file}'."
    exception_message += f" Visit '{repo}' for instructions."
    logger.exception(exception_message)
    raise Exception(exception_message)

params.headless_miner = False if params.headless_miner is None else bool(eval(params.headless_miner))

if params.headless_miner:
    start_mining(params.config_file)
else:
    aip = AI_Pilot(params.config_file)
    aip.start()
