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

while True:
    launcher_pid = None
    game_pid = None
    try:
        print('Initializing...')
        launcher_pid, game_pid = bot.login()
        print(f'Launcher PID:{launcher_pid}, Game PID:{game_pid}')
        bot.get_to_starting_point()
    except Exception as e:
        print(e)
        if e == 'Connection Lost, Restart':
            print('Complete Termination Beginning...')
            try:
                os.kill(game_pid, signal.SIGTERM)
            except:
                pass
            time.sleep(1)
            try:
                os.kill(launcher_pid, signal.SIGTERM)
            except:
                pass
            time.sleep(30)
            continue
        pass

    while True:
        try:
            bot.find_mining_spot()
            bot.mine_till_full()
            bot.unload()
        except Exception as e:
            print(e)
            if e == 'Connection Lost, Restart':
                break
            pass

    print('Complete Termination Beginning...')
    try:
        os.kill(game_pid, signal.SIGTERM)
    except:
        pass
    time.sleep(1)
    try:
        os.kill(launcher_pid, signal.SIGTERM)
    except:
        pass
    time.sleep(30)
