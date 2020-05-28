#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:liufeng
# datetime:2020/2/12 3:34 PM
# software: PyCharm

import pickle
from collections import defaultdict

from src.utils import phone2pairs
from src.utils import read_lines, write_lines, clean_sentence


def __change_tone_format(phone):
  phone = phone.replace("1", " *1").replace("2", " *2").replace("3", " *3")
  phone = phone.replace("4", " *4").replace("5", " *5")
  return phone


def __get_total_dict():
  with open("../../other_files/in_baiduhanyu.txt") as fr:
    lines = fr.readlines()[0:]
  new_lines = []
  for line in lines:
    line = line.replace("[", "").replace("]", "")
    # line = line.replace("[", "").replace("]", "").replace(":")
    chars = line.split(":")[0]
    print(chars)
    phones = line.split(":")[1].split(",")

    if len(chars) == 1 and len(phones) > 1:
      new_lines.append(line.strip())
  write_lines("../../other_files/poly_dict", new_lines)


def __generate_simple_poly_dict():
  data_path = '/data1/liujshi/yunlv_research/total_zhuiyi_corup/' \
              'total_metadata_new'
  total_lines = read_lines(data_path)[0:]
  print(total_lines[0:5])

  total_dict, poly_dict = defaultdict(list), defaultdict(list)
  for line in total_lines:
    phone, chars = line.split("|")[1], line.split("|")[2]
    chars = clean_sentence(chars.replace(" ", ""))
    phone = __change_tone_format(phone)
    try:
      phone_pairs = phone2pairs(chars, phone)
      for c, p in phone_pairs:
        total_dict[c].append(p)
        total_dict[c] = list(set(total_dict[c]))
    except TypeError:
      pass
    except IndexError:
      print("Index Error:", phone, chars)

  for line in read_lines("../../other_files/poly_dict"):
    key = line.split(":")[0]
    value = line.split(":")[1].split(",")
    poly_dict[key] = value

  map_phone = dict()
  for line in read_lines("../../other_files/phone_map_merge.txt"):
    key = line.split(":")[0]
    value = line.split(":")[1]
    map_phone[key] = value

  new_lines = []
  for char in poly_dict.keys():
    if char not in total_dict.keys():
      pass  # 未出现过的多音字移除掉
    else:
      values = total_dict[char]
      value_saved = []
      for value in values:
        # 发音词典拼音转化成标准拼音进行比对。
        map_value = map_phone[value.split()[0]] + \
                    map_phone[value.split()[1] + value.split()[2][-1]]
        if map_value in poly_dict[char]:
          value_saved.append(value)
      if len(value_saved) > 1:
        new_line = "{}:{}".format(char, ",".join(value_saved))
        new_lines.append(new_line)
        print("save:", new_line)
      else:
        pass  # 只出现过其中一个音的多音字移除掉。

  write_lines("../../other_files/simple_poly_dict", new_lines)
  return None


def __has_poly_char(corpus, poly_dict):
  for char in corpus:
    if char in poly_dict.keys():
      return True
  return False


def main():
  data_path = '../../models/total_1201_data.pkl'
  train_data, train_label, test_data, test_label = \
    pickle.load(open(data_path, 'rb'))

  print(test_data[0:3])
  print(test_label[0:3])

  data_path = '../../other_files/dict_20200113'
  xx = pickle.load(open(data_path, 'rb'))

  print(xx)
  return


if __name__ == "__main__":
  main()
