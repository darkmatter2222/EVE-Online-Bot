from MiningBot.EveInterface.Interface import Interface
import json, time
import pyautogui

config_dir = r'Configs/configs.json'
config = json.load(open(config_dir))
game = Interface(config_dir=config_dir)


def get_processed_cords(x, y):
    return x + config['monitor_offset_x'], y + config['monitor_offset_y']


# existing station...

resource_map = {}


def perform_mapping():
    global resource_map
    targets = ['Site1 P1', 'Site2 P1', 'Site3 P1']
    df = game.get_location_data(refresh_screen=True)

    for target in targets:
        xy = df.loc[df['Name'] == target, 'click_target'].values[0]
        pyautogui.moveTo(xy)
        time.sleep(0.1)
        pyautogui.click(button='right')
        time.sleep(0.1)
        pyautogui.moveTo(xy[0] + 50, xy[1] + 25)
        time.sleep(0.1)
        pyautogui.click(button='left')
        time.sleep(0.1)
        pyautogui.moveTo(1, 1)

    time.sleep(60)

# warp to playground and begin mapping
print(perform_mapping())
