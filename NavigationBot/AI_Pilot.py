import sys, os, decimal, json
import socket, uuid, time
import pyautogui
from tkinter import Frame, Canvas, Tk, BOTH, N, W, E, NW, Label, END, RIGHT, CENTER, Button, Listbox
from PIL import Image, ImageTk
import glob
import json
import threading
sys.path.append(os.path.realpath('..'))
from MiningBot.EveInterface.Interface import Interface, get_cells, get_row_points, get_col_points
from loguru import logger

config_dir = r'../MiningBot/Configs/configs.json'
config = json.load(open(config_dir))[socket.gethostname()]
game = Interface(config_dir=config_dir)

def get_processed_cords(x, y):
    return x + config['monitor_offset_x'], y + config['monitor_offset_y']



class AI_Pilot():
    def __init__(self):
        self.data_root = r'O:\source\repos\data_labeler\training_data\inventory'
        self.image_names = []
        self.image_data = []

        self.width = int(1920 / 6)
        self.height = int(1080 / 6)
        self.temp = ''
        self.title = "AI Pilot"
        self.root = Tk()
        self.e_stop_bool = False

        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(width=True, height=True)

        self.auto_to_dock_button = Button(self.root, text="Dock At Destination and Stop", width=30, command=self.auto_to_dock_threaded)
        self.auto_to_dock_button.grid(row=0, column=0, sticky=N)

        self.e_stop_button = Button(self.root, text="E Stop", width=30, command=self.e_stop)
        self.e_stop_button.grid(row=1, column=0, sticky=N)
        self.e_stop_button["state"] = "disabled"

    def e_stop(self):
        self.e_stop_bool = True

    def auto_to_dock_threaded(self):
        x = threading.Thread(target=self.auto_to_dock)
        x.start()

    def auto_to_dock(self):
        self.auto_to_dock_button["state"] = "disabled"
        self.e_stop_button["state"] = "active"
        nav_point_xy = get_processed_cords(137, 378)
        while True:
            if self.e_stop_bool:
                self.e_stop_bool = False
                break
            pyautogui.moveTo(nav_point_xy)
            time.sleep(0.1)
            pyautogui.click(button='right')
            time.sleep(0.1)
            box = (102, 289, 458, 658)
            img = game.get_screen()
            state_result = game.execute_clsf(img, 'game_state')
            print(state_result)
            img = img.crop(box)
            #print('saving...')
            #img.save(f'O:\\source\\repos\\EVE-Online-Bot\\training_data\\unclass\\{uuid.uuid1()}.png')
            nav_result = game.execute_clsf(img, 'nav_options')
            print(nav_result)
            if state_result['class'] == 'in_flight':
                if nav_result['class'] == 'dock_now':
                    print('Docking Now...')
                    pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 75)
                    time.sleep(0.1)
                    pyautogui.click(button='left')
                elif nav_result['class'] == 'jump_though_first':
                    print('jumping fist pos...')
                    pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 25)
                    time.sleep(0.1)
                    pyautogui.click(button='left')
                elif nav_result['class'] == 'jump_through_second':
                    print('jumping second pos...')
                    pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 50)
                    time.sleep(0.1)
                    pyautogui.click(button='left')
                elif nav_result['class'] == 'warp_to_dock_3':
                    print('Warp To Dock pos...')
                    pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 75)
                    time.sleep(0.1)
                    pyautogui.click(button='left')
                elif nav_result['class'] == 'warp_to_dock_4':
                    print('Warp To Dock pos...')
                    pyautogui.moveTo(nav_point_xy[0] + 50, nav_point_xy[1] + 100)
                    time.sleep(0.1)
                    pyautogui.click(button='left')
                else:
                    print('do nothing nav...')
            elif state_result['class'] == 'in_hanger':
                break
            else:
                break
            time.sleep(0.1)
            pyautogui.moveTo(get_processed_cords(100, 100))
            time.sleep(0.1)
            pyautogui.click(button='left')
            time.sleep(10)
        self.auto_to_dock_button["state"] = "active"
        self.e_stop_button["state"] = "disabled"

    def start(self):
        self.root.title(self.title)
        self.root.mainloop()

AIP = AI_Pilot()
AIP.start()