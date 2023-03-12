import numpy as np
import pandas as pd
import mss
import mss.tools
from PIL import Image, ImageDraw
import cv2
from datetime import datetime, timedelta
import subprocess, os, signal
import sys, os, decimal, json, time
import pyautogui, wmi
import socket
from MiningBot.AuditHistory.History import History
from loguru import logger


class Actions:
    def __init__(self, interface, config_dir=r'..\Configs\configs.json'):
        self.config_dir = config_dir
        self.config = json.load(open(self.config_dir))[socket.gethostname()]
        self.log = History(config_dir=config_dir)
        self.stale_mining_locations = {}
        self.last_nav_target = ''
        self.game = interface

    def current_screen_classification(self, report_fault=True):
        screen_class = self.game.get_screen_class()
        logger.info(f'Current Screen Classification:{screen_class}')
        if report_fault and \
                screen_class['class'] == 'connection_lost' and \
                screen_class['pass_general_tollerance']:
            raise Exception('Connection Lost, Restart')

    def get_processed_cords(self, x, y):
        return x + self.config['monitor_offset_x'], y + self.config['monitor_offset_y']

    def navigate_home(self):
        target = 'Home'
        location_df = self.game.get_location_data(refresh_screen=True)
        logger.info(f'Navigating to {target}')
        xy = location_df.loc[location_df['Name'] == target, 'click_target'].values[0]
        pyautogui.moveTo(xy)
        time.sleep(0.1)
        pyautogui.click(button='right')
        time.sleep(0.1)
        pyautogui.moveTo(xy[0] + 50, xy[1] + 25)
        time.sleep(0.1)
        pyautogui.click(button='left')
        time.sleep(0.1)
        pyautogui.moveTo(10, 10)
        self.log.log_navigate(target)
        time.sleep(180)  # warning, docking can take some time.

    def add_stale_field(self, location_name, stale_duration_hours=2):
        self.stale_mining_locations[location_name] = timedelta(hours=stale_duration_hours) + datetime.utcnow()

    def get_stale_mining_sites(self):
        release_keys = []
        for key in self.stale_mining_locations.keys():
            if datetime.utcnow() > self.stale_mining_locations[key]:
                release_keys.append(key)
        for key in release_keys:
            del self.stale_mining_locations[key]
        return self.stale_mining_locations.keys()

    def get_valid_mining_targets(self):
        targets = self.config['mining_sites']
        stale_sites = self.get_stale_mining_sites()
        final_list = [x for x in targets if x not in stale_sites]

        if len(final_list) == 0:
            final_list = self.config['mining_sites']
            logger.info('Ran out of targets, returning full list')

        return final_list

    def find_mining_spot_v2(self, keep_finding=True):
        location_df = self.game.get_location_data(refresh_screen=True)
        logger.info(location_df)
        targets = self.get_valid_mining_targets()

        for target in targets:
            self.current_screen_classification()  # logging only
            # note this fails hard!!!! One OCR fail it skips the rest of the sequience
            if target not in list(location_df['Name']):
                message = f'Unable to find target in list:{target}'
                logger.info(message)
                logger.info(list(location_df['Name']))
                continue

            logger.info(f'Navigating to {target}')
            xy = location_df.loc[location_df['Name'] == target, 'click_target'].values[0]
            pyautogui.moveTo(xy)
            time.sleep(0.1)
            pyautogui.click(button='right')
            time.sleep(0.1)
            pyautogui.moveTo(xy[0] + 50, xy[1] + 25)
            time.sleep(0.1)
            pyautogui.click(button='left')
            time.sleep(0.1)
            pyautogui.moveTo(1, 1)
            time.sleep(60)
            self.log.log_navigate(target)

            logger.info('scanning...')
            pyautogui.moveTo(self.get_processed_cords(*self.config['scanner_button_target']))
            time.sleep(0.1)
            pyautogui.click(button='left')
            time.sleep(7)
            scan_df = self.game.get_survey_scan_data(refresh_screen=True, extract_type='bool')
            if len(scan_df[scan_df['Quantity'] == True]) >= 2:
                return target
            else:
                logger.info(f'Marking Stale: {target}')
                self.add_stale_field(target)

        if keep_finding == False:
            logger.info('keep_finding = False, sending Home.')
            self.navigate_home()
            logger.info('Unable to locate Ore, Done...')
            return

    def all_same(self, items):
        return all(items[0].equals(x) for x in items)

    def mine_till_full_v2(self):
        default_location = (10, 10)
        field_depleted = False
        mining_stale = False
        mining_cycle_start = datetime.utcnow()
        cycle_delay = 30
        while True:
            self.select_mining_hold()  # Ensure we have our mining hold selected so we can read the inv space
            cargo_percent = self.game.get_cargo_data(refresh_screen=True)
            logger.info(f'Cargo {cargo_percent:.2f}')

            # Stale Check
            # Something happend where the ore was still targeted however the miners were not activated.
            if mining_cycle_start + timedelta(minutes=30) < datetime.utcnow():
                mining_stale = True
                logger.info('Time Based mining_stale = True')
                self.log.log_stale_mining('30 Minute Timeout')

            if cargo_percent > 0.9 or field_depleted or mining_stale:
                self.navigate_home()
                break

            scan_df = self.game.get_survey_scan_data(refresh_screen=True, extract_type='bool')

            logger.info(scan_df)

            scan_df = scan_df[scan_df['Quantity'] == True]

            logger.info(scan_df)

            if len(scan_df) == 0:
                field_depleted = True
                self.log.log_field_depleted()
                logger.info('field_depleted = True')

            top_two_scan_df = scan_df[0:2]

            logger.info(top_two_scan_df)

            top_two_not_locked_scan_df = top_two_scan_df[~top_two_scan_df['Locked'] == True]

            logger.info(top_two_not_locked_scan_df)

            top_two_not_locked_scan_indicies = top_two_not_locked_scan_df.index  # top two rows that are not locked
            logger.info('Identifying what miner is running...')
            mining_tool_results = self.game.get_mining_tool_class()
            logger.info(mining_tool_results)
            time.sleep(1)

            # valid, desirable states
            if len(top_two_not_locked_scan_indicies) == 0 and mining_tool_results['class'] == 'both_running':
                # Do Nothing, All Good
                logger.info('Both Miners Running, All Good...')
                pass
            elif len(top_two_not_locked_scan_indicies) == 2 and mining_tool_results['class'] == 'no_miners_running':
                # fire up both miners
                for i in top_two_not_locked_scan_indicies:
                    pyautogui.moveTo(scan_df.loc[i, 'click_target'])
                    time.sleep(0.1)
                    pyautogui.keyDown('ctrl')
                    time.sleep(0.1)
                    pyautogui.click()
                    time.sleep(0.1)
                    pyautogui.keyUp('ctrl')
                    time.sleep(1)
                time.sleep(4)
                xy = None
                for i, index in enumerate(top_two_not_locked_scan_indicies):
                    xy = scan_df.loc[index, 'click_target']
                    pyautogui.moveTo(xy)
                    time.sleep(0.1)
                    pyautogui.click()
                    time.sleep(0.1)
                    pyautogui.press(f'f{i + 1}')
                    time.sleep(1)
                self.log.log_extraction(action='Both_Miners')
                logger.info('Both Miners Started...')
            elif len(top_two_not_locked_scan_indicies) == 1 and \
                    mining_tool_results['class'] in ['miner_1_running', 'miner_2_running']:

                # Start Targeting
                pyautogui.moveTo(scan_df.loc[top_two_not_locked_scan_indicies[0], 'click_target'])
                time.sleep(0.1)
                pyautogui.keyDown('ctrl')
                time.sleep(0.1)
                pyautogui.click()
                time.sleep(0.1)
                pyautogui.keyUp('ctrl')
                time.sleep(1)
                # wait for targeting...
                time.sleep(4)
                # reselect post targeting...
                pyautogui.moveTo(scan_df.loc[top_two_not_locked_scan_indicies[0], 'click_target'])
                time.sleep(0.1)
                pyautogui.click()
                time.sleep(1)

                if mining_tool_results['class'] == 'miner_1_running':
                    # fire up miner 2
                    pyautogui.press(f'f{2}')
                    time.sleep(1)
                    mining_cycle_start = datetime.utcnow()
                    self.log.log_extraction(action='Miner_2')
                    logger.info('Miner 2 Started...')
                    pass
                elif mining_tool_results['class'] == 'miner_2_running':
                    # fire up miner 1
                    pyautogui.press(f'f{1}')
                    time.sleep(1)
                    mining_cycle_start = datetime.utcnow()
                    self.log.log_extraction(action='Miner_1')
                    logger.info('Miner 1 Started...')
                else:
                    # should be impossible to get here, log just in case.
                    # #aybe a race condition between scanning and mining tool check?
                    logger.info(f'FAULT (L2) - skipping....')
                    mining_stale = True
                    self.log.log_stale_mining('Invalid Miner State (L2)')
            # invalid, restart states
            else:
                logger.info(f'FAULT (L1) - skipping....')
                mining_stale = True
                self.log.log_stale_mining('Invalid Miner State (L1)')

            pyautogui.moveTo(default_location)

            logger.info(f'Cycle Delay... {cycle_delay} seconds...')
            time.sleep(30)

    def select_mining_hold(self):
        logger.info('Opening Mining Hold...')
        pyautogui.moveTo(
            self.get_processed_cords(*self.config['mining_hold_target']))  # ensure we have mining hold selected
        time.sleep(0.1)
        pyautogui.click(button='left')
        time.sleep(1)

    def unload(self):
        self.current_screen_classification()  # logging only
        self.select_mining_hold()
        cargo_percent = self.game.get_cargo_data(refresh_screen=True)
        pyautogui.moveTo(self.get_processed_cords(*self.config['click_and_drag_inv_box'][2:4]))  #
        time.sleep(0.1)
        x, y = self.get_processed_cords(*self.config['click_and_drag_inv_box'][0:2])
        pyautogui.dragTo(x, y, 1, button='left')
        time.sleep(0.1)
        pyautogui.moveTo(self.get_processed_cords(*self.config['click_and_drag_inv_line'][0:2]))
        time.sleep(0.1)
        x, y = self.get_processed_cords(*self.config['click_and_drag_inv_line'][2:4])
        pyautogui.dragTo(x, y, 1, button='left')
        time.sleep(0.1)
        self.log.log_unload(cargo_percent)
        self.exit_hanger()

    def exit_hanger(self):
        pyautogui.moveTo(self.get_processed_cords(*self.config['exit_hanger_target']))
        time.sleep(0.1)
        pyautogui.click(button='left')
        time.sleep(60)
        self.current_screen_classification()  # logging only

    def start_launcher(self):
        f = wmi.WMI()
        killed = False
        for p in f.Win32_Process():
            if p.Name == 'evelauncher.exe':
                logger.info('evelauncher.exe found to be running, killing...')
                os.kill(p.ProcessId, signal.SIGTERM)
                killed = True

        if killed:
            time.sleep(10)

        os.startfile(self.config['Eve_Launcher'])
        logger.info('starting launcher, waiting 30 seconds...')
        time.sleep(30)
        f = wmi.WMI()
        pid = None
        for p in f.Win32_Process():
            if p.Name == 'evelauncher.exe':
                pid = p.ProcessId
                break

        if pid == None:
            raise Exception("Eve Launcher Did Not Start")
        return pid

    def start_game(self):
        f = wmi.WMI()
        killed = False
        for p in f.Win32_Process():
            if p.Name == 'exefile.exe':
                logger.info('exefile.exe found to be running, killing...')
                os.kill(p.ProcessId, signal.SIGTERM)
                killed = True

        if killed:
            time.sleep(10)

        pyautogui.moveTo(self.get_processed_cords(467, 694))
        time.sleep(0.1)
        pyautogui.click(button='left')
        logger.info('starting game, waiting 30 seconds...')
        time.sleep(30)
        f = wmi.WMI()
        pid = None
        for p in f.Win32_Process():
            if p.Name == 'exefile.exe':
                pid = p.ProcessId
                break

        if pid == None:
            raise Exception("Eve Launcher Did Not Start")
        return pid

    def select_char(self):
        pyautogui.moveTo(self.get_processed_cords(611, 364))
        time.sleep(0.1)
        pyautogui.click(button='left')

    def login_sequience(self):
        # start launcher
        while True:
            logger.info('Beginning Login Sequence...')
            logger.info('Starting Launcher...')
            launcher_pid = self.start_launcher()
            logger.info('Starting Game...')
            game_pid = self.start_game()
            # check for connection issue?
            sc = self.game.get_screen_class()
            logger.info(f'Screen Class:{sc}')
            if sc['class'] == 'char_select' and sc['pass_general_tollerance']:
                logger.info('Selecting Char...')
                self.select_char()
                time.sleep(60)
                break
            else:
                logger.info('Not on Char Selection Screen, Killing PIDs')
                try:
                    os.kill(game_pid, signal.SIGTERM)
                except:
                    pass
                time.sleep(1)
                try:
                    os.kill(launcher_pid, signal.SIGTERM)
                except:
                    pass
                logger.info('Failed to start and get to Char Screen, trying again...')
                time.sleep(30)
        return launcher_pid, game_pid

    def login(self):
        os.startfile(self.config['Eve_Launcher'])
        time.sleep(30)
        pyautogui.moveTo(self.get_processed_cords(467, 694))
        time.sleep(0.1)
        pyautogui.click(button='left')
        time.sleep(30)
        pyautogui.moveTo(self.get_processed_cords(611, 364))
        time.sleep(0.1)
        pyautogui.click(button='left')
        logger.info('Login paused, 60 seconds...')
        time.sleep(60)
        logger.info('Login Finished, getting PIDs...')

        launcher_pid = None
        game_pid = None

        f = wmi.WMI()

        for p in f.Win32_Process():
            if p.Name == 'exefile.exe':
                game_pid = p.ProcessId
            elif p.Name == 'evelauncher.exe':
                launcher_pid = p.ProcessId
            if launcher_pid is not None and game_pid is not None:
                break

        return launcher_pid, game_pid

    def get_to_starting_point(self):
        logger.info('starting classifier...')
        screen_class_result = self.game.get_screen_class()
        logger.info(f'Current Screen:{screen_class_result}')
        if screen_class_result["class"] == 'in_hanger':
            self.exit_hanger()
