from AI_Pilot.Control_Functions.Monitors import get_screen
from AI_Pilot.Control_Functions.Mouse_Keyboard import perform_move_click, perform_move_ctrl_click, press_release_f_key, \
    move_to_default_pos
from AI_Pilot.Game_Functions.Common.UI_Table_Extraction import extract_bool
from AI_Pilot.Game_Functions.Common.Common import get_game_state
from AI_Pilot.Game_Functions.Cargo.Cargo import get_ship_root_cargo
from AI_Pilot.Game_Functions.Navigation.Locations_Navigation import get_location_table, dock_at_home
from AI_Pilot.Game_Functions.Common.UI_Table_Helpers import cell_dims, cell_dims_from_list, drange, get_row_points, \
    get_col_points, get_cells
import numpy as np
from loguru import logger
from PIL import Image
from datetime import datetime, timedelta
import time


def reset(ag):
    ag.fault_count = 0


def reset_stale(ag):
    ag.stale_mining_locations = {}


def get_miners_running(ag):
    image_stack = []
    for i in range(10):
        img = get_screen(ag)
        image_stack.append(np.array(img.crop(ag.static_screen_pos['range_miners'])))
        time.sleep(0.1)
    final_img = Image.fromarray(np.concatenate(image_stack, axis=0))
    result = ag.up.predict(final_img, 'mining_tool_state')
    return result


def execute_scan(ag):
    perform_move_click(ag, ag.static_screen_pos['click_target_scanner_button'], button='left')
    time.sleep(10)


def get_survey_scan_data(ag, force_scan=False):
    if force_scan:
        execute_scan(ag)

    y_range = get_row_points(ag.static_screen_pos['range_grid_survey_scan_box'],
                             ag.static_screen_pos['survey_scan_box_count'])
    x_range = get_col_points(ag.static_screen_pos['range_grid_survey_scan_box'],
                             ag.static_screen_pos['survey_scan_box_columns'])
    cells = get_cells(x_range, y_range)

    extract_columns = ['Locked', 'Ore', 'Quantity', 'Volume', 'Distance', 'click_target']

    img = get_screen(ag)

    df = extract_bool(ag, img=img, cells=cells, x_range=x_range,
                      y_range=y_range, columns=extract_columns)

    return df


def restart(ag):
    ag.fault_count = 10


def fault_tick(ag):
    ag.fault_count += 1
    logger.info(f'fault_count:{ag.fault_count}')
    if ag.fault_count > 10:
        message = 'Fault Count Exceeded'
        logger.error(message)
        raise Exception(message)


def get_scrub_scan_data(ag, force_scan=False):
    e_break = 0
    scan_df = None
    while True:
        e_break += 1
        time.sleep(1)
        scan_df = get_survey_scan_data(ag, force_scan=force_scan)
        logger.info(scan_df)
        scan_df = scan_df[0:4]
        scan_df = scan_df[scan_df['Ore'] == True].reset_index()
        del scan_df['index']
        logger.info(scan_df)
        target_to_expand = None

        if len(scan_df) == 1:
            if scan_df.loc[scan_df.index[0], 'Volume'] == False:
                target_to_expand = scan_df.loc[scan_df.index[0], 'click_target']
                logger.info('row 0 collapsed')

        if len(scan_df) > 1:
            # row one is colapsed, expand
            if scan_df.loc[scan_df.index[0], 'Volume'] == False and scan_df.loc[
                scan_df.index[1], 'Volume'] == False:
                target_to_expand = scan_df.loc[scan_df.index[0], 'click_target']
                logger.info('row 0 collapsed')

        if len(scan_df) > 2:
            if len(scan_df) == 3:
                if scan_df.loc[scan_df.index[2], 'Volume'] == False:
                    target_to_expand = scan_df.loc[scan_df.index[2], 'click_target']
                    logger.info('row 2 collapsed, end row')

            if len(scan_df) > 3:
                if scan_df.loc[scan_df.index[2], 'Volume'] == False and scan_df.loc[
                    scan_df.index[3], 'Volume'] == False:
                    target_to_expand = scan_df.loc[scan_df.index[2], 'click_target']
                    logger.info('row 2 collapsed, foloowd by another title')

        if e_break > 10:
            break

        if target_to_expand is not None:
            logger.info(f'expanding {target_to_expand}')
            perform_move_click(ag, target_to_expand, button='left', perform_offset=False)

        else:
            print('done')
            break

    return scan_df


