from AI_Pilot.Game_Functions.Cargo.Cargo import get_ship_root_cargo, load_mining_cargo, unload_mining_cargo, get_hanger_menus
from AI_Pilot.Control_Functions.Mouse_Keyboard import perform_move_click
from AI_Pilot.Game_Functions.Common.Common import exit_hanger
from AI_Pilot.Game_Functions.Navigation.Assets_Navigation import get_assets_search_table, get_set_dest_options
from AI_Pilot.Game_Functions.Navigation.Waypoint_Navigation import navigate_waypoints_to_end
from AI_Pilot.Control_Functions.Monitors import get_screen
from AI_Pilot.Control_Functions.General import get_cords_with_offset
import pyautogui
from loguru import logger
from PIL import Image
import time


def Aggregate_Resources(ag):
    unload_at_jita(ag)
    while True:
        load_until_full(ag)
        unload_at_jita(ag)


def unload_at_jita(ag):
    # =============================================================
    perform_move_click(ag, ag.static_screen_pos['click_target_first_item_in_inventory'],
                       button='right', perform_offset=True)
    time.sleep(1)
    perform_move_click(ag, (400, 1000), button='left',
                       perform_offset=True)
    time.sleep(1)

    jita_name = 'Jita IV - Moon 4 - Caldari Navy Assembly Plant'

    perform_move_click(ag, pos=(156, 130), button='left', perform_offset=True)
    pyautogui.write(jita_name)
    pyautogui.press('enter')
    time.sleep(3)

    click_target = get_cords_with_offset(ag, 1500, 683)


    # =============================================================
    perform_move_click(ag, click_target, button='right', perform_offset=False)

    start_offset = [-10, 4]
    resolution = [256, 396]

    crop_dims = (click_target[0] - ag.monitor_spec['monitor_offset'][0] - start_offset[0],
                 click_target[1] - ag.monitor_spec['monitor_offset'][1] - start_offset[1],
                 click_target[0] - ag.monitor_spec['monitor_offset'][0] - start_offset[0] + resolution[0],
                 click_target[1] - ag.monitor_spec['monitor_offset'][1] - start_offset[1] + resolution[1])

    img = get_screen(ag)
    img = img.crop(crop_dims)

    set_dest_result = get_set_dest_options(ag, img)

    if set_dest_result['class'] == 'second_pos':
        click_target = (click_target[0] + 80, click_target[1] + 70)
    elif set_dest_result['class'] == 'third_pos':
        click_target = (click_target[0] + 80, click_target[1] + 110)
    elif set_dest_result['class'] == 'seventh_pos':
        click_target = (click_target[0] + 80, click_target[1] + 230)

    perform_move_click(ag, click_target, button='left', perform_offset=False)
    # =============================================================
    logger.info('navigating waypoints')
    navigate_waypoints_to_end(ag)
    time.sleep(10)
    # =============================================================
    logger.info('unload cargo.')
    unload_mining_cargo(ag)
    time.sleep(1)
    logger.info('exiting hanger.')
    exit_hanger(ag)

    return



def load_until_full(ag):
    full = False
    while True:
        # get haul
        # =============================================================
        perform_move_click(ag, ag.static_screen_pos['click_target_mining_hold'], button='left')
        cargo_percent = get_ship_root_cargo(ag)
        logger.info(f"Cargo Percent: {cargo_percent}")
        perform_move_click(ag, ag.static_screen_pos['click_target_search_assets_button'], button='left')
        time.sleep(1)
        # =============================================================
        df = get_assets_search_table(ag)
        logger.info(df)
        df = df[~df['Name'].str.contains('Jita|Amsen')].reset_index(drop=True)
        logger.info(df)
        perform_move_click(ag, df.loc[0, 'click_target'], button='right', perform_offset=False)

        start_offset = [-10, 4]
        resolution = [256, 396]

        crop_dims = (df.loc[0, 'click_target'][0] - ag.monitor_spec['monitor_offset'][0] - start_offset[0],
                     df.loc[0, 'click_target'][1] - ag.monitor_spec['monitor_offset'][1] - start_offset[1],
                     df.loc[0, 'click_target'][0] - ag.monitor_spec['monitor_offset'][0] - start_offset[0] + resolution[0],
                     df.loc[0, 'click_target'][1] - ag.monitor_spec['monitor_offset'][1] - start_offset[1] + resolution[1])

        img = get_screen(ag)
        img = img.crop(crop_dims)

        set_dest_result = get_set_dest_options(ag, img)

        click_target = (0, 0)
        if set_dest_result['class'] == 'second_pos':
            click_target = (df.loc[0, 'click_target'][0] + 80, df.loc[0, 'click_target'][1] + 70)
        elif set_dest_result['class'] == 'third_pos':
            click_target = (df.loc[0, 'click_target'][0] + 80, df.loc[0, 'click_target'][1] + 110)
        elif set_dest_result['class'] == 'seventh_pos':
            click_target = (df.loc[0, 'click_target'][0] + 80, df.loc[0, 'click_target'][1] + 230)

        perform_move_click(ag, click_target, button='left', perform_offset=False)
        # =============================================================
        logger.info('navigating waypoints')
        navigate_waypoints_to_end(ag)
        time.sleep(10)
        # =============================================================
        logger.info('loading cargo.')
        load_mining_cargo(ag)
        time.sleep(1)
        hanger_menus_result = get_hanger_menus(ag)

        if hanger_menus_result['class'] == 'set_quant':
            perform_move_click(ag, ag.static_screen_pos['click_target_set_quant_target'], button='left')
            full = True
            time.sleep(2)

        logger.info('exiting hanger.')
        exit_hanger(ag)
        if full:
            logger.info('all full!')
            break
    return


