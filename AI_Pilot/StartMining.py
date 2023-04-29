import sys, os, decimal, json, socket, uuid, time, signal

sys.path.append(os.path.realpath('...'))
sys.path.append(os.path.realpath('..'))

from AI_Pilot.Bot_Engine import Bot_Engine
from AI_Pilot.Audit_History.History import History
from AI_Pilot.Game_Functions.Game_Client.Game_Client import login_sequience
from loguru import logger

config_dir = r'../AI_Pilot/ai_pilot_config_v2.json'

Bot = Bot_Engine(config_dir=config_dir)
host = socket.gethostname()
Bot.ag.log = History(Bot.ag)
logger.add(Bot.ag.this_config['general']['log_dir'] + '\\' + host + "Audit_History{time}.log")

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

        # prep
        #logger.info('Main Loop-Prep')
        #Bot.ag.log.log_main_loop_activity('Prep', "Get To Starting Point Starting")
        #Bot.get_to_starting_point()
        #Bot.reset_stale_mining_sites()
        #Bot.ag.log.log_main_loop_activity('Prep', "Get To Starting Point Finished")

        # mine
        logger.info('Main Loop-Mine') # should spend 23 hours a day here...
        Bot.ag.log.log_main_loop_activity('Mine', "Mining Main Loop Starting")
        try:
            Bot.start_mining()
        except Exception as e:
            logger.exception(e)
            try:
                if e.args[0] == 'Connection Lost, Restart':
                    break # Recycle and repeat main loop
                elif e.args[0] == 'Fault Count Exceeded':
                    break
                elif 'PyAutoGUI fail-safe triggered from mouse moving to a corner of the screen' in e.args[0]:
                    Bot.recover_mouse()
                    break
                else:
                    break
            except Exception as ex:
                logger.exception(ex)
                break





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
        pass