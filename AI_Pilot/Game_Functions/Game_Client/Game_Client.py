import os, wmi, signal, time
from loguru import logger
from AI_Pilot.Game_Functions.Common.Common import beta_get_game_state_cake, beta_get_game_state_cake_l2
from AI_Pilot.Control_Functions.Mouse_Keyboard import perform_move_click


def login_sequience(ag):
    # start launcher
    while True:
        logger.info('Beginning Login Sequence...')
        logger.info('Starting Launcher...')
        launcher_pid = start_launcher(ag)
        logger.info('Starting Game...')
        game_pid = start_game(ag)
        # check for connection issue?
        sc = beta_get_game_state_cake_l2(ag)
        logger.info(f'Screen Class:{sc}')
        if sc['class'] == 'char_select':
            logger.info('Selecting Char...')
            select_char(ag)
            time.sleep(60)
            break
        else:
            logger.info('Not on Char Selection Screen, Killing PIDs')
            try:
                os.kill(game_pid, signal.SIGTERM)
            except:
                pass
            time.sleep(1)
            try:
                os.kill(launcher_pid, signal.SIGTERM)
            except:
                pass
            logger.info('Failed to start and get to Char Screen, trying again...')
            time.sleep(30)
    return launcher_pid, game_pid


def login(ag):
    os.startfile(ag.general_config['eve_launcher'])
    time.sleep(30)
    perform_move_click(ag, (467, 694), button='left')
    time.sleep(30)
    perform_move_click(ag, (611, 364), button='left')
    logger.info('Login paused, 60 seconds...')
    time.sleep(60)
    logger.info('Login Finished, getting PIDs...')

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


def start_launcher(ag):
    f = wmi.WMI()
    killed = False
    for p in f.Win32_Process():
        if p.Name == 'evelauncher.exe':
            logger.info('evelauncher.exe found to be running, killing...')
            os.kill(p.ProcessId, signal.SIGTERM)
            killed = True

    if killed:
        time.sleep(10)

    os.startfile(ag.general_config['eve_launcher'])
    logger.info('starting launcher, waiting 30 seconds...')
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


def start_game(ag):
    f = wmi.WMI()
    killed = False
    for p in f.Win32_Process():
        if p.Name == 'exefile.exe':
            logger.info('exefile.exe found to be running, killing...')
            os.kill(p.ProcessId, signal.SIGTERM)
            killed = True

    if killed:
        time.sleep(10)

    perform_move_click(ag, (467, 694), button='left')

    logger.info('starting game, waiting 30 seconds...')
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


def select_char(ag):
    perform_move_click(ag, (611, 364), button='left')
