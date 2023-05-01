import os
import signal
import socket
import time

from loguru import logger

from AI_Pilot.Audit_History.History import History
from AI_Pilot.Bot_Engine.Bot_Engine import Bot_Engine
from AI_Pilot.Game_Functions.Game_Client.Game_Client import login_sequience


def recycle(launcher_pid, game_pid):
    try:
        os.kill(game_pid, signal.SIGTERM)
    except:
        pass
    time.sleep(1)
    try:
        os.kill(launcher_pid, signal.SIGTERM)
    except:
        pass


def start_mining(config_dir):
    Bot = Bot_Engine(config_dir=config_dir)
    host = socket.gethostname()
    Bot.ag.log = History(Bot.ag)
    logger.add(Bot.ag.this_config['general']['log_dir'] + '\\' + host + "Audit_History{time}.log")

    while True:
        launcher_pid = None
        game_pid = None
        try:
            # startup
            Bot.restart_fault_vars()
            Bot.ag.log.log_main_loop_activity('Startup', "Login Sequence Starting")
            launcher_pid, game_pid = login_sequience(Bot.ag)
            logger.info(f'Main Loop-Launcher PID:{launcher_pid}, Game PID:{game_pid}')
            Bot.ag.log.log_main_loop_activity('Startup', "Login Sequence Finished")

            # mine
            logger.info('Main Loop-Mine')  # should spend 23 hours a day here...
            Bot.ag.log.log_main_loop_activity('Mine', "Mining Main Loop Starting")
            try:
                Bot.start_mining()
            except Exception as e:
                logger.exception(e)
                try:
                    if e.args[0] == 'Connection Lost, Restart':
                        pass  # Recycle and repeat main loop
                    elif e.args[0] == 'Fault Count Exceeded':
                        pass
                    elif 'PyAutoGUI fail-safe triggered from mouse moving to a corner of the screen' in e.args[0]:
                        Bot.recover_mouse()
                        pass
                    else:
                        pass
                except Exception as ex:
                    logger.exception(ex)
                    pass

            Bot.ag.log.log_main_loop_activity('Mine', "Mining Main Loop Finished")

            # recycle
            logger.info('Main Loop-Recycle Begin')
            Bot.ag.log.log_main_loop_activity('Recycle', "Recycle Main Loop Starting")
            recycle(launcher_pid, game_pid)
            Bot.ag.log.log_main_loop_activity('Recycle', "Recycle Main Loop Finished")
            logger.info('Main Loop-Sleeping 30 seconds...')
            time.sleep(30)
        except Exception as e:
            logger.info(f'Main Loop-Exception:{e}')
            logger.exception(e)
            Bot.ag.log.log_main_loop_activity('Recycle', "Recycle Exception Main Loop Starting")
            recycle(launcher_pid, game_pid)
            Bot.ag.log.log_main_loop_activity('Recycle', "Recycle Exception Main Loop Finished")
            logger.info('Main Loop-Sleeping 30 seconds...')
            time.sleep(30)