def add_stale_field(ag, location_name, stale_duration_hours=2):
    ag.stale_mining_locations[location_name] = timedelta(hours=stale_duration_hours) + datetime.utcnow()


def reset_stale_mining_sites(ag):
    ag.stale_mining_locations = {}


def get_stale_mining_sites(ag):
    logger.info(f'pre - current stale mining sites:{ag.stale_mining_locations}')
    release_keys = []
    for key in ag.stale_mining_locations.keys():
        if datetime.utcnow() > ag.stale_mining_locations[key]:
            release_keys.append(key)
    for key in release_keys:
        del ag.stale_mining_locations[key]
    logger.info(f'post - current stale mining sites:{ag.stale_mining_locations}')
    return ag.stale_mining_locations.keys()


def get_valid_mining_targets(ag):
    targets = ag.static_screen_pos['mining_sites']
    stale_sites = get_stale_mining_sites(ag)
    final_list = [x for x in targets if x not in stale_sites]

    if len(final_list) == 0:
        final_list = ag.static_screen_pos['mining_sites']
        reset_stale_mining_sites(ag)
        logger.info('Ran out of targets, returning full list, resetting...')

    return final_list


def find_mining_spot_v2(ag, keep_finding=True):
    location_df = get_location_table(ag)
    logger.info(location_df)
    targets = get_valid_mining_targets(ag)

    for target in targets:
        if target not in list(location_df['Name']):
            message = f'Unable to find target in list:{target}'
            logger.info(message)
            logger.info(list(location_df['Name']))
            continue

        logger.info(f'Navigating to {target}')
        xy = location_df.loc[location_df['Name'] == target, 'click_target'].values[0]

        perform_move_click(ag, xy, button='right', perform_offset=False)

        perform_move_click(ag, (xy[0] + 50, xy[1] + 25), button='right', perform_offset=False)

        time.sleep(60)

        scan_df = get_scrub_scan_data(ag, force_scan=True)

        if len(scan_df[scan_df['Volume'] == True]) >= 2:
            return target
        else:
            logger.info(f'Marking Stale: {target}')
            add_stale_field(ag, target)

    if keep_finding == False:
        logger.info('keep_finding = False, sending Home.')
        dock_at_home()
        logger.info('Unable to locate Ore, Done...')
    return


def select_mining_hold(ag):
    perform_move_click(ag, ag.static_screen_pos['click_target_mining_hold'], button='left')


