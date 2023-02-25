import numpy as np
import pandas as pd
import mss
import mss.tools
from PIL import Image, ImageDraw
import cv2
import sys, os, decimal, json
from pytesseract import pytesseract
import socket, json
import tensorflow as tf

sys.path.append(os.path.realpath('..'))

class ScreenClassifier:
    def __init__(self,
                 config_dir=r'..\Configs\configs.json'):
        self.config_dir = config_dir
        self.config = json.load(open(self.config_dir))[socket.gethostname()]
        self.screen = self.get_screen()
        self.model = tf.keras.models.load_model(self.config["screen_classifier_model"])
        f = open(self.config["screen_classifier_classes"], "r")
        self.classes = json.loads(f.read())
        self.img_height = 180
        self.img_width = 180
        print('ScreenClassifier loaded...')

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

    def get_screen_class(self):
        img = self.get_screen().resize((self.img_height, self.img_width), resample=Image.Resampling.NEAREST)
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create a batch
        predictions = self.model.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        return self.classes[np.argmax(score)]

