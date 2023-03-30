import json, time
import pyautogui
import socket, uuid, time
import mss
import mss.tools
import tensorflow as tf
from PIL import Image, ImageDraw
import cv2
import numpy as np
import sys, os, decimal, json
sys.path.append(os.path.realpath('..'))
from MiningBot.EveInterface.Interface import Interface, get_cells, get_row_points, get_col_points
from loguru import logger


config_dir = r'../MiningBot/Configs/configs.json'
config = json.load(open(config_dir))[socket.gethostname()]
game = Interface(config_dir=config_dir)

logger.add(config['log_dir'] + '\\' + "miner_{time}.log")

classifiers = {}

for clsf_name in config['Classifiers'].keys():
    f = open(config['Classifiers'][clsf_name]['class_location'], "r")
    classifiers[clsf_name] = {
        'model': tf.keras.models.load_model(config['Classifiers'][clsf_name]['model_location']),
        'classes': json.loads(f.read()),
        'image_resize': tuple(config['Classifiers'][clsf_name]['image_resize']),
        'save_images': bool(config['Classifiers'][clsf_name]['save_images']),
    }

def get_screen():
    with mss.mss() as sct:
        mon = sct.monitors[config['monitor_number']]

        # The screen part to capture
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"],
            "mon": config['monitor_number'],
        }

        # Grab the data
        img = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        return img

def execute_clsf(img, clsf_name):
    img = img.resize(
        (classifiers[clsf_name]['image_resize'][1], classifiers[clsf_name]['image_resize'][0]),
        # TF trains backwards
        resample=Image.Resampling.NEAREST)
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    predictions = classifiers[clsf_name]['model'].predict(img_array)
    scores = tf.nn.softmax(predictions[0])
    result = {
        'argmax_index': np.argmax(scores),
        'value_at_argmax': scores[np.argmax(scores)].numpy(),
        'pass_general_tollerance': scores[np.argmax(scores)].numpy() > 0.5,
        'class': classifiers[clsf_name]['classes'][np.argmax(scores)],
        'classes': classifiers[clsf_name]['classes'],
        'scores': scores.numpy().tolist()
    }
    return result

def get_processed_cords(x, y):
    return x + config['monitor_offset_x'], y + config['monitor_offset_y']


