from tkinter import *
from AI_Pilot.General.General import get_cords_with_offset
import sys, os, decimal, json


def cell_dims(x1, y1, x2, y2):
    return x1, y1, x2 - x1, y2 - y1


def cell_dims_from_list(list_onbj):
    return cell_dims(list_onbj[0], list_onbj[1], list_onbj[2], list_onbj[3])


def drawbox(root, canvas, text, top, left, bottom, right, color='#ff6600'):
    canvas.create_line(top, left, top, right,
                       top, right, bottom, right,
                       bottom, right, bottom, left,
                       bottom, left, top, left,
                       fill=color, width=1)


def draw_movement(top, left, bottom, right, color='#ff6600'):
    global canvas
    canvas.create_line(top, left, bottom, right,
                       fill=color, width=1)


def draw_target(root, canvas, text, x, y, color='#ff6600'):
    Label(root, text=text).place(x=x-10, y=y-30)
    canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill=color, width=2)


def overlay(ag):
    root = Tk()
    canvas = Canvas(root, background="#ffffff")

    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.wm_attributes("-transparentcolor", "#ffffff")
    root.configure(background='#ffffff')

    for key in ag.static_screen_pos.keys():
        if 'click_target_' in key:
            draw_target(root, canvas, key, *ag.static_screen_pos[key])
        if 'range_' in key:
            draw_target(root, canvas, key, *ag.static_screen_pos[key][0:2], color='limegreen')
            drawbox(root, canvas, key, *ag.static_screen_pos[key])


    canvas.pack(fill=BOTH, expand=1)
    root.geometry(
        f"{ag.monitor_spec['monitor_dims'][0]}x{ag.monitor_spec['monitor_dims'][1]}" +
        f"+{ag.monitor_spec['monitor_offset'][0]}+{ag.monitor_spec['monitor_offset'][1]}")
    root.title("Overlay")

    root.mainloop()
