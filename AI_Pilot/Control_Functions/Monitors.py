import mss, cv2
import numpy as np
from PIL import Image


def get_monitor_spec(ag):
    with mss.mss() as sct:
        mon = sct.monitors[ag.general_config['monitor_number']]

        # The screen part to capture
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"],
            "monitor_number": ag.general_config['monitor_number'],
        }
    return monitor


def get_screen(ag):
    with mss.mss() as sct:
        mon = sct.monitors[ag.general_config['monitor_number']]

        # The screen part to capture
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"],
            "monitor_number": ag.general_config['monitor_number'],
        }

        # Grab the data
        img = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        return img
