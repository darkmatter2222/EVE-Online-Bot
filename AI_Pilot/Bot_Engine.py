import threading, time, json, socket, pyautogui, uuid, random
from AI_Pilot.Monitor_Interface.Monitors import get_monitor_spec, get_screen
from ML_Components.Universal_Prediction import Universal_Prediction
import numpy as np
from loguru import logger

config_dir = r'../AI_Pilot/ai_pilot_config.json'
config = json.load(open(config_dir))[socket.gethostname()]
UP = Universal_Prediction()



import tensorflow as tf
model2 = tf.keras.models.load_model(r"O:\source\repos\EVE-Online-Bot\TrainingPipelines\test_location.h5")

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

    # region ----- Training Data Collector
    def data_collector(self):
        combos = [
            (138, 100),
            (163, 100),
            (189, 100)
        ]
        data_root = r'O:\eve_models\training_data\unclass'
        for i in range(10):
            xy = random.choice(combos)
            pyautogui.moveTo(self.get_cords_with_offset(*xy))
            time.sleep(0.1)
            pyautogui.click(button='left')
            time.sleep(0.1)
            pyautogui.moveTo(self.get_cords_with_offset(*config['default_cords']))
            time.sleep(1)
            img = get_screen(config['monitor_number'])
            id = uuid.uuid1()
            img = img.crop((0, 0, 500, 600))
            img.save(f"{data_root}\\{id}.png")
            logger.info(f'Saved image:{id}')
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
        ui_callback('dock_at_destination_button', 'state', 'disabled')
        ui_callback('dock_at_destination_e_stop_button', 'state', 'active')
        logging_callback(f"Starting in 1 Second...")
        time.sleep(1)

        # TODO Train a model to find this?
        nav_point_xy = self.get_cords_with_offset(*config['next_waypoint_click_target'])
        itter_counter = 0
        while True:
            itter_counter += 1

            self.data_collector()
            time.sleep(10)
            continue


            if self.dock_at_destination_parms['e_stop']:
                break

            img = get_screen(config['monitor_number'])
            img = img.crop((0, 0, 500, 600))

            prediction = model2.predict(np.array([np.array(img)]))
            prediction = (prediction * np.array([600]))
            logger.info(f"prediction:{prediction}")
            pyautogui.moveTo(self.get_cords_with_offset(136, prediction[0]))
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
            if state_result['class'] == 'in_flight':
                click_target = None
                logging_callback(f"{itter_counter} - state:{state_result['class']} nav:{nav_result['class']}")
                # TODO Train a model to pos this?
                if nav_result['class'] == 'dock_now':
                    click_target = (nav_point_xy[0] + 50, nav_point_xy[1] + 75)
                elif nav_result['class'] == 'jump_though_first':
                    click_target = (nav_point_xy[0] + 50, nav_point_xy[1] + 25)
                elif nav_result['class'] == 'jump_through_second':
                    click_target = (nav_point_xy[0] + 50, nav_point_xy[1] + 50)
                elif nav_result['class'] == 'warp_to_dock_3':
                    click_target = (nav_point_xy[0] + 50, nav_point_xy[1] + 75)
                elif nav_result['class'] == 'warp_to_dock_4':
                    click_target = (nav_point_xy[0] + 50, nav_point_xy[1] + 100)
                else:
                    logger.info('do nothing nav...')

                if click_target is not None:
                    pyautogui.moveTo(click_target)
                    time.sleep(0.1)
                    pyautogui.click(button='left')

            elif state_result['class'] == 'in_hanger':
                break
            else:
                break
            time.sleep(0.1)
            pyautogui.moveTo(self.get_cords_with_offset(*config['default_cords']))
            time.sleep(0.1)
            pyautogui.click(button='left')
            self.data_collector()
            time.sleep(10)
        ui_callback('dock_at_destination_button', 'state', 'active')
        ui_callback('dock_at_destination_e_stop_button', 'state', 'disabled')
        logging_callback(f"Arrived")
    # endregion