def mine_till_full_v2(ag):
    default_location = (10, 10)
    field_depleted = False
    mining_stale = False
    mining_cycle_start = datetime.utcnow()
    cycle_delay = 30
    race_condition_fault_count = 0
    while True:
        # validate we are in flgiht
        game_state = get_game_state(ag)
        if game_state['class'] != 'in_flight':
            break

        select_mining_hold(ag)  # Ensure we have our mining hold selected so we can read the inv space
        cargo_percent = get_ship_root_cargo(ag)
        logger.info(f'Cargo {cargo_percent:.2f}')

        # Stale Check
        # Something happend where the ore was still targeted however the miners were not activated.
        if mining_cycle_start + timedelta(minutes=30) < datetime.utcnow():
            mining_stale = True
            logger.info('Time Based mining_stale = True')
            ag.log.log_stale_mining('30 Minute Timeout')

        if cargo_percent > 0.9 or mining_stale:
            dock_at_home(ag)
            break

        scan_df = get_survey_scan_data(ag)

        logger.info('Full scan:')
        logger.info(scan_df)

        scan_df = scan_df[scan_df['Volume'] == True]
        logger.info('Volume scan subset:')
        logger.info(scan_df)
        count_valid_minables = len(scan_df.index)

        if len(scan_df) == 0:
            # field_depleted = True
            # logger.info('field_depleted = True')
            ag.log.log_field_depleted()
            logger.info('field_depleted - finding new mining spot...')
            find_mining_spot_v2(ag)
            logger.info('field_depleted - Spot Found, proceeding harvesting...')
            continue

        top_two_scan_df = scan_df[0:2]
        logger.info('Volume scan top 2 subset:')
        logger.info(top_two_scan_df)

        top_two_not_locked_scan_df = top_two_scan_df[~top_two_scan_df['Locked'] == True]

        logger.info(top_two_not_locked_scan_df)

        top_two_not_locked_scan_indicies = top_two_not_locked_scan_df.index  # top two rows that are not locked
        logger.info('Identifying what miner is running...')
        mining_tool_results = get_miners_running(ag)
        logger.info(mining_tool_results)
        time.sleep(1)

        # valid, desirable states
        if len(top_two_not_locked_scan_indicies) == 0 and mining_tool_results['class'] == 'both_running':
            # Do Nothing, All Good
            logger.info('Both Miners Running, All Good...')
        # Valid, last bit of a field:
        elif len(top_two_not_locked_scan_indicies) == 0 and \
                mining_tool_results['class'] in ['miner_1_running', 'miner_2_running']:
            # Do Nothing, All Good
            logger.info(f"{mining_tool_results['class']} miner Running, All Good... Finishing Field...")
        # valid, desirable states
        elif len(top_two_not_locked_scan_indicies) == 2 and mining_tool_results['class'] == 'no_miners_running':
            # fire up both miners
            for i in top_two_not_locked_scan_indicies:
                perform_move_ctrl_click(ag, scan_df.loc[i, 'click_target'], button='left', perform_offset=False)
                time.sleep(1)
            time.sleep(4)

            xy = None
            for i, index in enumerate(top_two_not_locked_scan_indicies):
                xy = scan_df.loc[index, 'click_target']

                perform_move_click(ag, xy, button='left', perform_offset=False)
                time.sleep(1)
                press_release_f_key(ag, i + 1)
                time.sleep(1)

            ag.log.log_extraction(action='Both_Miners')
            logger.info('Both Miners Started...')
        # valid, desirable states
        elif len(top_two_not_locked_scan_indicies) == 1 and \
                mining_tool_results['class'] in ['miner_1_running', 'miner_2_running']:

            perform_move_ctrl_click(ag, scan_df.loc[top_two_not_locked_scan_indicies[0], 'click_target'], button='left',
                                    perform_offset=False)
            time.sleep(4)
            perform_move_click(ag, scan_df.loc[top_two_not_locked_scan_indicies[0], 'click_target'], button='left',
                               perform_offset=False)
            time.sleep(1)

            if mining_tool_results['class'] == 'miner_1_running':
                # fire up miner 2
                press_release_f_key(ag, 2)
                time.sleep(1)
                mining_cycle_start = datetime.utcnow()
                ag.log.log_extraction(action='Miner_2')
                logger.info('Miner 2 Started...')
                pass
            elif mining_tool_results['class'] == 'miner_2_running':
                # fire up miner 1
                press_release_f_key(ag, 1)
                time.sleep(1)
                mining_cycle_start = datetime.utcnow()
                ag.log.log_extraction(action='Miner_1')
                logger.info('Miner 1 Started...')
            else:
                # should be impossible to get here, log just in case.
                # #aybe a race condition between scanning and mining tool check?
                logger.info(f'FAULT (L2) - skipping....')
                mining_stale = True
                ag.log.log_stale_mining('Invalid Miner State (L2)')
        # Catch All
        else:
            logger.info(f'FAULT (L1) race_condition_fault_count:{race_condition_fault_count}')
            race_condition_fault_count += 1
            if race_condition_fault_count > 5:
                mining_stale = True
                logger.info(f'FAULT (L1) - Going Stale')
                ag.log.log_stale_mining('Invalid Miner State (L1)')
                fault_tick(ag)
            else:
                # TODO handle this  and a full recycle at dock
                logger.info(f'FAULT (L1) - Another Chance')

        move_to_default_pos(ag)

        logger.info(f'Cycle Delay... {cycle_delay} seconds...')
        time.sleep(30)


def sub_mining_cycle(ag):
    if not hasattr(ag, 'stale_mining_locations'):
        ag.stale_mining_locations = {}
    if not hasattr(ag, 'fault_count'):
        ag.fault_count = 10

    # always asume we are not mining and we need to nav to starting point
    # find minig Spot
    find_mining_spot_v2(ag)
    mine_till_full_v2(ag)
