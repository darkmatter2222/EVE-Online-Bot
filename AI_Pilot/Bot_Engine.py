import threading, time, json, socket, pyautogui
from AI_Pilot.Monitor_Interface.Monitors import get_monitor_spec, get_screen
from ML_Components.Universal_Prediction import Universal_Prediction
import numpy as np
from loguru import logger

config_dir = r'../AI_Pilot/ai_pilot_config.json'
config = json.load(open(config_dir))[socket.gethostname()]
UP = Universal_Prediction()

class Bot_Engine:
    def __init__(self):
        monitor_spec = get_monitor_spec(config['monitor_number'])
        self.monitor_dims = (monitor_spec['width'], monitor_spec['height'])  # x, y
        self.monitor_offset = np.array([monitor_spec['left'], monitor_spec['top']])  # x, y

        self.dock_at_destination_parms = {}

    # region ----- Common Functions
    def get_cords_with_offset(self, x, y):
        # don't ask why i did it this way, it felt good.
        result = np.array([x, y]) + self.monitor_offset
        return result[0], result[1]
    # endregion

    # region ----- dock_at_destination
    def dock_at_destination_e_stop(self):
        self.dock_at_destination_parms['e_stop'] = True

    def dock_at_destination_threaded(self, logging_callback, ui_callback):
        self.dock_at_destination_parms['thread'] = threading.Thread(target=self.dock_at_destination,
                                                              args=(logging_callback, ui_callback,))
        self.dock_at_destination_parms['thread'].start()

    def dock_at_destination(self, logging_callback, ui_callback):
        self.dock_at_destination_parms['e_stop'] = False
        ui_callback('dock_at_dest_button', 'state', 'disabled')
        ui_callback('dock_at_dest_e_stop_button', 'state', 'active')
        logging_callback(f"Starting in 1 Second...")
        time.sleep(1)

        # TODO Train a model to find this?
        nav_point_xy = self.get_cords_with_offset(*config['next_waypoint_click_target'])
        itter_counter = 0
        while True:
            itter_counter += 1
            if self.dock_at_destination_parms['e_stop']:
                break
            pyautogui.moveTo(nav_point_xy)
            time.sleep(0.1)
            pyautogui.click(button='right')
            time.sleep(0.1)
            img = get_screen(config['monitor_number'])
            state_result = UP.predict(img, 'game_state')
            logger.info(state_result)
            # TODO Train a model to crop this?
            img = img.crop(tuple(config['next_waypoint_menu_box']))
            nav_result = UP.predict(img, 'nav_options')
            logger.info(nav_result)
            time.sleep(5)

    # endregion

