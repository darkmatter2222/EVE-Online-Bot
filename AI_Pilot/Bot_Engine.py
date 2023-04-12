import threading, time, json, socket, pyautogui, uuid, random
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
    def move_to_default_pos(self):
        pyautogui.moveTo(self.get_cords_with_offset(*config['default_cords']))
        time.sleep(0.1)


    def perform_click(self, button):
        pyautogui.click(button=button)
        time.sleep(0.1)

    def perform_move_click(self, pos, button='right', perform_offset=True, finish_at_default=False):
        # pos is tuple (x, y)
        if perform_offset:
            pos = self.get_cords_with_offset(*pos)
        pyautogui.moveTo(pos)
        time.sleep(0.1)
        self.perform_click(button)
        self.move_to_default_pos()
        return

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

            self.perform_move_click(pos=xy, button='left', perform_offset=True)
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

        itter_counter = 0
        while True:
            itter_counter += 1

            if self.dock_at_destination_parms['e_stop']:
                break

            # region ----- get waypoint y
            img = get_screen(config['monitor_number'])
            img_x = img.crop((0, 0, 500, 600))
            route_y_large_vert_class_v2_result = UP.predict(img_x, 'route_y_large_vert_class_v2')
            logger.info(route_y_large_vert_class_v2_result)
            # endregion

            target_y = int(route_y_large_vert_class_v2_result['class'])
            nav_point_xy = self.get_cords_with_offset(136, target_y + 4)
            self.perform_move_click(pos=nav_point_xy, button='right', perform_offset=False)

            # region ----- get game state
            img = get_screen(config['monitor_number'])
            state_result = UP.predict(img, 'game_state')
            logger.info(state_result)
            # endregion

            # TODO Train a model to crop this?
            template = config['next_waypoint_menu_box']
            template[1] = target_y - 90
            template[3] = template[1] + 369

            # region ----- get gav options
            img = img.crop(tuple(template))
            nav_result = UP.predict(img, 'nav_options')
            logger.info(nav_result)
            # endregion

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
                    self.perform_move_click(pos=click_target, button='left', perform_offset=False)

            elif state_result['class'] == 'in_hanger':
                break
            else:
                break
            self.move_to_default_pos()
            time.sleep(0.1)
            pyautogui.click(button='left')
            time.sleep(10)
        ui_callback('dock_at_destination_button', 'state', 'active')
        ui_callback('dock_at_destination_e_stop_button', 'state', 'disabled')
        logging_callback(f"Arrived")
    # endregion

