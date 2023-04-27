from AI_Pilot.Control_Functions.Monitors import get_screen
import numpy as np
from PIL import Image
import time

def get_miners_running(ag):
    image_stack = []
    for i in range(10):
        img = get_screen(ag)
        image_stack.append(np.array(img.crop(ag.static_screen_pos['range_miners'])))
        time.sleep(0.1)
    final_img = Image.fromarray(np.concatenate(image_stack, axis=0))
    result = ag.up.predict(final_img, 'mining_tool_state')
    return result
