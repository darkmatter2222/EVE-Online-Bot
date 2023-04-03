import sys, os, decimal, json, time, uuid, socket
import numpy as np
from PIL import Image, ImageDraw
import tensorflow as tf
from loguru import logger

class Universal_Prediction:
    def __new__(cls): # make singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(Universal_Prediction, cls).__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self):
        if(self.__initialized): return # make singleton
        self.__initialized = True

        self.classifiers = {}

        self.config_dir = r'../ML_Components/universal_classifier_config.json'
        self.config = json.load(open(self.config_dir))[socket.gethostname()]

        logger.add(
        self.config['log_dir'] + '\\' + socket.gethostname() + "_" + sys.argv[0].split('/')[-1:][0] + "_{time}.log")

        for clsf_name in self.config['Classifiers'].keys():
            f = open(self.config['Classifiers'][clsf_name]['class_location'], "r")
            self.classifiers[clsf_name] = {
                'model': tf.keras.models.load_model(self.config['Classifiers'][clsf_name]['model_location']),
                'classes': json.loads(f.read()),
                'image_resize': tuple(self.config['Classifiers'][clsf_name]['image_resize']),
                'save_images': bool(self.config['Classifiers'][clsf_name]['save_images']),
            }
            logger.info(f'{clsf_name} Model Loaded')

    def predict(self, img, clsf_name):
        img = img.resize(
            (self.classifiers[clsf_name]['image_resize'][1], self.classifiers[clsf_name]['image_resize'][0]),
            # TF trains backwards
            resample=Image.Resampling.NEAREST)
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create a batch

        predictions = self.classifiers[clsf_name]['model'].predict(img_array)
        scores = tf.nn.softmax(predictions[0])
        result = {
            'argmax_index': np.argmax(scores),
            'value_at_argmax': scores[np.argmax(scores)].numpy(),
            'pass_general_tollerance': scores[np.argmax(scores)].numpy() > 0.5,
            'class': self.classifiers[clsf_name]['classes'][np.argmax(scores)],
            'classes': self.classifiers[clsf_name]['classes'],
            'scores': scores.numpy().tolist()
        }
        return result