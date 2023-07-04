from AI_Pilot.Control_Functions.Mouse_Keyboard import perform_move_click
from AI_Pilot.Config_Management.Config_Management import load_config
from AI_Pilot.Control_Functions.Monitors import get_monitor_spec
import time
import numpy as np
import random


class active_globals():
    def __new__(cls, **args):  # make singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(active_globals, cls).__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self):
        if self.__initialized: return  # make singleton
        self.__initialized = True

def auto_range(config_dir):
    ag = active_globals()

    ag.config_dir = config_dir

    load_config(ag)

    ag.general_config = ag.this_config['general']
    ag.ml_botting_core_config = ag.this_config['ml_botting_core']
    ag.static_screen_pos = ag.this_config['static_screen_pos']

    monitor_spec = get_monitor_spec(ag)

    ag.monitor_spec = {
        "monitor_dims": (monitor_spec['width'], monitor_spec['height']),
        "monitor_offset": np.array([monitor_spec['left'], monitor_spec['top']])  # x, y
            }
    for i in range(100):
        print(i)

        top = ag.static_screen_pos['range_pd_top'].copy()
        top[0] += random.randint(0, 10)
        top[1] += random.randint(0, 10)
        top[2] -= random.randint(0, 10)
        top[3] += random.randint(0, 10)
        print(top)
        perform_move_click(ag, pos=(top[0], top[1]), button='left', perform_offset=True)
        perform_move_click(ag, pos=(top[0], top[3]), button='left', perform_offset=True)
        perform_move_click(ag, pos=(top[2], top[3]), button='left', perform_offset=True)
        perform_move_click(ag, pos=(top[2], top[1]), button='left', perform_offset=True)
        perform_move_click(ag, pos=(top[0], top[1]), button='left', perform_offset=True)

        top = ag.static_screen_pos['range_pd_bottom'].copy()
        top[0] += random.randint(0, 10)
        top[1] += random.randint(0, 10)
        top[2] -= random.randint(0, 10)
        top[3] += random.randint(0, 10)
        print(top)
        perform_move_click(ag, pos=(top[0], top[1]), button='left', perform_offset=True)
        perform_move_click(ag, pos=(top[0], top[3]), button='left', perform_offset=True)
        perform_move_click(ag, pos=(top[2], top[3]), button='left', perform_offset=True)
        perform_move_click(ag, pos=(top[2], top[1]), button='left', perform_offset=True)
        perform_move_click(ag, pos=(top[0], top[1]), button='left', perform_offset=True)

        time.sleep(1 + random.randint(0, 5))
        perform_move_click(ag, pos=ag.static_screen_pos['click_target_pd_submit_target'], button='left', perform_offset=True)
        time.sleep(2 + random.randint(0, 5))
        perform_move_click(ag, pos=ag.static_screen_pos['click_target_pd_submit_target'], button='left', perform_offset=True)
        time.sleep(2 + random.randint(0, 5))
        perform_move_click(ag, pos=ag.static_screen_pos['click_target_pd_submit_target'], button='left', perform_offset=True)
        time.sleep(5 + random.randint(0, 5))
