from loguru import logger
import numpy as np
from AI_Pilot.Monitor_Interface.Monitors import get_screen


def get_game_state(ag):
    # region ----- get game state
    img = get_screen(ag)
    state_result = ag.up.predict(img, 'game_state')
    logger.info(state_result)
    # endregion
    return state_result


def get_cords_with_offset(ag, x, y):
    # don't ask why i did it this way, it felt good.
    result = np.array([x, y]) + ag.monitor_spec['monitor_offset']
    return result[0], result[1]


def beta_get_game_state_cake(ag):
    img = get_screen(ag)
    result = ag.up.predict(img, 'game_state_cake_layer_1_v1')
    logger.info(result)
    min_threshold = ag.up.classifiers['game_state_cake_layer_1_v1']['meta']['decision_threshold']
    if float(result['value_at_argmax']) < min_threshold:
        result = ag.up.predict(img, 'game_state_cake_layer_2_v1')
        logger.info(result)

    return result
