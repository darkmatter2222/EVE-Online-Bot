from MiningBot.EveInterface.Interface import Interface
import json
import pyautogui

config_dir = r'Configs/configs.json'
config = json.load(open(config_dir))
game = Interface(config_dir=config_dir)


def get_processed_cords(x, y):
    return x + config['monitor_offset_x'], y + config['monitor_offset_y']


# existing station...

resource_map = {}


def perform_mapping():
    df = game.get_location_data(refresh_screen=True)


# warp to playground and begin mapping
print(perform_mapping())
