from AI_Pilot.General.General import get_ship_root_cargo
from AI_Pilot.Mouse_Keyboard.Mouse_Keyboard import perform_move_click
from loguru import logger


def Aggregate_Resources(ag):
    # get haul
    perform_move_click(ag, ag.static_screen_pos['click_target_ship_root'], button='left')
    cargo_percent = get_ship_root_cargo(ag)
    logger.info(f"Cargo Percent: {cargo_percent}")
    # search for ores

    # set destination
    # navigate
    # load up
    # check to make sure not over full
    # navigate to home or next dest
    return

