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
import socket
import pathlib
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageOps

from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
import tensorflow_addons as tfa
from tensorflow.keras.callbacks import ModelCheckpoint, CSVLogger, ReduceLROnPlateau, EarlyStopping, TensorBoard

from sklearn.metrics import confusion_matrix

from TrainingPipelines.ImageClassifier.ModelBuilder import build_and_train

import seaborn as sns
import mplcyberpunk

plt.style.use("cyberpunk")
plt.rcParams['figure.facecolor'] = '#0d1117'
plt.rcParams['axes.facecolor'] = '#0d1117'
plt.rcParams['savefig.facecolor'] = '#0d1117'

cap = cv2.VideoCapture(f"C:\\Users\\ryans\\Videos\\2023-03-27 20-15-29.mp4")

output = cv2.VideoWriter(f"C:\\Users\\ryans\\Videos\\out.avi", cv2.VideoWriter_fourcc(*'DIVX'), 30, (1920, 1080))

model2 = tf.keras.models.load_model(r"O:\source\repos\EVE-Online-Bot\TrainingPipelines\temp.h5")

reduction = 10

img_width = int(1920/reduction)
img_height = int(1080/reduction)

while (True):
    ret, frame = cap.read()
    if (ret):

        # adding filled rectangle on each frame
        if random.randint(0, 9) < 1:
            id = uuid.uuid1()
            cv2.imwrite(f"temp\\{id}.png", frame)
        frame = cv2.transpose(frame)
        frame2 = cv2.resize(frame, (img_height, img_width), interpolation=None )
        frame2 = cv2.transpose(frame2)
        img = np.array([np.array(frame2)])
        prediction = model2.predict(img)
        result2 = ((prediction) * np.array([1920, 1080, 1920, 1080]) )
        frame = cv2.transpose(frame)
        cv2.rectangle(frame, (int(result2[0][0]), int(result2[0][1])), (int(result2[0][2]), int(result2[0][3])),
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