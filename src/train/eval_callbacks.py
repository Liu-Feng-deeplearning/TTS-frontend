#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:liufeng
# datetime:2020/2/14 5:38 PM
# software: PyCharm


from kashgari.tasks.base_model import BaseModel
from tensorflow.python import keras

import src.infolog as infolog


class EvalCallBack(keras.callbacks.Callback):
  def __init__(self, kash_model: BaseModel, valid_x, valid_y,
               step=5, batch_size=256, log_path=None):
    """
    Evaluate callback, calculate precision, recall and f1
    Args:
        kash_model: the kashgari model to evaluate
        valid_x: feature other_files
        valid_y: label other_files
        step: step, default 5
        batch_size: batch size, default 256
    """
    super(EvalCallBack, self).__init__()
    self.kash_model = kash_model
    self.valid_x = valid_x
    self.valid_y = valid_y
    self.step = step
    self.batch_size = batch_size
    self.logs = []
    self.log_path = log_path
    infolog.init(log_path, "train-labeling-task")

  def on_epoch_end(self, epoch, logs=None):
    err_num, tot_num = 0, 0
    if (epoch + 1) % self.step == 0:
      y_pred = self.kash_model.predict(self.valid_x, batch_size=self.batch_size)
      y_true = [seq[:len(y_pred[index])] for index, seq in
                enumerate(self.valid_y)]
      for index, (pred, true) in enumerate(zip(y_pred, y_true)):
        filter_true = [t for t in true if not t == "-"]
        filter_pred = [p for p, t in zip(pred, true) if not t == "-"]
        tot_num += len(filter_true)
        err_num += len(
          [1 for p, t in zip(filter_pred, filter_true) if not p == t])
        if index < 5:
          infolog.log("index:{},tot:{},err:{}".format(index, tot_num, err_num))
          infolog.log("truth:{}".format(true))
          infolog.log("pred:{}".format(pred))
      infolog.log("epoch:{}, acc:{:.3f}\n".format(epoch, 1 - err_num / tot_num))

    return


class PsdEvalCallBack(keras.callbacks.Callback):
  def __init__(self, kash_model: BaseModel, valid_x, valid_y,
               step=5, batch_size=256, log_path=None):
    """
    Evaluate callback, calculate precision, recall and f1
    Args:
        kash_model: the kashgari model to evaluate
        valid_x: feature other_files
        valid_y: label other_files
        step: step, default 5
        batch_size: batch size, default 256
    """
    super(PsdEvalCallBack, self).__init__()
    self.kash_model = kash_model
    self.valid_x = valid_x
    self.valid_y = valid_y
    self.step = step
    self.batch_size = batch_size
    self.logs = []
    self.log_path = log_path
    infolog.init(log_path, "train-labeling-task")

  def on_epoch_end(self, epoch, logs=None):
    err_num, tot_num = 0, 0
    if (epoch + 1) % self.step == 0:
      y_pred = self.kash_model.predict(self.valid_x, batch_size=self.batch_size)
      y_true = [seq[:len(y_pred[index])] for index, seq in
                enumerate(self.valid_y)]
      for index, (pred, true) in enumerate(zip(y_pred, y_true)):
        filter_true = [t for t in true]
        filter_pred = [p for p, t in zip(pred, true)]
        tot_num += len(filter_true)
        err_num += len(
          [1 for p, t in zip(filter_pred, filter_true) if not p == t])
        if index < 5:
          infolog.log("index:{},tot:{},err:{}".format(index, tot_num, err_num))
          infolog.log("truth:{}".format(true))
          infolog.log("pred:{}".format(pred))
      infolog.log("epoch:{}, acc:{:.3f}\n".format(epoch, 1 - err_num / tot_num))
    return


if __name__ == '__main__':
  pass
