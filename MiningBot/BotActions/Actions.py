import numpy as np
import pandas as pd
import mss
import mss.tools
from PIL import Image, ImageDraw
import cv2
from datetime import datetime, timedelta
import subprocess, os, signal
import sys, os, decimal, json, time
import wmi
import pyautogui
import socket
from MiningBot.AuditHistory.History import History
from MiningBot.ScreenStateClassifier.ScreenState import ScreenClassifier

class Actions:
    def __init__(self, config_dir=r'..\Configs\configs.json'):
        self.config_dir = config_dir
        self.config = json.load(open(self.config_dir))[socket.gethostname()]
        self.log = History(config_dir=config_dir)
        self.clsf = ScreenClassifier(config_dir=config_dir)

    def get_processed_cords(self, x, y):
        return x + self.config['monitor_offset_x'], y + self.config['monitor_offset_y']

    def find_mining_spot(self, game, keep_finding=True):
        location_df = game.get_location_data(refresh_screen=True)
        while True:
            for target in self.config['mining_sites']:
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
                scan_df = game.get_survey_scan_data(refresh_screen=True, extract_type='bool')
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

    def mine_till_full(self, game):
        field_depleted = False
        mining_stale = False
        mining_cycle_start = datetime.utcnow()
        while True:
            cargo_percent = game.get_cargo_data(refresh_screen=True)
            print(f'Cargo {cargo_percent:.2f}')

            # Stale Check
            # Something happend where the ore was still targeted however the miners were not activated.
            if mining_cycle_start + timedelta(minutes=30) < datetime.utcnow():
                mining_stale = True
                self.log.log_stale_mining()

            if cargo_percent > 0.9 or field_depleted or mining_stale:
                target = 'Home'
                location_df = game.get_location_data(refresh_screen=True)
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
            scan_df = game.get_survey_scan_data(refresh_screen=True, extract_type='bool')
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
                time.sleep(175)
            else:
                print('skipping...')
                time.sleep(30)

    def unload(self, game):
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

    def login(self):
        os.startfile(self.config['Eve_Launcher'])
        #launcher_pid = subprocess.Popen(self.config['Eve_Launcher'], shell=True)
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
        print('Login Finished')
        return None, None

    def get_to_starting_point(self):
        print('starting classifier...')
        current_screen = self.clsf.get_screen_class()
        print(f'Current Screen:{current_screen}')
        if current_screen == 'in_hanger':
            self.exit_hanger()



