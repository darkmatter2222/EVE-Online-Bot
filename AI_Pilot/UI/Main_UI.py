import sys, os, socket, time
import tkinter as tk

from AI_Pilot.Bot_Engine.Bot_Engine import Bot_Engine
from loguru import logger


class AI_Pilot():
    def __init__(self, config_dir):
        self.bot = Bot_Engine(config_dir=config_dir)
        host = socket.gethostname()
        logger.add(
            self.bot.ag.this_config['general']['log_dir'] + '\\' + host + "Audit_History{time}.log")

        self.title = "AI Pilot V1"
        self.root = tk.Tk()
        # self.root.attributes('-topmost', True)
        self.root.resizable(width=True, height=True)

        # region ----- Column 0
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
        # endregion

        # region ----- column 4
        self.aggregate_resources_lf = tk.LabelFrame(self.root, text="aggregate Resources")
        self.aggregate_resources_lf.grid(row=0, column=1, sticky=tk.NW, padx=(10, 10), pady=(10, 10))
        self.aggregate_resources_start_button = tk.Button(self.aggregate_resources_lf, text="Start", width=30,
                                                           command=self.aggregate_resources_start)
        self.aggregate_resources_start_button.grid(row=0, column=0, sticky=tk.N, padx=(10, 10), pady=(5, 5))
        # endregion


    # region ----- universal functions
    def ui_element_change(self, element, element_property, value):
        self.__dict__[element][element_property] = value

    def ui_element_get_text(self, element):
        return self.__dict__[element].get(1.0,'end')
    # endregion

    # region ----- dock_at_dest
    def dock_at_destination_clear_log(self):
        self.dock_at_destination_lb.delete(0, tk.END)

    def dock_at_destination_append_log(self, entry):
        if len(self.dock_at_destination_log) > 6:
            del self.dock_at_destination_log[0]

        self.dock_at_destination_log.append(entry)
        self.dock_at_destination_clear_log()
        for record in self.dock_at_destination_log:
            self.dock_at_destination_lb.insert(0, f" {record}")

    def dock_at_destination_e_stop(self):
        self.bot.dock_at_destination_e_stop()

    def dock_at_destination_start(self):
        self.dock_at_destination_clear_log()
        self.bot.dock_at_destination_threaded(self.dock_at_destination_append_log, self.ui_element_change)

    # endregion

    # region ----- search_for_destination_start
    def search_for_destination_start(self):
        self.bot.move_ore_threaded(self)
        time.sleep(3)
        #Bot.dock_at_destination_threaded(self.dock_at_destination_append_log, self.ui_element_change)
    # endregion

    # region ----- start aggregate_resources
    def aggregate_resources_start(self):
        self.bot.aggregate_resources_start()
    # endregion



    def start(self):
        self.root.title(self.title)
        self.root.mainloop()


#AIP = AI_Pilot()
#AIP.start()
