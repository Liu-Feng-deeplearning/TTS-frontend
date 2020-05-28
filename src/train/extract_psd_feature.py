#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:liufeng
# datetime:2020/2/20 5:56 PM
# software: PyCharm

import pickle

from src.utils import read_lines, split_psd


def main():
  train_path = "/data1/liufeng/synthesis/feature/feature_taco/feat_0307/train.txt"
  train_lines = [line.split("|")[6] for line in read_lines(train_path) if "#" in line]
  train_data = [split_psd(line, pairs=False) for line in train_lines]
  print(train_data[0])

  train_x = [x for x, _ in train_data]
  train_y = [y for _, y in train_data]

  dev_path = "/data1/liufeng/synthesis/feature/feature_taco/feat_0307/dev_psd.txt"
  dev_lines = [line.split("|")[6] for line in read_lines(dev_path)]
  dev_data = [split_psd(line, pairs=False) for line in dev_lines]

  dev_x = [x for x, _ in dev_data]
  dev_y = [y for _, y in dev_data]

  with open('/data1/liufeng/synthesis/frontend/models/feature_psd.pkl', 'wb') as fw:
    pickle.dump((train_x, train_y, dev_x, dev_y), fw)
    print("save {}/{} train/dev items".format(len(train_x), len(dev_x)))
  return


if __name__ == '__main__':
  main()