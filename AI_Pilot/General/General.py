from ml_botting_core import universal_predictor
from loguru import logger
from AI_Pilot.Monitor_Interface.Monitors import get_screen


def get_game_state(general_config):
    # region ----- get game state
    up = universal_predictor()
    img = get_screen(general_config['monitor_number'])
    state_result = up.predict(img, 'game_state')
    logger.info(state_result)
    return state_result
    # endregion
