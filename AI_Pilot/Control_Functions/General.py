from loguru import logger
import numpy as np
from AI_Pilot.Control_Functions.Monitors import get_screen


def get_cords_with_offset(ag, x, y):
    # don't ask why i did it this way, it felt good.
    result = np.array([x, y]) + ag.monitor_spec['monitor_offset']
    return result[0], result[1]


def convert_to_baw(img, thresh=140):
    fn = lambda x: 255 if x > thresh else 0
    return img.convert('L').point(fn, mode='1')
