#!/usr/bin/env python
# coding: utf-8

# import functools
import os,cv2

from datetime import datetime
from matplotlib import gridspec
import matplotlib.pylab as plt
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

print("TF Version: ", tf.__version__)
print("TF Hub version: ", hub.__version__)
print("Eager mode enabled: ", tf.executing_eagerly())
print("GPU available: ", tf.config.list_physical_devices('GPU'))
# Load TF Hub module.
hub_handle = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
hub_module = hub.load(hub_handle)

# def crop_center(image):
#     """Returns a cropped square image."""
#     shape = image.shape
#     new_shape = min(shape[1], shape[2])
#     offset_y = max(shape[1] - shape[2], 0) // 2
#     offset_x = max(shape[2] - shape[1], 0) // 2
#     image = tf.image.crop_to_bounding_box(
#       image, offset_y, offset_x, new_shape, new_shape)
#     return image

# def resize_image_to_square(image_np, image_size=(256,256), preserve_aspect_ratio=True):
#     image_np_extra = image_np.astype(np.float32)[np.newaxis, ...]
#     if image_np_extra.max() > 1.0:
#         image_np_extra = image_np_extra / 255.
#     if len(image_np_extra.shape) == 3:
#         image_np_extra = tf.stack([image_np_extra, image_np_extra, image_np_extra], axis=-1)
#     image_np_extra = crop_center(image_np_extra)
#     image_np_extra = tf.image.resize(image_np_extra, image_size, preserve_aspect_ratio=True)
#     return image_np_extra

def load_image(img_path):
    img = tf.io.read_file(img_path)
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = img[tf.newaxis, :]
    return img

# show images in the notebook side by side
def show_n(images, titles=('',)):
    n = len(images)
    image_sizes = [image.shape[1] for image in images]
    w = (image_sizes[0] * 6) // 320
    plt.figure(figsize=(w * n, w))
    gs = gridspec.GridSpec(1, n, width_ratios=image_sizes)
    for i in range(n):
        plt.subplot(gs[i])
        plt.imshow(images[i][0], aspect='equal')
        plt.axis('off')
        plt.title(titles[i] if len(titles) > i else '')
    plt.show()

def transfer_img(content_img, style_img):
    outputs = hub_module(tf.constant(content_img), tf.constant(style_img))
    stylized_image = outputs[0]
    # Visualize input images and the generated stylized image.
    # show_n([content_image, style_image, stylized_image], titles=['Original content image', 'Style image', 'Stylized image'])
    # Store image
    datetime_str = str(datetime.now())
    cv2.imwrite('img/ai/{}.jpg'.format(datetime_str), cv2.cvtColor(np.squeeze(stylized_image)*255, cv2.COLOR_BGR2RGB))
    file_path = 'img/ai/'+datetime_str+'.jpg'
    return file_path
