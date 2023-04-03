import sys, os, decimal, json, socket, uuid, time
import tkinter as tk

sys.path.append(os.path.realpath('..'))
from ML_Components.Universal_Prediction import Universal_Prediction
from AI_Pilot.Bot_Engine import Bot_Engine
from loguru import logger

config_dir = r'../AI_Pilot/ai_pilot_config.json'
config = json.load(open(config_dir))[socket.gethostname()]
logger.add(config['log_dir'] + '\\' + socket.gethostname() + "_" + sys.argv[0].split('/')[-1:][0] + "_{time}.log")
UC = Universal_Prediction()
Bot = Bot_Engine()

class AI_Pilot():
    def __init__(self):
        self.title = "AI Pilot"
        self.root = tk.Tk()
        self.root.resizable(width=True, height=True)

        self.dock_at_destination_lf = tk.LabelFrame(self.root, text="Dock at Destination")
        self.dock_at_destination_lf.grid(row=0, column=0, sticky=tk.NW, padx=(10, 10), pady=(10, 10))
        self.dock_at_destination_button = tk.Button(self.dock_at_destination_lf, text="Start", width=30,
                                          command=self.dock_at_destination_start)
        self.dock_at_destination_button.grid(row=0, column=0, sticky=tk.N, padx=(10, 10), pady=(10, 5))
        self.dock_at_destination_e_stop_button = tk.Button(self.dock_at_destination_lf, text="E Stop", width=30,
                                                 command=self.dock_at_destination_e_stop)
        self.dock_at_destination_e_stop_button.grid(row=1, column=0, sticky=tk.N, padx=(10, 10), pady=(5, 5))
        self.dock_at_destination_e_stop_button["state"] = "disabled"
        self.dock_at_destination_lb = tk.Listbox(self.dock_at_destination_lf, width=40)
        self.dock_at_destination_lb.grid(row=2, column=0, sticky=tk.N, padx=(5, 5), pady=(5, 10))
        self.dock_at_destination_log = []
        self.dock_at_destination_e_stop_bool = False

        self.migrate_ore_lf = tk.LabelFrame(self.root, text="Migrate Ore (Start in Space)")
        self.migrate_ore_lf.grid(row=0, column=1, sticky=tk.W, padx=(10, 10), pady=(10, 10))

        self.migrate_ore_lf_sub1 = tk.Frame(self.migrate_ore_lf)
        self.migrate_ore_lf_sub1.grid(row=0, column=0, sticky=tk.W, padx=(10, 10), pady=(0, 0))
        self.migrate_ore_l1 = tk.Label(self.migrate_ore_lf_sub1, text="From:")
        self.migrate_ore_l1.grid(row=0, column=0, sticky=tk.W, padx=(10, 10), pady=(10, 5))
        self.migrate_ore_tb1 = tk.Text(self.migrate_ore_lf_sub1, height=1, width=25)
        self.migrate_ore_tb1.insert(tk.INSERT, "Amsen VI - Moon - Moon 1 Science and Trade Institute School")
        self.migrate_ore_tb1.grid(row=0, column=1, sticky=tk.W, padx=(10, 10), pady=(10, 5))

        self.migrate_ore_lf_sub2 = tk.Frame(self.migrate_ore_lf)
        self.migrate_ore_lf_sub2.grid(row=1, column=0, sticky=tk.W, padx=(10, 10), pady=(0, 0))
        self.migrate_ore_l2 = tk.Label(self.migrate_ore_lf_sub2, text="To:")
        self.migrate_ore_l2.grid(row=0, column=0, sticky=tk.W, padx=(10, 10), pady=(5, 10))
        self.migrate_ore_tb2 = tk.Text(self.migrate_ore_lf_sub2, height=1, width=25)
        self.migrate_ore_tb2.insert(tk.INSERT, "Jita IV - Moon 4 - Caldari Navy Assembly Plant")
        self.migrate_ore_tb2.grid(row=0, column=1, sticky=tk.W, padx=(10, 10), pady=(10, 5))

        self.migrate_ore_start_button = tk.Button(self.migrate_ore_lf, text="Start", width=35,
                                          )
        self.migrate_ore_start_button.grid(row=2, column=0, sticky=tk.N, padx=(10, 10), pady=(10, 5))
        self.migrate_ore_e_stop_button = tk.Button(self.migrate_ore_lf, text="End", width=35,
                                          )
        self.migrate_ore_e_stop_button.grid(row=3, column=0, sticky=tk.N, padx=(10, 10), pady=(5, 5))
        self.migrate_ore_e_stop_button["state"] = "disabled"

        self.migrate_ore_lb = tk.Listbox(self.migrate_ore_lf, width=40)
        self.migrate_ore_lb.grid(row=4, column=0, sticky=tk.N, padx=(5, 5), pady=(5, 10))
        self.migrate_ore_log = []

    # region ----- ock_at_dest
    def dock_at_destination_clear_log(self):
        self.dock_at_destination_lb.delete(0, tk.END)

    def dock_at_destination_append_log(self, entry):
        if len(self.dock_at_destination_log) > 6:
            del self.dock_at_destination_log[0]

        self.dock_at_destination_log.append(entry)
        self.dock_at_destination_clear_log()
        for record in self.dock_at_destination_log:
            self.dock_at_destination_lb.insert(0, f" {record}")

    def ui_element_change(self, element, element_property, value):
        self.__dict__[element][element_property] = value

    def dock_at_destination_e_stop(self):
        Bot.dock_at_destination_e_stop()
        
    def dock_at_destination_start(self):
        self.dock_at_destination_clear_log()
        Bot.dock_at_destination_threaded(self.dock_at_destination_append_log, self.ui_element_change)
    # endregion

    def start(self):
        self.root.title(self.title)
        self.root.mainloop()

AIP = AI_Pilot()
AIP.start()
