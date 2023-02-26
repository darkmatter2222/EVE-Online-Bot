import sys, os, signal

sys.path.append(os.path.realpath('..'))

from MiningBot.EveInterface.Interface import Interface
from MiningBot.BotActions.Actions import Actions
import json, time
import socket

config_dir = r'../MiningBot/Configs/configs.json'
config = json.load(open(config_dir))[socket.gethostname()]
game = Interface(config_dir=config_dir)
bot = Actions(config_dir=config_dir, interface=game)

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
        launcher_pid, game_pid = bot.login_sequience()
        print(f'Main Loop-Launcher PID:{launcher_pid}, Game PID:{game_pid}')

        # prep
        print('Main Loop-Prep')
        bot.get_to_starting_point()

        # mine
        print('Main Loop-Mine') # should spend 23 hours a day here...
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

        # recycle
        print('Main Loop-Recycle Begin')
        recycle(launcher_pid, game_pid)
        print('Main Loop-Sleeping 30 seconds...')
        time.sleep(30)
    except Exception as e:
        print(f'Main Loop-Exception:{e}')
        recycle(launcher_pid, game_pid)
        print('Main Loop-Sleeping 30 seconds...')
        time.sleep(30)
        pass
