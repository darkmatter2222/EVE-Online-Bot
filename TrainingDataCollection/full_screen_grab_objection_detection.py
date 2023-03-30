import sys, os, decimal, json
import socket, uuid, time

sys.path.append(os.path.realpath('..'))
from MiningBot.EveInterface.Interface import Interface, get_cells, get_row_points, get_col_points
from loguru import logger

config_dir = r'../MiningBot/Configs/configs.json'
config = json.load(open(config_dir))[socket.gethostname()]
game = Interface(config_dir=config_dir)

data_root = r'O:\source\repos\data_labeler\training_data\inventory'

logger.add(config['log_dir'] + '\\' + socket.gethostname() + "_" + sys.argv[0].split('/')[-1:][0] + "_{time}.log")

while True:
    img = game.get_screen()
    id = uuid.uuid1()
    img.save(f"{data_root}\\{id}.png")
    logger.info(f'Saved image:{id}')
    time.sleep(0.1)