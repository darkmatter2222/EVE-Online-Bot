from PIL import Image
from tqdm import tqdm
import numpy as np

# img = Image.open(r"O:\eve_models\training_data\route_y\00aeaf60-d4d0-11ed-9113-2cf05d9fe8eb.png")
img = Image.open(r"O:\eve_models\training_data\route_y\0aa40e54-d40c-11ed-9923-2cf05d9fe8eb.png")
train_x = []
# img = img.crop((120, 0, 160, 600))
train_x.append(np.array(img))

image_array = train_x[0]
#mask = np.array([[1] * 9] * 9)

masks = \
[
    [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
]
masks = np.array(masks)

images = []

for mask in tqdm(masks):
    final_render = []
    for y in range(train_x[0].shape[0]):
        x_results = [False] * mask.shape[1]
        for x in range(train_x[0].shape[1]):
            if x + mask.shape[1] < train_x[0].shape[1] and \
                y + mask.shape[0] < train_x[0].shape[0]:
                extract_0 = train_x[0][y:mask.shape[0] + y, x:mask.shape[1] + x, 0]
                extract_1 = train_x[0][y:mask.shape[0] + y, x:mask.shape[1] + x, 1]
                extract_2 = train_x[0][y:mask.shape[0] + y, x:mask.shape[1] + x, 2]

                extract_0 = extract_0 * mask
                extract_1 = extract_0 * mask
                extract_2 = extract_0 * mask


            x_results.append((extract_0[extract_0 != 0] == extract_0[extract_0 != 0][0]).all())
        final_render.append(x_results)
    images.append(final_render)

Image.fromarray(np.array(images[0])).show()
Image.fromarray(np.array(images[1])).show()
res = np.array(images[0] and images[1])
Image.fromarray(res).show()

print('')
