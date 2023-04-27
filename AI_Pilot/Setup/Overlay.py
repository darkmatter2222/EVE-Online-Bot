from tkinter import *
from AI_Pilot.Config_Management.Config_Management import save_config
import decimal
import numpy as np


def cell_dims(x1, y1, x2, y2):
    return x1, y1, x2 - x1, y2 - y1


def cell_dims_from_list(list_onbj):
    return cell_dims(list_onbj[0], list_onbj[1], list_onbj[2], list_onbj[3])


def drange(x, y, jump):
    while x < y:
        yield float(x)
        x += decimal.Decimal(jump)


def get_row_points(box, num_of_scanned_rows):
    space = (box[3] - box[1]) / num_of_scanned_rows
    row_points = list(drange(box[1], box[3], f'{space}'))
    final_row_points = list(np.rint(np.asarray(row_points)).astype(int))
    return final_row_points


def get_col_points(box, col_coefs):
    col_delta = box[2] - box[0]
    cols_points = []
    for col_coef in col_coefs:
        cols_points.append(col_delta * col_coef)

    temp_list = []
    for i in range(len(cols_points)):
        this_int = box[0]
        for j in range(i + 1):
            this_int += cols_points[j]
        temp_list.append(this_int)

    final_col_points = np.array(temp_list)
    final_col_points = list(np.rint(final_col_points).astype(int))
    final_col_points = [box[0]] + final_col_points + [box[2]]
    return final_col_points


def get_cells(x_range, y_range):
    cells = {}
    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            try:
                cells[i, j] = tuple([x, y, x + x_range[i + 1], y + y_range[j + 1]])
            except:  # lazy
                pass
    return cells


class overlay:
    def __init__(self, ag):
        self.root = Tk()
        self.ag = ag

        self.circle_size = 10

        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.wm_attributes("-transparentcolor", "#ffffff")
        self.root.configure(background='#ffffff')

        self.load_shapes(ag)

        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.end_move)
        self.root.bind("<B1-Motion>", self.move)

        self.root.geometry(
            f"{ag.monitor_spec['monitor_dims'][0]}x{ag.monitor_spec['monitor_dims'][1]}" +
            f"+{ag.monitor_spec['monitor_offset'][0]}+{ag.monitor_spec['monitor_offset'][1]}")
        self.root.title("Overlay")

        self.root.mainloop()

    def load_shapes(self, ag):
        self.canvas = Canvas(self.root, background="#ffffff", name="frame")
        for key in ag.static_screen_pos.keys():
            if 'click_target_' in key:
                self.draw_target(self.root, key, *ag.static_screen_pos[key])
            if 'range_' in key:
                self.draw_target(self.root, key + "_sub1", *ag.static_screen_pos[key][0:2], color='limegreen')
                self.draw_target(self.root, key + "_sub2", *ag.static_screen_pos[key][2:4], color='limegreen')
                self.drawbox(self.root, key, *ag.static_screen_pos[key])
            if '_grid_' in key:
                self.draw_grid(self.root, key, ag, key)

        self.canvas.pack(fill=BOTH, expand=1)

    def drawbox(self, root, text, top, left, bottom, right, color='#ff6600'):
        self.canvas.create_line(top, left, top, right,
                                top, right, bottom, right,
                                bottom, right, bottom, left,
                                bottom, left, top, left,
                                fill=color, width=1)

    def draw_movement(self, top, left, bottom, right, color='#ff6600'):
        self.canvas.create_line(top, left, bottom, right,
                                fill=color, width=1)

    def draw_grid(self, root, text, ag, key):
        y_range = get_row_points(self.ag.static_screen_pos[key], self.ag.static_screen_pos[key.replace('range_grid_', '') + '_count'])
        x_range = get_col_points(self.ag.static_screen_pos[key], self.ag.static_screen_pos[key.replace('range_grid_', '') + '_columns'])
        cells = get_cells(x_range, y_range)

        for i in cells.keys():
            self.drawbox( root, text, *list(cell_dims_from_list(cells[i]))),

    def draw_target(self, root, text, x, y, color='#ff6600'):
        Label(root, text=text, name=f"label_{text}").place(x=x - self.circle_size, y=y - self.circle_size * 3)
        self.canvas.create_oval(x - self.circle_size, y - self.circle_size, x + self.circle_size, y + self.circle_size,
                                fill=color, width=2, tag=f"circle_{text}")

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def end_move(self, event):
        key_edited = None
        new_x = 0
        new_y = 0
        for key in self.ag.static_screen_pos.keys():
            if 'click_target_' in key:
                moveable_canvases = self.canvas.find_withtag(f"circle_{key}")
                for canvas_id in moveable_canvases:
                    cords = self.canvas.coords(canvas_id)
                    x = cords[0] + self.circle_size
                    y = cords[1] + self.circle_size
                    if self.ag.static_screen_pos[key] != [x, y]:
                        print(key)
                        key_edited = key
                        new_x = x
                        new_y = y
                        break
                if key_edited is not None:
                    self.ag.static_screen_pos[key_edited] = [int(new_x), int(new_y)]
                    self.ag = save_config(self.ag)
                    break

            if 'range_' in key:
                moveable_canvases = self.canvas.find_withtag(f"circle_{key}_sub1")
                for canvas_id in moveable_canvases:
                    cords = self.canvas.coords(canvas_id)
                    x = cords[0] + self.circle_size
                    y = cords[1] + self.circle_size
                    if self.ag.static_screen_pos[key][0:2] != [x, y]:
                        print(key)
                        key_edited = key
                        new_x = x
                        new_y = y
                        break
                if key_edited is not None:
                    self.ag.static_screen_pos[key_edited] = [int(new_x), int(new_y)] + self.ag.static_screen_pos[
                                                                                           key_edited][2:4]
                    self.ag = save_config(self.ag)
                    break
                moveable_canvases = self.canvas.find_withtag(f"circle_{key}_sub2")
                for canvas_id in moveable_canvases:
                    cords = self.canvas.coords(canvas_id)
                    x = cords[0] + self.circle_size
                    y = cords[1] + self.circle_size
                    if self.ag.static_screen_pos[key][2:4] != [x, y]:
                        print(key)
                        key_edited = key
                        new_x = x
                        new_y = y
                        break
                if key_edited is not None:
                    self.ag.static_screen_pos[key_edited] = self.ag.static_screen_pos[key_edited][0:2] + [int(new_x),
                                                                                                          int(new_y)]
                    self.ag = save_config(self.ag)
                    break

        self.load_shapes(self.ag)

    def move(self, event):
        deltax = event.x - self._x
        deltay = event.y - self._y
        self._x = event.x
        self._y = event.y
        self.canvas.move("current", deltax, deltay)
