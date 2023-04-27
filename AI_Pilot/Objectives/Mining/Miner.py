from AI_Pilot.Game_Functions.Common.Common import beta_get_game_state_cake
from AI_Pilot.Control_Functions.Mouse_Keyboard import perform_move_click


def mining_cycle(ag):
    state_result = beta_get_game_state_cake(ag)
    if state_result['class'] == 'in_flight':
        # do nothing
        pass
    elif state_result['class'] == 'in_hanger':
        # undock
        pass
    else:
        #TODO
        pass


def exit_hanger(ag):
    perform_move_click(ag.static_screen_pos['next_waypoint_menu_box_dims_from_click'])
    pyautogui.moveTo(self.get_processed_cords(*self.config['exit_hanger_target']))
    time.sleep(0.1)
    pyautogui.click(button='left')
    time.sleep(60)
    self.current_screen_classification()  # logging only






    # get state
    # get to space