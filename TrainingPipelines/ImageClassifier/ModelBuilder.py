import matplotlib.pyplot as plt
import numpy as np
import PIL, json
import tensorflow as tf
import socket
import pathlib

from PIL import Image, ImageDraw

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from sklearn.metrics import confusion_matrix


def build_and_train(root_image_directory,
                    model_name):
    data_dir = pathlib.Path(root_image_directory)

    image_list = list(data_dir.glob('*/*.png'))
    image_count = len(image_list)
    print(image_count)

    img = Image.open(image_list[0])

    batch_size = 1
    img_height = int(img.height * 0.2)
    img_width = int(img.width * 0.2)

    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    class_names = train_ds.class_names
    print(class_names)

    class_location = fr'{root_image_directory}\{model_name}_classes.json'
    f = open(class_location, "w")
    f.write(json.dumps(class_names))
    f.close()

    AUTOTUNE = tf.data.AUTOTUNE

    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    num_classes = len(class_names)

    model = Sequential([
        layers.Rescaling(1. / 255, input_shape=(img_height, img_width, 3)),
        layers.Conv2D(16, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes)
    ])

    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    epochs = 10
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs
    )
    train_data = list(train_ds)
    features = np.concatenate([train_data[n][0] for n in range(0, len(train_data))])
    targets = np.concatenate([train_data[n][1] for n in range(0, len(train_data))])
    print(targets)
    predictions = model.predict(features)
    print(predictions.argmax(1))
    
    cf = confusion_matrix(targets, predictions.argmax(1).astype(int))
    
    model_location = fr'{root_image_directory}\{model_name}_model.h5'
    model.save(model_location)
    
    return {'image_resize': [img_height, img_width],
            'class_location': class_location,
            'model_location': model_location,
            'cm':cf}
