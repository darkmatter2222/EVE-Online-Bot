import time
from AI_Pilot.Control_Functions.Mouse_Keyboard import perform_move_click, perform_range_select, perform_drag
from AI_Pilot.Control_Functions.Monitors import get_screen
from AI_Pilot.Control_Functions.General import convert_to_baw
from loguru import logger
import numpy as np


def get_ship_root_cargo(ag):
    img = get_screen(ag)
    cargo_bar = convert_to_baw(img.crop(ag.static_screen_pos['range_cargo_box']), thresh=20)
    img_array = np.array(cargo_bar)
    return len(img_array[img_array == True]) / (
            len(img_array[img_array == True]) + len(img_array[img_array == False]))


def unload_cargo(ag):
    perform_range_select(ag, ag.static_screen_pos['range_click_and_drag_inv_box'][2:4],
                         ag.static_screen_pos['range_click_and_drag_inv_box'][0:2])

    perform_drag(ag, ag.static_screen_pos['click_target_first_item_in_inventory'],
                 ag.static_screen_pos['click_target_hanger'])
