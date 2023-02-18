import numpy as np
import mss
import mss.tools
from PIL import Image, ImageDraw
import cv2
import sys, os, decimal, json

sys.path.append(os.path.realpath('..'))


def drange(x, y, jump):
    while x < y:
        yield float(x)
        x += decimal.Decimal(jump)


def cell_dims(x1, y1, x2, y2):
    return x1, y1, x2 - x1, y2 - y1


def cell_dims_from_list(list_onbj):
    return cell_dims(list_onbj[0], list_onbj[1], list_onbj[2], list_onbj[3])


def get_row_points(box, num_of_scanned_rows):
    space = (box[3] - box[1]) / num_of_scanned_rows
    row_points = list(drange(box[1], box[3], f'{space}'))
    final_row_points = list(np.rint(np.asarray(row_points)).astype(int))
    return final_row_points


class Interface:
    def __init__(self,
                 config_dir=r'..\Configs\configs.json'):
        self.config_dir = config_dir
        self.config = json.load(open(self.config_dir))

    def get_screen(self):
        with mss.mss() as sct:
            mon = sct.monitors[self.config['monitor_number']]

            # The screen part to capture
            monitor = {
                "top": mon["top"],
                "left": mon["left"],
                "width": mon["width"],
                "height": mon["height"],
                "mon": self.config['monitor_number'],
            }

            # Grab the data
            img = np.array(sct.grab(monitor))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            return img

    def get_survey_scan_data(self, rows=6):
        y_range = get_row_points(self.config['survey_scan_box'], rows)


I = Interface()

I.get_screen().show()
