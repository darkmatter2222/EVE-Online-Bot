from AI_Pilot.Game_Functions.Common.Common import beta_get_game_state_cake
from AI_Pilot.Game_Functions.Cargo.Cargo import get_ship_root_cargo, unload_cargo
from AI_Pilot.Game_Functions.Common.Common import exit_hanger
from AI_Pilot.Game_Functions.Mining.Mining import get_miners_running, sub_mining_cycle, select_mining_hold, reset, reset_stale
from AI_Pilot.Game_Functions.Navigation.Locations_Navigation import dock_at_home
from loguru import logger
import time

cargo_unload_threshold = 0.8


def mining_cycle(ag):
    last_execution = None
    while True:
        select_mining_hold(ag)
        state_result = beta_get_game_state_cake(ag)
        cargo_full = True if get_ship_root_cargo(ag) > cargo_unload_threshold else False
        if state_result['class'] == 'in_flight' and cargo_full:
            dock_at_home(ag)
            last_execution = 'Dock'
        elif state_result['class'] == 'in_hanger' and cargo_full:
            # unload
            unload_cargo(ag)
            last_execution = 'Unload'
        elif state_result['class'] == 'in_hanger' and not cargo_full:
            # exit hanger
            exit_hanger(ag)
            last_execution = 'UnDock'
        elif state_result['class'] == 'in_flight' and not cargo_full:
            mining_tool_state_result = get_miners_running(ag)
            sub_mining_cycle(ag)

        time.sleep(30)

def restart_fault_vars(ag):
    reset(ag)

def reset_stale_mining_sites(ag):
    reset_stale(ag)
