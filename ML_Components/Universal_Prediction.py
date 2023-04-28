import sys, os, decimal, json, time, uuid, socket, errno, xmltodict
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
            self.config['log_dir'] + '\\' + socket.gethostname() + "Audit_History" + sys.argv[0].split('/')[-1:][0] + "Audit_History{time}.log")

        self.sync_models()

        for clsf_name in self.config['Classifiers']['enabled_classifiers']:
            f = open(f"{self.config['Classifiers']['download_dest_root']}\\{clsf_name}\\{clsf_name}_meta.json", "r")
            self.classifiers[clsf_name] = {
                'model': tf.keras.models.load_model(f"{self.config['Classifiers']['download_dest_root']}\\{clsf_name}\\{clsf_name}_model.h5"),
                'meta': json.loads(f.read()),
                'save_images': clsf_name in self.config['Classifiers']['save_image_classifiers'],
            }

            mkdir_p(f"{self.config['log_dir']}\\{clsf_name}")
            logger.info(f'{clsf_name} Model Loaded')

    def download_model(self, clsf_name, available_models):
        local_model_root = f"{self.config['Classifiers']['download_dest_root']}\\{clsf_name}"
        mkdir_p(local_model_root)

        logger.info(f'Downloading Model:{clsf_name}')
        outfile = f"{local_model_root}\\{clsf_name}_model.h5"
        upfile = f"{self.config['Classifiers']['download_source_root']}/{available_models[clsf_name][f'{clsf_name}_model.h5']['Key']}"
        r = requests.get(upfile, allow_redirects=True)
        open(outfile, 'wb').write(r.content)

        logger.info(f'Downloading Meta:{clsf_name}')
        outfile = f"{local_model_root}\\{clsf_name}_meta.json"
        upfile = f"{self.config['Classifiers']['download_source_root']}/{available_models[clsf_name][f'{clsf_name}_meta.json']['Key']}"
        r = requests.get(upfile, stream=True)
        with open(outfile, 'wb') as output:
            output.write(r.content)

    def sync_models(self):
        r = requests.get(self.config['Classifiers']['download_source_root'], allow_redirects=True)
        data_dict = xmltodict.parse(r.content)
        available_models = {}
        for obj in data_dict['ListBucketResult']['Contents']:
            key_split = obj['Key'].split('/')
            available_models[key_split[0]] = available_models[key_split[0]] if key_split[0] in available_models else {}
            available_models[key_split[0]][key_split[1]] = obj

        installed_models = {}
        try:
            f = open(f"{self.config['Classifiers']['download_dest_root']}\\installed_models.json", "r")
            installed_models = json.loads(f.read())
            f.close()
        except:
            logger.info('installed_models file missing, proceeding w/ new.')
            pass

        for clsf_name in self.config['Classifiers']['enabled_classifiers']:
            if clsf_name not in available_models.keys():
                Exception(f"{clsf_name} not available for download.")
        change_made = False
        for clsf_name in self.config['Classifiers']['enabled_classifiers']:
            if clsf_name in installed_models:
                if installed_models[clsf_name] != available_models[clsf_name]:
                    self.download_model(clsf_name, available_models)
                    installed_models[clsf_name] = available_models[clsf_name]
                    change_made = True
            else:
                self.download_model(clsf_name, available_models)
                installed_models[clsf_name] = available_models[clsf_name]
                change_made = True

        if change_made:
            f = open(f"{self.config['Classifiers']['download_dest_root']}\\installed_models.json", "w")
            f.write(json.dumps(installed_models, indent=1))
            f.close()



    def predict(self, orig_img, clsf_name):
        img = orig_img.resize(
            (self.classifiers[clsf_name]['meta']['image_resize'][1], self.classifiers[clsf_name]['meta']['image_resize'][0]),
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
            'class': self.classifiers[clsf_name]['meta']['classes'][np.argmax(scores)],
            'classes': self.classifiers[clsf_name]['meta']['classes'],
            'scores': scores.numpy().tolist(),
            'id': id,
            'image_saved': self.classifiers[clsf_name]['save_images'],
            'clsf': clsf_name
        }

        return result