while True:
    while True:
        send_home = False

        pyautogui.moveTo(get_processed_cords(1283, 133))
        time.sleep(0.1)
        pyautogui.click(button='left')
        time.sleep(5)
        search_df = game.get_search_data(rows=13, refresh_screen=True)
        search_df = search_df[(~search_df['Name'].str.contains('Jita')) & (~search_df['Name'].str.contains('Amsen'))].reset_index()
        del search_df['index']
        click_target = search_df.loc[0, 'click_target']
        pyautogui.moveTo(click_target)
        time.sleep(0.1)
        pyautogui.click(button='right')
        time.sleep(0.1)
        box_top_left = (935, 204)
        box_bottom_right = (1200, 600)
        img = get_screen()
        img = img.crop([box_top_left[0], box_top_left[1], box_bottom_right[0], box_bottom_right[1]])
        img.save(f'O:\\source\\repos\\EVE-Online-Bot\\training_data\\unclass\\{uuid.uuid1()}.png')

        dest_result = execute_clsf(img, 'set_dest')
        logger.info(dest_result)

        if dest_result['class'] == 'second_pos':
            pyautogui.moveTo(click_target[0] + 50, click_target[1] + 60)
        elif dest_result['class'] == 'seventh_pos':
            pyautogui.moveTo(click_target[0] + 50, click_target[1] + 234)
        elif dest_result['class'] == 'third_pos':
            pyautogui.moveTo(click_target[0] + 50, click_target[1] + 109)

        time.sleep(0.1)
        pyautogui.click(button='left')
        time.sleep(1)

        nav_point_xy = get_processed_cords(137, 378)
        while True:
            pyautogui.moveTo(nav_point_xy)
            time.sleep(0.1)
            pyautogui.click(button='right')
            time.sleep(0.1)
            box = (102, 289, 458, 658)
            img = get_screen()
            state_result = execute_clsf(img, 'game_state')
            logger.info(state_result)
            img = img.crop(box)
            logger.info('saving...')
            img.save(f'O:\\source\\repos\\EVE-Online-Bot\\training_data\\unclass\\{uuid.uuid1()}.png')
            nav_result = execute_clsf(img, 'nav_options')
            logger.info(nav_result)
            if state_result['class'] == 'in_flight':
                if nav_result['class'] == 'dock_now':
                    logger.info('Docking Now...')
                    pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 75)
                    time.sleep(0.1)
                    pyautogui.click(button='left')
                elif nav_result['class'] == 'jump_though_first':
                    logger.info('jumping fist pos...')
                    pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 25)
                    time.sleep(0.1)
                    pyautogui.click(button='left')
                elif nav_result['class'] == 'jump_through_second':
                    logger.info('jumping second pos...')
                    pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 50)
                    time.sleep(0.1)
                    pyautogui.click(button='left')
                elif nav_result['class'] == 'warp_to_dock_3':
                    logger.info('Warp To Dock pos...')
                    pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 75)
                    time.sleep(0.1)
                    pyautogui.click(button='left')
                elif nav_result['class'] == 'warp_to_dock_4':
                    logger.info('Warp To Dock pos...')
                    pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 100)
                    time.sleep(0.1)
                    pyautogui.click(button='left')
                else:
                    logger.info('do nothing nav...')
            elif state_result['class'] == 'in_hanger':
                time.sleep(2)

                pyautogui.moveTo(get_processed_cords(*config['hanger_target']))  # ensure we have mining hold selected
                time.sleep(0.1)
                pyautogui.click(button='left')
                time.sleep(1)

                pyautogui.moveTo(get_processed_cords(*config['click_and_drag_inv_box'][2:4]))  #
                time.sleep(0.1)
                x, y = get_processed_cords(*config['click_and_drag_inv_box'][0:2])
                pyautogui.dragTo(x, y, 1, button='left')
                time.sleep(0.1)
                pyautogui.moveTo(get_processed_cords(*config['Load_to_mininghold_click_and_drag_inv_line'][0:2]))
                time.sleep(0.1)
                x, y = get_processed_cords(*config['Load_to_mininghold_click_and_drag_inv_line'][2:4])
                pyautogui.dragTo(x, y, 1, button='left')

                time.sleep(2)

                img = get_screen()
                menu_result = execute_clsf(img, 'hanger_menus')
                logger.info(menu_result)
                if menu_result['class'] == 'set_quant':
                    pyautogui.moveTo(
                        get_processed_cords(*config['set_quant_target']))  # ensure we have mining hold selected
                    time.sleep(0.1)
                    pyautogui.click(button='left')
                    time.sleep(1)
                    send_home = True

                time.sleep(0.1)
                pyautogui.moveTo(get_processed_cords(*config['exit_hanger_target']))
                time.sleep(0.1)
                pyautogui.click(button='left')
                time.sleep(30)
                break
            else:
                logger.info('do nothing state...')
            time.sleep(0.1)
            pyautogui.moveTo(get_processed_cords(100, 100))
            time.sleep(0.1)
            pyautogui.click(button='left')
            time.sleep(10)
        if send_home:
            break

    search_df = game.get_search_data(rows=13, refresh_screen=True)
    search_df = search_df[search_df['Name'].str.contains('Jita')].reset_index()
    del search_df['index']
    click_target = search_df.loc[0, 'click_target']
    pyautogui.moveTo(click_target)
    time.sleep(0.1)
    pyautogui.click(button='right')
    time.sleep(0.1)
    pyautogui.moveTo(click_target[0] + 50, click_target[1] + 60)
    time.sleep(0.1)
    pyautogui.click(button='left')
    time.sleep(1)

    nav_point_xy = get_processed_cords(137, 378)
    while True:
        pyautogui.moveTo(nav_point_xy)
        time.sleep(0.1)
        pyautogui.click(button='right')
        time.sleep(0.1)
        box = (102, 289, 458, 658)
        img = get_screen()
        state_result = execute_clsf(img, 'game_state')
        logger.info(state_result)
        img = img.crop(box)
        nav_result = execute_clsf(img, 'nav_options')
        img.save(f'O:\\source\\repos\\EVE-Online-Bot\\training_data\\unclass\\{uuid.uuid1()}.png')
        logger.info(nav_result)
        if state_result['class'] == 'in_flight':
            if nav_result['class'] == 'dock_now':
                logger.info('Docking Now...')
                pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 75)
                time.sleep(0.1)
                pyautogui.click(button='left')
            elif nav_result['class'] == 'jump_though_first':
                logger.info('jumping fist pos...')
                pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 25)
                time.sleep(0.1)
                pyautogui.click(button='left')
            elif nav_result['class'] == 'jump_through_second':
                logger.info('jumping second pos...')
                pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 50)
                time.sleep(0.1)
                pyautogui.click(button='left')
            elif nav_result['class'] == 'warp_to_dock':
                logger.info('Warp To Dock pos...')
                pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 75)
                time.sleep(0.1)
                pyautogui.click(button='left')
            else:
                logger.info('do nothing nav...')
        elif state_result['class'] == 'in_hanger':
            time.sleep(2)

            pyautogui.moveTo(get_processed_cords(*config['mining_hold_target']))  # ensure we have mining hold selected
            time.sleep(0.1)
            pyautogui.click(button='left')
            time.sleep(1)

            pyautogui.moveTo(get_processed_cords(*config['click_and_drag_inv_box'][2:4]))  #
            time.sleep(0.1)
            x, y = get_processed_cords(*config['click_and_drag_inv_box'][0:2])
            pyautogui.dragTo(x, y, 1, button='left')
            time.sleep(0.1)
            pyautogui.moveTo(get_processed_cords(*config['Unload_nav_bot_click_and_drag_inv_line'][0:2]))
            time.sleep(0.1)
            x, y = get_processed_cords(*config['Unload_nav_bot_click_and_drag_inv_line'][2:4])
            pyautogui.dragTo(x, y, 1, button='left')
            time.sleep(0.1)
            pyautogui.moveTo(get_processed_cords(*config['exit_hanger_target']))
            time.sleep(0.1)
            pyautogui.click(button='left')
            time.sleep(30)
            break
        else:
            logger.info('do nothing state...')
        time.sleep(0.1)
        pyautogui.moveTo(get_processed_cords(100, 100))
        time.sleep(0.1)
        pyautogui.click(button='left')
        time.sleep(10)