import sys, os, signal

sys.path.append(os.path.realpath('..'))
from MiningBot.AuditHistory.History import History
from MiningBot.EveInterface.Interface import Interface
from MiningBot.BotActions.Actions import Actions

import json, time
import socket
from loguru import logger


config_dir = r'../MiningBot/Configs/configs.json'
config = json.load(open(config_dir))[socket.gethostname()]
game = Interface(config_dir=config_dir)
bot = Actions(config_dir=config_dir, interface=game)
log = History(config_dir=config_dir)

logger.add(config['log_dir'] + '\\' + socket.gethostname() + "_" + sys.argv[0].split('/')[-1:][0] + "_{time}.log")
#logger.add(config['log_dir'] + '\\' + "miner_{time}.log")
logger.info('starting Miner...')
logger.info('waiting 5 seconds...')
time.sleep(5)
logger.info('starting...')

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
        bot.restart()
        log.log_main_loop_activity('Startup', "Login Sequence Starting")
        launcher_pid, game_pid = bot.login_sequience()
        logger.info(f'Main Loop-Launcher PID:{launcher_pid}, Game PID:{game_pid}')
        log.log_main_loop_activity('Startup', "Login Sequence Finished")

        # prep
        logger.info('Main Loop-Prep')
        log.log_main_loop_activity('Prep', "Get To Starting Point Starting")
        bot.get_to_starting_point()
        bot.reset_stale_mining_sites()
        log.log_main_loop_activity('Prep', "Get To Starting Point Finished")

        # mine
        logger.info('Main Loop-Mine') # should spend 23 hours a day here...
        log.log_main_loop_activity('Mine', "Mining Main Loop Starting")
        while True:
            try:
                bot.find_mining_spot_v2()
                bot.mine_till_full_v2()
                bot.unload()
            except Exception as e:
                logger.info(e)
                if e.args[0] == 'Connection Lost, Restart':
                    break # Recycle and repeat main loop
                elif e.args[0] == 'Fault Count Exceeded':
                    break
                elif 'PyAutoGUI fail-safe triggered from mouse moving to a corner of the screen' in e.args[0]:
                    bot.recover_mouse()
                pass
        log.log_main_loop_activity('Mine', "Mining Main Loop Finished")

        # recycle
        logger.info('Main Loop-Recycle Begin')
        log.log_main_loop_activity('Recycle', "Recycle Main Loop Starting")
        recycle(launcher_pid, game_pid)
        log.log_main_loop_activity('Recycle', "Recycle Main Loop Finished")
        logger.info('Main Loop-Sleeping 30 seconds...')
        time.sleep(30)
    except Exception as e:
        logger.error(f'Main Loop-Exception:{e}')
        log.log_main_loop_activity('Recycle', "Recycle Exception Main Loop Starting")
        recycle(launcher_pid, game_pid)
        log.log_main_loop_activity('Recycle', "Recycle Exception Main Loop Finished")
        logger.info('Main Loop-Sleeping 30 seconds...')
        time.sleep(30)
        pass
