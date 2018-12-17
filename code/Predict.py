#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 20:46:18 2018

@author: user1
"""
import tensorflow as tf
from tensorflow.contrib import predictor
import numpy as np
import cv2
from tqdm import tqdm
import pandas as pd
#INPUT_SHAPE = (299,299,3)
INPUT_SHAPE = (224,224,3)
ORI_IMAGE_SHAPE = (512,512,4)
TEST_FILE = "../input_tf/Test-.tfrecords"

export_dir = './model/201812120644_F1Loss_lr1e-05_345QtrHoldOut_RGBY/export/best_exporter/1544627576'
predict_fn = predictor.from_saved_model(export_dir)


testf = tf.python_io.tf_record_iterator(TEST_FILE)
submit = pd.read_csv('../input/sample_submission.csv')

predicted = []
for exi in tqdm(testf):
    ex = tf.train.Example.FromString(exi)
#    height = ex.features.feature["height"].int64_list.value[0]
#    width = ex.features.feature["width"].int64_list.value[0]
#    channel = ex.features.feature["channel"].int64_list.value[0]
    image = ex.features.feature["image"].bytes_list.value[0]
    image = np.frombuffer(image, dtype=np.uint8)
    image = image.reshape([ORI_IMAGE_SHAPE[0],ORI_IMAGE_SHAPE[1],ORI_IMAGE_SHAPE[2]])
    image = cv2.resize(image,(INPUT_SHAPE[0],INPUT_SHAPE[1]))
    image = np.stack((image[:,:,0].astype(np.float32)/255.0,
                     image[:,:,1].astype(np.float32)/255.0,
                     image[:,:,2].astype(np.float32)/255.0+image[:,:,3].astype(np.float32)/255.0)
                    ,axis=2)
    onebatch = np.expand_dims(image, axis=0)
    
    predictions = predict_fn({'image_input':onebatch})
    label_predict = np.arange(28)[predictions['predictions'][0]>=0.5]
    str_predict_label = ' '.join(str(l) for l in label_predict)
    predicted.append(str_predict_label)

submit['Predicted'] = predicted
submit.to_csv('mysubmission05.csv', index=False)

