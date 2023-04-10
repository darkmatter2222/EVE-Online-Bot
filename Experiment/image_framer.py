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

plt.style.use("cyberpunk")
plt.rcParams['figure.facecolor'] = '#0d1117'
plt.rcParams['axes.facecolor'] = '#0d1117'
plt.rcParams['savefig.facecolor'] = '#0d1117'

cap = cv2.VideoCapture(f"C:\\Users\\ryans\\Videos\\2023-04-09 21-29-33.mp4")

output = cv2.VideoWriter(f"C:\\Users\\ryans\\Videos\\out2.avi", cv2.VideoWriter_fourcc(*'DIVX'), 30, (1920, 1080))

model2 = tf.keras.models.load_model(r"O:\source\repos\EVE-Online-Bot\TrainingPipelines\test_location.h5", compile=False)

reduction = 2

img_width = int(500/reduction)
img_height = int(600/reduction)

while (True):
    ret, frame = cap.read()
    if (ret):

        # adding filled rectangle on each frame
        #if random.randint(0, 9) < 1:
        #    id = uuid.uuid1()
        #    cv2.imwrite(f"temp\\{id}.png", frame)
        #frame = cv2.transpose(frame)
        color_converted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.transpose(frame)
        pil_image=Image.fromarray(color_converted)
        pil_image = pil_image.crop((0, 0, 500, 600))
        img = pil_image.resize((img_width, img_height), resample=Image.Resampling.NEAREST)

        img = np.array([np.array(img)])
        prediction = model2.predict(img)
        result2 = ((prediction) * np.array([600]) )
        frame = cv2.transpose(frame)
        cv2.line(frame, (0, int(result2[0][0])), (1000, int(result2[0][0])),
                      (0, 255, 0), thickness = 2)

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