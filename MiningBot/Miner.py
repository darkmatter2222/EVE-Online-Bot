import sys, os, signal

sys.path.append(os.path.realpath('..'))
from MiningBot.AuditHistory.History import History
from MiningBot.EveInterface.Interface import Interface
from MiningBot.BotActions.Actions import Actions
import json, time
import socket

config_dir = r'../MiningBot/Configs/configs.json'
config = json.load(open(config_dir))[socket.gethostname()]
game = Interface(config_dir=config_dir)
bot = Actions(config_dir=config_dir, interface=game)
log = History(config_dir=config_dir)

print('waiting 5 seconds...')
time.sleep(5)
print('starting...')

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
        log.log_main_loop_activity('Startup', "Login Sequence Starting")
        launcher_pid, game_pid = bot.login_sequience()
        print(f'Main Loop-Launcher PID:{launcher_pid}, Game PID:{game_pid}')
        log.log_main_loop_activity('Startup', "Login Sequence Finished")

        # prep
        print('Main Loop-Prep')
        log.log_main_loop_activity('Prep', "Get To Starting Point Starting")
        bot.get_to_starting_point()
        log.log_main_loop_activity('Prep', "Get To Starting Point Finished")

        # mine
        print('Main Loop-Mine') # should spend 23 hours a day here...
        log.log_main_loop_activity('Mine', "Mining Main Loop Starting")
        while True:
            try:
                bot.find_mining_spot()
                bot.mine_till_full()
                bot.unload()
            except Exception as e:
                print(e)
                if e.args[0] == 'Connection Lost, Restart':
                    break # Recycle and repeat main loop
                pass
        log.log_main_loop_activity('Mine', "Mining Main Loop Finished")

        # recycle
        print('Main Loop-Recycle Begin')
        log.log_main_loop_activity('Recycle', "Recycle Main Loop Starting")
        recycle(launcher_pid, game_pid)
        log.log_main_loop_activity('Recycle', "Recycle Main Loop Finished")
        print('Main Loop-Sleeping 30 seconds...')
        time.sleep(30)
    except Exception as e:
        print(f'Main Loop-Exception:{e}')
        log.log_main_loop_activity('Recycle', "Recycle Exception Main Loop Starting")
        recycle(launcher_pid, game_pid)
        log.log_main_loop_activity('Recycle', "Recycle Exception Main Loop Finished")
        print('Main Loop-Sleeping 30 seconds...')
        time.sleep(30)
        pass
