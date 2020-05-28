#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:liufeng
# datetime:2020/2/12 3:34 PM
# software: PyCharm

import pickle
import random
import re

from src.utils import phone2pairs, has_poly_char, load_poly_dict, rm_prosody
from src.utils import read_lines, write_lines, clean_sentence


def __extract_feature(new_lines, poly_dict):
  data_lines = []
  meta_data = []
  for line in new_lines:
    line = rm_prosody(line)

    line = re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", line)

    phone, chars = line.split("|")[1], line.split("|")[2]
    chars = clean_sentence(chars.replace(" ", ""))
    # phone = split_tone(phone)
    try:
      phone_pairs = phone2pairs(chars, phone)
      new_phone_pairs = []
      for c, p in phone_pairs:
        if c in poly_dict.keys():
          new_phone_pairs.append((c, p))
        else:
          new_phone_pairs.append((c, "-"))
      data_lines.append(line)
      meta_data.append(([p for p in chars],
                        [p.replace(" ", "").replace("*", "")
                        for _, p in new_phone_pairs]))
    except TypeError:
      pass
    except IndexError:
      print("Index Error:", phone, chars)

  print("there are {} trainable lines".format(len(data_lines)))
  for i in range(5):
    print(meta_data[i])

  data_x = [x for x, _ in meta_data]
  data_y = [y for _, y in meta_data]
  return data_x, data_y, data_lines


def main():
  data_path = '/data1/liufeng/synthesis/TACOTRON-2-refined/data/data_0306/' \
              'metadata_tot.csv'
  total_lines = read_lines(data_path)[0:]
  print(total_lines[0])

  poly_dict = load_poly_dict()

  new_lines = []
  for line in total_lines:
    if has_poly_char(line.split("|")[2], poly_dict):
      new_lines.append(line)
  print("there are {} lines with poly char".format(len(new_lines)))

  random.shuffle(new_lines)
  dev_lines = new_lines[0:5000]
  train_lines = new_lines[5000:]

  poly_chars, tot_chars = 0, 0
  for line in new_lines:
    for char in line:
      tot_chars += 1
      if char in poly_dict.keys():
        poly_chars += 1
  print("there are {}chars in total {}chars ({})".format(
    poly_chars, tot_chars, poly_chars/tot_chars))

  train_x, train_y, data_lines = __extract_feature(train_lines, poly_dict)
  write_lines("metadata_train.txt", data_lines)
  dev_x, dev_y, data_lines = __extract_feature(dev_lines, poly_dict)
  write_lines("metadata_dev.txt", data_lines)

  with open('/data1/liufeng/synthesis/frontend/models/feature.pkl', 'wb') as fw:
    pickle.dump((train_x, train_y, dev_x, dev_y), fw)
    print("save {}/{} train/dev items ".format(len(train_x), len(dev_x)))
  return


if __name__ == "__main__":
  main()
