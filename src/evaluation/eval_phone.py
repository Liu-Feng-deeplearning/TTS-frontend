#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019-11-14 18:44
# @Author  : liufeng

import collections
import logging
import os

import src.infolog as infolog
from src.utils import read_lines, phone2pairs, load_poly_dict


class ErrorStatic:
  def __init__(self):
    self.err_num = 0
    self.tot_num = 0
    self.err_poly = 0
    self.tot_poly = 0
    self.err_dict = collections.defaultdict(list)
    return

  def print_result(self):
    infolog.log("total num:{}, err num:{}".format(self.tot_num, self.err_num))
    infolog.log("err rate:{:.3f}\n".format(self.err_num / self.tot_num))
    infolog.log("total poly num:{}, err poly num:{}".format(
      self.tot_poly, self.err_poly))
    infolog.log("err poly rate:{:.3f}\n".format(self.err_poly / self.tot_poly))
    return

  def print_detail(self):
    err_list = sorted(self.err_dict.items(), key=lambda v: len(v[1]),
                      reverse=True)
    infolog.log("total wrong char: {}".format(len(err_list)))
    for key, value in err_list[0:30]:
      infolog.log("\n{}: {}".format(key, len(value)))
      for i in range(min(5, len(value))):
        infolog.log(
          "char:{}, right phone:{}, wrong phone:{}, text and phone: {}/{}".format(
            value[i][0], value[i][1], value[i][2], value[i][3], value[i][4]))
    return


def __read_from_result(data_path):
  lines = read_lines(data_path)
  count = 0
  result_pairs = []
  while count < len(lines):
    if lines[count].startswith("id:"):
      count += 2
    elif lines[count].startswith("split-id:"):
      sub_sentence = lines[count].split("|")[1]
      phone = lines[count + 1].strip()
      result_pairs.append((sub_sentence.replace(" ", ""), phone))
      count += 2
    elif lines[count].startswith("split-end"):
      count += 1
    elif lines[count].lower().startswith("end"):
      break
    else:
      count += 1
  return result_pairs


def __eval_for_phone(truth_path, predict_path):
  err_static = ErrorStatic()
  poly_dict = load_poly_dict()
  truth_result = __read_from_result(truth_path)
  predict_result = __read_from_result(predict_path)

  for index, (truth, predict) in enumerate(zip(truth_result, predict_result)):
    if truth[0] != predict[0]:
      print(index, truth[0], predict[0])
      raise Exception("Error")
    try:
      truth_pairs = phone2pairs(truth[0], truth[1])
      predict_pairs = phone2pairs(predict[0], predict[1])
      # exit()
      if len(truth_pairs) != len(predict_pairs):
        print("ERROR for {}:{}".format(index, truth_pairs))
      for pred_ph, truth_ph in zip(predict_pairs, truth_pairs):
        err_static.tot_num += 1
        if truth_ph[0] in poly_dict.keys():
          err_static.tot_poly += 1
        if pred_ph != truth_ph:
          err_static.err_num += 1
          err_static.err_dict[truth_ph[0]].append(
            (truth_ph[0], truth_ph[1], pred_ph[1],
             predict[0], predict[1]))
          if truth_ph[0] in poly_dict.keys():
            err_static.err_poly += 1

    except IndexError:
      pass
      print("index Error line:")

  err_static.print_result()
  err_static.print_detail()
  return


def main():
  eval_dir = "/data1/liufeng/synthesis/frontend/models/v3/eval"
  truth_path = os.path.join(eval_dir, "truth.txt")
  predict_path = os.path.join(eval_dir, "output.txt")
  infolog.init(os.path.join(eval_dir, "err_n0.log"), "baseline")
  __eval_for_phone(truth_path, predict_path)


if __name__ == '__main__':
  logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s",
                      level=logging.INFO)
  main()
