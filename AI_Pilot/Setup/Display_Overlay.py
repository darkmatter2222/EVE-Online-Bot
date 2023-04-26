import threading, time, json, socket, pyautogui, uuid, random
from AI_Pilot.Monitor_Interface.Monitors import get_monitor_spec
from AI_Pilot.Setup.Overlay import overlay
from ml_botting_core import universal_predictor
from AI_Pilot.Config_Management.Config_Management import load_config
import numpy as np

class active_globals():
    def __new__(cls, **args):  # make singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(active_globals, cls).__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self):
        if self.__initialized: return  # make singleton
        self.__initialized = True

ag = active_globals()

config_dir = r'..\..\AI_Pilot\ai_pilot_config_v2.json'

ag.config_dir = config_dir

load_config(ag)

ag.up = universal_predictor(config=ag.ml_botting_core_config)
monitor_spec = get_monitor_spec(ag)

ag.monitor_spec = {
    "monitor_dims": (monitor_spec['width'], monitor_spec['height']),
    "monitor_offset": np.array([monitor_spec['left'], monitor_spec['top']])  # x, y
}

o = overlay(ag)