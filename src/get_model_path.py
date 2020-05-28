#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:liufeng
# datetime:2020/2/14 9:43 PM
# software: PyCharm

import os


def get_model_path(hdf5_dir, model_epoch=0):
  model_path, last_epoch = None, 0
  if os.path.exists(hdf5_dir):
    for name in os.listdir(hdf5_dir):
      if not (name.endswith("h5") or name.endswith("hdf5")):
        continue
      tmp = name.replace("-", ".")
      epoch = int(tmp.split(".")[1])
      if epoch == model_epoch:
        model_path = os.path.join(hdf5_dir, name)
        return model_path, epoch
      if epoch > last_epoch:
        last_epoch = epoch
        model_path = os.path.join(hdf5_dir, name)
  return model_path, last_epoch
