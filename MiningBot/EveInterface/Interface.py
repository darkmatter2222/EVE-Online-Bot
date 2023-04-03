import numpy as np
import pandas as pd
import mss
import mss.tools
from PIL import Image, ImageDraw
import cv2
import sys, os, decimal, json, time, uuid
from pytesseract import pytesseract
import socket
import tensorflow as tf
from loguru import logger

sys.path.append(os.path.realpath('..'))
from ML_Components.Universal_Prediction import Universal_Prediction
save_images = False
UC = Universal_Prediction()



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


def extract_values(img, cells, x_range, y_range, columns,
                   monitor_x_offset, monitor_y_offset,
                   click_target_offset_x, click_target_offset_y
                   ):
    frames = []
    for i in range(len(y_range) - 1):
        frame = {}
        for j in range(0, len(x_range) - 1):
            cell = cell_dims_from_list(list(cells[j, i]))
            cell_image = img.crop(cell)

            transcript = pytesseract.image_to_string(cell_image, lang='eng')

            frame[columns[j]] = transcript.replace('\n', '').replace('+', '').replace('>', '').replace('k m',
                                                                                                       ' km').replace(
                ',', '')
        frame['click_target'] = (
            cells[0, i][0] + click_target_offset_x + monitor_x_offset,
            cells[0, i][1] + click_target_offset_y + monitor_y_offset)  # offset by 10x10 pixels
        frames.append(frame)
    return pd.DataFrame(frames, columns=columns)


def extract_bool(img, cells, x_range, y_range, columns,
                 monitor_x_offset, monitor_y_offset,
                 click_target_offset_x, click_target_offset_y
                 ):
    frames = []
    for i in range(len(y_range) - 1):
        frame = {}
        for j in range(0, len(x_range) - 1):
            cell = cell_dims_from_list(list(cells[j, i]))
            cell_image = img.crop(cell)

            cell_image = convert_to_baw(cell_image, thresh=160)
            img_array = np.array(cell_image)

            percent_text = len(img_array[img_array == True]) / (
                    len(img_array[img_array == True]) + len(img_array[img_array == False]))

            populated = False
            if percent_text > 0.005:
                populated = True

            frame[columns[j]] = populated

        frame['click_target'] = (
            cells[0, i][0] + click_target_offset_x + monitor_x_offset,
            cells[0, i][1] + click_target_offset_y + monitor_y_offset)  # offset by 10x10 pixels
        frames.append(frame)
    return pd.DataFrame(frames, columns=columns)


def convert_to_baw(img, thresh=140):
    fn = lambda x: 255 if x > thresh else 0
    return img.convert('L').point(fn, mode='1')


class Interface:
    def __init__(self,
                 config_dir=r'..\Configs\configs.json'):
        self.config_dir = config_dir
        self.config = json.load(open(self.config_dir))[socket.gethostname()]
        self.screen = self.get_screen()

    def refresh_screen(self):
        self.screen = self.get_screen()

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

    def get_survey_scan_data(self, rows=6, refresh_screen=False, extract_type='values'):
        y_range = get_row_points(self.config['survey_scan_box'], rows)
        x_range = get_col_points(self.config['survey_scan_box'], self.config['survey_scan_box_columns'])
        cells = get_cells(x_range, y_range)

        if refresh_screen:
            self.screen = self.get_screen()

        id = uuid.uuid1()
        if save_images:
            self.screen.save(f"{self.config['log_dir']}\\images\\{id}.png")
            logger.info(f'Survey_Scan_Results Image_Saved: {id}')

        extract_columns = ['Locked', 'Ore', 'Quantity', 'Volume', 'Distance', 'click_target']

        result = None
        if extract_type == 'values':
            result = extract_values(img=self.screen, cells=cells, x_range=x_range,
                                    y_range=y_range, columns=extract_columns,
                                    monitor_x_offset=self.config['monitor_offset_x'],
                                    monitor_y_offset=self.config['monitor_offset_y'],
                                    click_target_offset_x=self.config['click_target_offset_x'],
                                    click_target_offset_y=self.config['click_target_offset_y'])
        else:
            result = extract_bool(img=self.screen, cells=cells, x_range=x_range,
                                  y_range=y_range, columns=extract_columns,
                                  monitor_x_offset=self.config['monitor_offset_x'],
                                  monitor_y_offset=self.config['monitor_offset_y'],
                                  click_target_offset_x=self.config['click_target_offset_x'],
                                  click_target_offset_y=self.config['click_target_offset_y'])

        return result

    def get_location_data(self, rows=13, refresh_screen=False):
        y_range = get_row_points(self.config['locations_box'], rows)
        x_range = get_col_points(self.config['locations_box'], self.config['locations_box_columns'])
        cells = get_cells(x_range[0:2], y_range)

        if refresh_screen:
            self.screen = self.get_screen()

        extract_columns = ['Name', 'click_target']

        return extract_values(img=self.screen, cells=cells, x_range=x_range[0:2],
                              y_range=y_range, columns=extract_columns,
                              monitor_x_offset=self.config['monitor_offset_x'],
                              monitor_y_offset=self.config['monitor_offset_y'],
                              click_target_offset_x=self.config['click_target_offset_x'],
                              click_target_offset_y=self.config['click_target_offset_y'])

    def get_search_data(self, rows=11, refresh_screen=False):
        y_range = get_row_points(self.config['search_location_grid'], rows)
        x_range = get_col_points(self.config['search_location_grid'], [1])
        cells = get_cells(x_range[0:2], y_range)

        if refresh_screen:
            self.screen = self.get_screen()

        extract_columns = ['Name', 'click_target']

        return extract_values(img=self.screen, cells=cells, x_range=x_range[0:2],
                              y_range=y_range, columns=extract_columns,
                              monitor_x_offset=self.config['monitor_offset_x'],
                              monitor_y_offset=self.config['monitor_offset_y'],
                              click_target_offset_x=self.config['click_target_offset_x'],
                              click_target_offset_y=self.config['click_target_offset_y'])

    def get_cargo_data(self, refresh_screen=False):
        if refresh_screen:
            self.screen = self.get_screen()

        cargo_bar = convert_to_baw(self.screen.crop(self.config['cargo_box']), thresh=20)
        img_array = np.array(cargo_bar)
        return len(img_array[img_array == True]) / (
                len(img_array[img_array == True]) + len(img_array[img_array == False]))

    def get_screen_class(self):
        clsf_name = 'game_state'

        self.screen = self.get_screen()

        id = uuid.uuid1()

        result = UC.predict(self.screen, clsf_name)
        result['id'] = id
        result['model'] = clsf_name

        return result

    def get_mining_tool_class(self):
        clsf_name = 'mining_tool_state'

        image_stack = []
        for i in range(10):
            img = self.get_screen()
            image_stack.append(np.array(img.crop(self.config['miners'])))
            time.sleep(0.1)
        final_img = Image.fromarray(np.concatenate(image_stack, axis=0))

        id = uuid.uuid1()

        result = UC.predict(final_img, clsf_name)
        result['id'] = id
        result['model'] = clsf_name

        return result
