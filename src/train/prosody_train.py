#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020-2-09 11:44
# @Author  : liujshi

import argparse
import os
import pickle

import kashgari
from kashgari.embeddings import BERTEmbedding
from kashgari.tasks.labeling import BiLSTM_CRF_Model as KashModel
from keras_radam import RAdam
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard

from src.train.eval_callbacks import PsdEvalCallBack as EvalCallBack

ROOT_DIR = "/data1/liufeng/synthesis/frontend/models"
# kashgari.config.use_cudnn_cell = False


def train():
  parser = argparse.ArgumentParser()
  parser.add_argument('model_dir', default='model dir')
  args = parser.parse_args()

  model_dir = args.model_dir
  hdf_dir = os.path.join(model_dir, "hdf5")
  os.makedirs(hdf_dir, exist_ok=True)

  bert_model_path = os.path.join(ROOT_DIR, 'BERT-baseline')
  data_path = os.path.join(model_dir, "feature_psd.pkl")
  with open(data_path, 'rb') as fr:
    train_data, train_label, test_data, test_label = pickle.load(fr)
  print("load {}/{} train/dev items ".format(len(train_data), len(test_data)))

  bert_embed = BERTEmbedding(bert_model_path, task=kashgari.LABELING,
                             sequence_length=50)
  model = KashModel(bert_embed)
  model.build_model(x_train=train_data, y_train=train_label,
                    x_validate=test_data, y_validate=test_label)

  from src.get_model_path import get_model_path
  model_path, init_epoch = get_model_path(hdf_dir)
  if init_epoch > 0:
    print("load epoch from {}".format(model_path))
    model.tf_model.load_weights(model_path)

  optimizer = RAdam(learning_rate=0.0001)
  model.compile_model(optimizer=optimizer)

  hdf5_path = os.path.join(hdf_dir, "crf-{epoch:03d}-{val_accuracy:.3f}.hdf5")
  checkpoint = ModelCheckpoint(hdf5_path,
                               monitor='val_accuracy', verbose=1,
                               save_best_only=True,
                               save_weights_only=False,
                               mode='auto', period=1)
  tensorboard = TensorBoard(log_dir=os.path.join(model_dir, "log"))
  eval_callback = EvalCallBack(kash_model=model, valid_x=test_data,
                               valid_y=test_label, step=1,
                               log_path=os.path.join(model_dir, "acc.txt"))
  callbacks = [checkpoint, tensorboard, eval_callback]

  model.fit(train_data[0:], train_label[0:], x_validate=test_data[0:],
            y_validate=test_label[0:], epochs=100, batch_size=256,
            callbacks=callbacks)
  return


if __name__ == "__main__":
  train()
