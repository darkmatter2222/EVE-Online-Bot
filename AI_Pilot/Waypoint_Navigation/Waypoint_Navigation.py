from ml_botting_core import universal_predictor
from loguru import logger
from AI_Pilot.Monitor_Interface.Monitors import get_screen
from AI_Pilot.General.General import get_game_state

def get_y_waypoint_nav_pos(general_config):
    # region ----- get waypoint y
    up = universal_predictor()
    img = get_screen(general_config['monitor_number'])
    img_x = img.crop((0, 0, 500, 600))
    route_y_large_vert_class_v2_result = up.predict(img_x, 'route_y_large_vert_class_v2')
    logger.info(route_y_large_vert_class_v2_result)
    # endregion
    return route_y_large_vert_class_v2_result


def navigate_one_waypoint(general_config):
    state_result = get_game_state(general_config)
    if state_result['class'] == 'in_flight':
        route_y_large_vert_class_v2_result = get_y_waypoint_nav_pos(general_config)


def navigate_waypoints_to_end(general_config, allow_dock=True):
    pass