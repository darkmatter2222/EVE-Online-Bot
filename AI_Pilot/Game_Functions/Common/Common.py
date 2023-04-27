import time
from AI_Pilot.Control_Functions.Mouse_Keyboard import perform_move_click
from AI_Pilot.Control_Functions.Monitors import get_screen
from AI_Pilot.Control_Functions.General import convert_to_baw
from loguru import logger
import numpy as np


def get_game_state(ag):
    # region ----- get game state
    img = get_screen(ag)
    state_result = ag.up.predict(img, 'game_state')
    logger.info(state_result)
    # endregion
    return state_result


def beta_get_game_state_cake(ag):
    img = get_screen(ag)
    result = ag.up.predict(img, 'game_state_cake_layer_1_v1')
    logger.info(result)
    min_threshold = ag.up.classifiers['game_state_cake_layer_1_v1']['meta']['decision_threshold']
    if float(result['value_at_argmax']) < min_threshold:
        result = ag.up.predict(img, 'game_state_cake_layer_2_v1')
        logger.info(result)

    return result


def exit_hanger(ag):
    perform_move_click(ag, ag.static_screen_pos['click_target_exit_hanger'], button='left')
    time.sleep(30)



