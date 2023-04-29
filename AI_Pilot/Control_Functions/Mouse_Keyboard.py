import time, pyautogui
from AI_Pilot.Control_Functions.General import get_cords_with_offset
from loguru import logger


def recover_mouse(ag):
    try:
        logger.info('recovering mouse...')
        pyautogui.FAILSAFE = False
        time.sleep(1)
        move_to_default_pos(ag)
        time.sleep(1)
        pyautogui.FAILSAFE = True
        logger.info('recovered')
    except:
        logger.info('failed recovery')
        pass
    time.sleep(5)

def move_to_default_pos(ag):
    pyautogui.moveTo(get_cords_with_offset(ag, *ag.static_screen_pos['click_target_default_cords']))
    time.sleep(0.1)


def perform_click(ag, button):
    pyautogui.click(button=button)
    time.sleep(0.1)


def perform_move_click(ag, pos, button='right', perform_offset=True, finish_at_default=True):
    # pos is tuple (x, y)
    if perform_offset:
        pos = get_cords_with_offset(ag, *pos)
    pyautogui.moveTo(pos)
    time.sleep(0.1)
    perform_click(ag, button)

    if finish_at_default:
        move_to_default_pos(ag)
    return

def perform_move_ctrl_click(ag, pos, button='right', perform_offset=True, finish_at_default=True):
    # pos is tuple (x, y)
    if perform_offset:
        pos = get_cords_with_offset(ag, *pos)
    pyautogui.moveTo(pos)
    time.sleep(0.1)
    pyautogui.keyDown('ctrl')
    perform_click(ag, button)
    time.sleep(0.1)
    pyautogui.keyUp('ctrl')

    if finish_at_default:
        move_to_default_pos(ag)
    return


def perform_drag(ag, start_pos, end_pos, button='left', perform_offset=True, finish_at_default=True):
    # pos is tuple (x, y)
    if perform_offset:
        start_pos = get_cords_with_offset(ag, *start_pos)
        end_pos = get_cords_with_offset(ag, *end_pos)
    pyautogui.moveTo(start_pos)
    time.sleep(0.1)
    pyautogui.dragTo(*end_pos, 1, button=button)
    time.sleep(0.1)

    if finish_at_default:
        move_to_default_pos(ag)
    return


def perform_range_select(ag, pos_start, pos_end, button='left', perform_offset=True):
    if perform_offset:
        pos_start = get_cords_with_offset(ag, *pos_start)
        pos_end = get_cords_with_offset(ag, *pos_end)
        pyautogui.moveTo(pos_start)
        time.sleep(0.1)
        pyautogui.dragTo(*pos_end, 1, button=button)
        time.sleep(0.1)

def press_release_f_key(ag, f_key_number):
    pyautogui.press(f'f{f_key_number}')
