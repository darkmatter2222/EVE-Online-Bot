import threading, time, json, socket, pyautogui, uuid, random
from AI_Pilot.Monitor_Interface.Monitors import get_monitor_spec, get_screen
from ML_Components.Universal_Prediction import Universal_Prediction
import numpy as np
from tqdm import tqdm
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
        self.search_for_destination_parms = {}

    # region ----- Common Functions

    def move_to_default_pos(self):
        pyautogui.moveTo(self.get_cords_with_offset(*config['default_cords']))
        time.sleep(0.1)

    def perform_click(self, button):
        pyautogui.click(button=button)
        time.sleep(0.1)

    def perform_move_click(self, pos, button='right', perform_offset=True, finish_at_default=True):
        # pos is tuple (x, y)
        if perform_offset:
            pos = self.get_cords_with_offset(*pos)
        pyautogui.moveTo(pos)
        time.sleep(0.1)
        self.perform_click(button)

        if finish_at_default:
            self.move_to_default_pos()
        return

    def perform_range_select(self, pos_start, pos_end, button='left', perform_offset=True):
        if perform_offset:
            pos_start = self.get_cords_with_offset(*pos_start)
            pos_end = self.get_cords_with_offset(*pos_end)
            pyautogui.moveTo(pos_start)
            time.sleep(0.1)
            pyautogui.dragTo(*pos_end, 1, button=button)
            time.sleep(0.1)



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

    # region ----- search_for_destination
    def move_ore_threaded(self, ui_class):
        self.search_for_destination_parms['thread'] = threading.Thread(target=self.move_ore,
                                                              args=(ui_class,))
        self.search_for_destination_parms['thread'].start()

    def move_ore(self, ui_class):
        source_staton = ui_class.ui_element_get_text('migrate_ore_tb1')
        destination_staton = ui_class.ui_element_get_text('migrate_ore_tb2')
        next_target = source_staton
        next_action = 'load'
        while True:
            self.perform_move_click(pos=(156, 130), button='left', perform_offset=True)
            pyautogui.write(next_target)
            time.sleep(3)
            pyautogui.press('enter')

            click_target = (1300, 650)
            self.perform_move_click(pos=click_target, button='right', perform_offset=True)
            box_top_left = (click_target[0] + 12, click_target[1] - 33)
            box_bottom_right = (click_target[0] + 256 + 12, click_target[1] + 396 - 33)
            img = get_screen(config['monitor_number'])
            img = img.crop([box_top_left[0], box_top_left[1], box_bottom_right[0], box_bottom_right[1]])
            set_dest_result = UP.predict(img, 'set_dest')

            if set_dest_result['class'] == 'second_pos':
                click_target = (click_target[0] + 50, click_target[1] + 60)
            elif set_dest_result['class'] == 'seventh_pos':
                click_target = (click_target[0] + 50, click_target[1] + 234)
            elif set_dest_result['class'] == 'third_pos':
                click_target = (click_target[0] + 50, click_target[1] + 109)

            self.perform_move_click(pos=click_target, button='left', perform_offset=True)
            time.sleep(2)
            # nav
            self.dock_at_destination(ui_class.dock_at_destination_append_log, ui_class.ui_element_change)
            time.sleep(2)
            # pick up ore
            if next_action == 'load':
                self.perform_move_click(pos=tuple(config['hanger_target']), button='left', perform_offset=True)
                time.sleep(1)
                self.perform_range_select(tuple(config['click_and_drag_inv_box'][2:4]),
                                          tuple(config['click_and_drag_inv_box'][0:2]))
                time.sleep(1)
                self.perform_range_select(tuple(config['Load_to_mininghold_click_and_drag_inv_line'][0:2]),
                                          tuple(config['ship_root_target']))
                time.sleep(1)
                img = get_screen(config['monitor_number'])
                menu_result = UP.predict(img, 'hanger_menus')
                if menu_result['class'] == 'set_quant':
                    self.perform_move_click(pos=tuple(config['set_quant_target']), button='left', perform_offset=True)
                time.sleep(1)
            else:
                self.perform_move_click(pos=tuple(config['ship_root_target']), button='left', perform_offset=True)
                time.sleep(1)
                self.perform_range_select(tuple(config['click_and_drag_inv_box'][2:4]),
                                          tuple(config['click_and_drag_inv_box'][0:2]))
                time.sleep(1)
                self.perform_range_select(tuple(config['Load_to_mininghold_click_and_drag_inv_line'][0:2]),
                                          tuple(config['hanger_target']))
                time.sleep(1)

            self.perform_move_click(pos=tuple(config['exit_hanger_target']), button='left', perform_offset=True)
            time.sleep(30)

            if next_target == source_staton:
                next_target = destination_staton
                next_action = 'unload'
            else:
                next_target = source_staton
                next_action = 'load'
















        # set dest
        # nav
        # drop off



        return



    def search_for_destination_threaded(self, ui_class):
        self.search_for_destination_parms['thread'] = threading.Thread(target=self.search_for_destination,
                                                              args=(ui_class))
        self.search_for_destination_parms['thread'].start()


    def search_for_destination(self, ui_class):

        time.sleep(1)
        search_string = "Amsen VI - Moon - Moon 1 Science and Trade Institute School"
        self.perform_move_click(pos=(156, 130), button='left', perform_offset=True)
        pyautogui.write(search_string)
        time.sleep(3)
        pyautogui.press('enter')
        self.perform_move_click(pos=(1300, 650), button='right', perform_offset=True)
        self.perform_move_click(pos=(1300 + 50, 650 + 65), button='right', perform_offset=True)
        pass
    # endregion




