import cv2
import sys, os, decimal, json

sys.path.append(os.path.realpath('..'))
import json, time
import pandas as pd
import random
import matplotlib.pyplot as plt
import glob
import uuid
import matplotlib.pyplot as plt
import numpy as np
import random
import PIL, json
import tensorflow as tf
from PIL import Image
import socket
import pathlib
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageOps

from sklearn.metrics import confusion_matrix

from TrainingPipelines.ImageClassifier.ModelBuilder import build_and_train

import seaborn as sns
import mplcyberpunk
import json

plt.style.use("cyberpunk")
plt.rcParams['figure.facecolor'] = '#0d1117'
plt.rcParams['axes.facecolor'] = '#0d1117'
plt.rcParams['savefig.facecolor'] = '#0d1117'

cap = cv2.VideoCapture(f"C:\\Users\\ryans\\Videos\\2023-04-09 21-29-33.mp4")

output = cv2.VideoWriter(f"C:\\Users\\ryans\\Videos\\out2.avi", cv2.VideoWriter_fourcc(*'DIVX'), 30, (1920, 1080))

model2 = tf.keras.models.load_model(
    'O:\\eve_models\\training_data\\route_y_large_vert_class_v2\\route_y_large_vert_class_v2_model.h5', compile=False)
class_names = ['200', '210', '220', '250', '260', '270', '290', '310', '320', '330', '340', '350', '360', '370', '380', '390', '400', '410', '420', '430', '440', '460', '470', '480', '490']
reduction = 2

img_width = int(500 / reduction)
img_height = int(600 / reduction)

font = cv2.FONT_HERSHEY_SIMPLEX
# org
org = (100, 100)

# fontScale
fontScale = 0.75

# Blue color in BGR
color = (0, 0, 255)

# Line thickness of 2 px
thickness = 1


def normalize(arr, t_min, t_max):
    norm_arr = []
    diff = t_max - t_min
    diff_arr = max(arr) - min(arr)
    for i in arr:
        temp = (((i - min(arr)) * diff) / diff_arr) + t_min
        norm_arr.append(temp)
    return norm_arr


while (True):
    ret, frame = cap.read()
    if (ret):

        # adding filled rectangle on each frame
        # if random.randint(0, 9) < 1:
        #    id = uuid.uuid1()
        #    cv2.imwrite(f"temp\\{id}.png", frame)
        # frame = cv2.transpose(frame)
        color_converted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.transpose(frame)
        pil_image = Image.fromarray(color_converted)
        pil_image = pil_image.crop((0, 0, 500, 600))
        # img = pil_image.resize((img_width, img_height), resample=Image.Resampling.NEAREST)
        img = pil_image

        img = np.array([np.array(img)])
        prediction = model2.predict(img)
        argm = np.argmax(prediction)
        y_prediction = class_names[argm]

        frame = cv2.transpose(frame)

        y0, dy = 200, 20
        paylaod = "Model Output: \n" + json.dumps(list(prediction[0].astype(str)), indent=1)
        for i, line in enumerate(paylaod.split('\n')):
            y = y0 + i * dy
            if i-2 == argm:
                color = (0, 255, 0)
            else:
                color = (0,0,255)

            frame = cv2.putText(frame, line, (1200, y), font, fontScale, color, thickness, cv2.LINE_AA)

        frame = cv2.putText(frame, 'AI trying to locate the y axis of the waypoint bar', (100, 100), font, 2,
                            (0, 255, 0), 2, cv2.LINE_AA)
        cv2.line(frame, (0, int(y_prediction) + 4), (1000, int(y_prediction) + 4),
                 (0, 255, 0), thickness=2)

        # writing the new frame in output
        output.write(frame)
        cv2.imshow("output", frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
    else:
        break

cv2.destroyAllWindows()
output.release()
cap.release()
