from AI_Pilot.Game_Functions.Common.UI_Table_Helpers import cell_dims, cell_dims_from_list, drange, get_row_points, get_col_points, get_cells
from AI_Pilot.Control_Functions.General import convert_to_baw
from pytesseract import pytesseract
import numpy as np
import pandas as pd

def extract_values(ag, img, cells, x_range, y_range, columns):
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
            cells[0, i][0] + 10 + ag.monitor_spec['monitor_offset'][0],
            cells[0, i][1] + 10 + ag.monitor_spec['monitor_offset'][1])  # offset by 10x10 pixels
        frames.append(frame)
    return pd.DataFrame(frames, columns=columns)


def extract_bool(ag, img, cells, x_range, y_range, columns):
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
            cells[0, i][0] + 10 + ag.monitor_spec['monitor_offset'][0],
            cells[0, i][1] + 10 + ag.monitor_spec['monitor_offset'][1])  # offset by 10x10 pixels
        frames.append(frame)
    return pd.DataFrame(frames, columns=columns)