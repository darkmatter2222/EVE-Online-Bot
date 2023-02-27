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

class Actions:
    def __init__(self, interface, config_dir=r'..\Configs\configs.json'):
        self.config_dir = config_dir
        self.config = json.load(open(self.config_dir))[socket.gethostname()]
        self.log = History(config_dir=config_dir)
        self.game = interface

    def current_screen_classification(self, report_fault=True):
        screen_class = self.game.get_screen_class(refresh_screen=True)
        print(f'Current Screen Classification:{screen_class}')
        if report_fault and \
                screen_class['class'] == 'connection_lost' and \
                screen_class['pass_general_tollerance']:
            raise Exception('Connection Lost, Restart')


    def get_processed_cords(self, x, y):
        return x + self.config['monitor_offset_x'], y + self.config['monitor_offset_y']

    def find_mining_spot(self, keep_finding=True):
        location_df = self.game.get_location_data(refresh_screen=True)
        while True:
            for target in self.config['mining_sites']:
                self.current_screen_classification()  # logging only
                # note this fails hard!!!! One OCR fail it skips the rest of the sequience
                if target not in list(location_df['Name']):
                    message = f'Unable to find target in list:{target}'
                    print(message)
                    print(list(location_df['Name']))
                    self.log.log_fault(message)
                    continue

                print(f'Navigating to {target}')
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

                print('scanning...')
                pyautogui.moveTo(self.get_processed_cords(*self.config['scanner_button_target']))
                time.sleep(0.1)
                pyautogui.click(button='left')
                time.sleep(7)
                scan_df = self.game.get_survey_scan_data(refresh_screen=True, extract_type='bool')
                if len(scan_df[scan_df['Quantity'] == True]) >= 2:
                    return target
            if keep_finding == False:
                print('keep_finding = False, sending Home.')
                target = 'Home'
                print(f'Navigating to {target}')
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
                print('Unable to locate Ore, Done...')
                return

    def mine_till_full(self):
        field_depleted = False
        mining_stale = False
        mining_cycle_start = datetime.utcnow()
        while True:
            self.current_screen_classification()  # logging only
            self.select_mining_hold()
            cargo_percent = self.game.get_cargo_data(refresh_screen=True)
            print(f'Cargo {cargo_percent:.2f}')

            # Stale Check
            # Something happend where the ore was still targeted however the miners were not activated.
            if mining_cycle_start + timedelta(minutes=30) < datetime.utcnow():
                mining_stale = True
                self.log.log_stale_mining()

            if cargo_percent > 0.9 or field_depleted or mining_stale:
                target = 'Home'
                location_df = self.game.get_location_data(refresh_screen=True)
                print(f'Navigating to {target}')
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
                break
            scan_df = self.game.get_survey_scan_data(refresh_screen=True, extract_type='bool')
            scan_df = scan_df[scan_df['Quantity'] == True]

            if len(scan_df) < 2:
                field_depleted = True

            snap_df = scan_df[0:2]
            snap_df = snap_df[~snap_df['Locked'] == True]
            indicies = snap_df.index
            if len(indicies) == 2:
                print('starting 2x...')
                mining_cycle_start = datetime.utcnow()
                self.log.log_extraction()
                for i in indicies:
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
                for i, index in enumerate(indicies):
                    xy = scan_df.loc[index, 'click_target']
                    pyautogui.moveTo(xy)
                    time.sleep(0.1)
                    pyautogui.click()
                    time.sleep(0.1)
                    pyautogui.press(f'f{i + 1}')
                    time.sleep(1)
                xy = (10, 10)
                pyautogui.moveTo(xy)
                print('started...')
                time.sleep(130) # adding in mining crystals... reducing to 130 from 175
            else:
                print('skipping...')
                time.sleep(30)

    def select_mining_hold(self):
        print('Opening Mining Hold...')
        pyautogui.moveTo(self.get_processed_cords(*self.config['mining_hold_target'])) # ensure we have mining hold selected
        time.sleep(0.1)
        pyautogui.click(button='left')
        time.sleep(1)

    def unload(self):
        self.current_screen_classification()  # logging only
        self.select_mining_hold()
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
        self.log.log_unload()
        self.exit_hanger()

    def exit_hanger(self):
        pyautogui.moveTo(self.get_processed_cords(*self.config['exit_hanger_target']))
        time.sleep(0.1)
        pyautogui.click(button='left')
        time.sleep(60)
        self.current_screen_classification()  # logging only

    def start_launcher(self):
        os.startfile(self.config['Eve_Launcher'])
        print('starting launcher, waiting 30 seconds...')
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
        pyautogui.moveTo(self.get_processed_cords(467, 694))
        time.sleep(0.1)
        pyautogui.click(button='left')
        print('starting game, waiting 30 seconds...')
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
            print('Beginning Login Sequence...')
            print('Starting Launcher...')
            launcher_pid = self.start_launcher()
            print('Starting Game...')
            game_pid = self.start_game()
            #check for connection issue?
            sc = self.game.get_screen_class(refresh_screen=True)
            print(f'Screen Class:{sc}')
            if sc['class'] == 'char_select' and sc['pass_general_tollerance']:
                print('Selecting Char...')
                self.select_char()
                time.sleep(60)
                break
            else:
                print('Not on Char Selection Screen, Killing PIDs')
                try:
                    os.kill(game_pid, signal.SIGTERM)
                except:
                    pass
                time.sleep(1)
                try:
                    os.kill(launcher_pid, signal.SIGTERM)
                except:
                    pass
                print('Failed to start and get to Char Screen, trying again...')
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
        print('Login paused, 60 seconds...')
        time.sleep(60)
        print('Login Finished, getting PIDs...')

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
        print('starting classifier...')
        screen_class_result = self.game.get_screen_class(refresh_screen=True)
        print(f'Current Screen:{screen_class_result}')
        if screen_class_result["class"] == 'in_hanger':
            self.exit_hanger()



