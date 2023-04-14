import sys, os, decimal, json, time, uuid, socket, errno
import numpy as np
from PIL import Image, ImageDraw
import tensorflow as tf
from loguru import logger
import requests


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class Universal_Prediction:
    def __new__(cls):  # make singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(Universal_Prediction, cls).__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self):
        if (self.__initialized): return  # make singleton
        self.__initialized = True

        self.classifiers = {}

        self.config_dir = r'../ML_Components/universal_classifier_config.json'
        self.config = json.load(open(self.config_dir))[socket.gethostname()]

        logger.add(
            self.config['log_dir'] + '\\' + socket.gethostname() + "_" + sys.argv[0].split('/')[-1:][0] + "_{time}.log")

        for clsf_name in self.config['Classifiers'].keys():
            if not os.path.isfile(self.config['Classifiers'][clsf_name]['model_location']):
                logger.info(f'Downloading Model:{clsf_name}')
                outfile = os.path.join(self.config['Classifiers'][clsf_name]['model_location'])
                mkdir_p('\\'.join(self.config['Classifiers'][clsf_name]['model_location'].split('\\')[:-1]))
                r = requests.get(self.config['Classifiers'][clsf_name]['download_source_model'], allow_redirects=True)
                open(outfile, 'wb').write(r.content)

            else:
                logger.info(f'Using Downloaded Model:{clsf_name}')

            if not os.path.isfile(self.config['Classifiers'][clsf_name]['class_location']):
                logger.info(f'Downloading Classes:{clsf_name}')
                outfile = os.path.join(self.config['Classifiers'][clsf_name]['class_location'])
                mkdir_p('\\'.join(self.config['Classifiers'][clsf_name]['class_location'].split('\\')[:-1]))
                response = requests.get(self.config['Classifiers'][clsf_name]['download_source_class'], stream=True)
                with open(outfile, 'wb') as output:
                    output.write(response.content)
            else:
                logger.info(f'Using Downloaded Model:{clsf_name}')

            f = open(self.config['Classifiers'][clsf_name]['class_location'], "r")
            self.classifiers[clsf_name] = {
                'download_source_model': self.config['Classifiers'][clsf_name]['download_source_model'],
                'download_source_class': self.config['Classifiers'][clsf_name]['download_source_class'],
                'model': tf.keras.models.load_model(self.config['Classifiers'][clsf_name]['model_location']),
                'classes': json.loads(f.read()),
                'image_resize': tuple(self.config['Classifiers'][clsf_name]['image_resize']),
                'save_images': bool(self.config['Classifiers'][clsf_name]['save_images']),
            }

            mkdir_p(f"{self.config['log_dir']}\\{clsf_name}")
            logger.info(f'{clsf_name} Model Loaded')

    def predict(self, img, clsf_name):
        img = img.resize(
            (self.classifiers[clsf_name]['image_resize'][1], self.classifiers[clsf_name]['image_resize'][0]),
            # TF trains backwards
            resample=Image.Resampling.NEAREST)

        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create a batch

        id = uuid.uuid1()
        if self.classifiers[clsf_name]['save_images']:
            img.save(f"{self.config['log_dir']}\\{clsf_name}\\{id}.png")

        predictions = self.classifiers[clsf_name]['model'].predict(img_array)
        scores = tf.nn.softmax(predictions[0])
        result = {
            'argmax_index': np.argmax(scores),
            'value_at_argmax': scores[np.argmax(scores)].numpy(),
            'pass_general_tollerance': scores[np.argmax(scores)].numpy() > 0.5,
            'class': self.classifiers[clsf_name]['classes'][np.argmax(scores)],
            'classes': self.classifiers[clsf_name]['classes'],
            'scores': scores.numpy().tolist(),
            'id': id,
            'image_saved': self.classifiers[clsf_name]['save_images'],
            'clsf': clsf_name
        }

        return result
