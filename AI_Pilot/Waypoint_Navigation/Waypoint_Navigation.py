from loguru import logger
import time
from AI_Pilot.Monitor_Interface.Monitors import get_screen
from AI_Pilot.General.General import get_game_state, get_cords_with_offset, beta_get_game_state_cake
from AI_Pilot.Mouse_Keyboard.Mouse_Keyboard import perform_move_click


def get_nav_options(ag, crop):
    # region ----- get gav options
    img = get_screen(ag)
    img = img.crop(tuple(crop))
    nav_result = ag.up.predict(img, 'nav_options')
    logger.info(nav_result)
    # endregion
    return nav_result


def get_y_waypoint_nav_pos(ag):
    # region ----- get waypoint y
    img = get_screen(ag)
    img_x = img.crop((0, 0, 500, 600))
    route_y_large_vert_class_v2_result = ag.up.predict(img_x, 'route_y_large_vert_class_v4')
    logger.info(route_y_large_vert_class_v2_result)
    # endregion
    return route_y_large_vert_class_v2_result


def navigate_one_waypoint(ag):
    state_result = beta_get_game_state_cake(ag)
    if state_result['class'] == 'in_flight':
        route_y_large_vert_class_v2_result = get_y_waypoint_nav_pos(ag)
        splits = route_y_large_vert_class_v2_result['class'].split('_')
        #target_y = int(route_y_large_vert_class_v2_result['class'])
        #nav_point_xy = get_cords_with_offset(ag, 136, target_y + 4)
        nav_point_xy = get_cords_with_offset(ag, int(splits[0]) + 4, int(splits[1]) + 4)
        perform_move_click(ag, pos=nav_point_xy, button='right', perform_offset=False)

        # TODO Train a model to crop this?
        template = [0, 0, 0, 0]
        template[1] = int(splits[1]) + ag.static_screen_pos['next_waypoint_menu_box_dims_from_click'][0]
        template[3] = template[1] + ag.static_screen_pos['next_waypoint_menu_box_dims_from_click'][1]

        template[0] = int(splits[0]) + ag.static_screen_pos['next_waypoint_menu_box_dims_from_click'][2]
        template[2] = template[0] + ag.static_screen_pos['next_waypoint_menu_box_dims_from_click'][3]

        nav_result = get_nav_options(ag, template)

        click_target = None
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
            perform_move_click(ag, pos=click_target, button='left', perform_offset=False)

    return state_result


def navigate_waypoints_to_end(ag, allow_dock=True):
    while True:
        state_result = navigate_one_waypoint(ag)
        # TODO, handle other states
        if state_result['class'] != 'in_flight' or not allow_dock:
            break
        else:
            time.sleep(10)
