#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019-11-14 18:44
# @Author  : liufeng

import collections
import logging
import os

import src.infolog as infolog
from src.utils import read_lines, split_psd, merge_psd


class ErrorStatic:
  def __init__(self):
    self.err_num = 0
    self.tot_num = 0
    self.err_seq = 0
    self.tot_seq = 0
    self.err_dict = collections.defaultdict(list)
    return

  def print_result(self):
    infolog.log("total num:{}, err num:{}".format(self.tot_num, self.err_num))
    infolog.log("err rate:{:.3f}".format(self.err_num / self.tot_num))
    infolog.log("err seq:{}/{}".format(self.err_seq, self.tot_seq))
    infolog.log("err seq rate:{:.3f}\n".format(self.err_seq / self.tot_seq))
    return

  def print_detail(self):
    err_list = sorted(self.err_dict.items(), key=lambda v: v[0], reverse=True)
    for k in range(3):
      for truth, predict in err_list[k][1]:
        infolog.log("\nerr:{}".format(err_list[k][0]))
        infolog.log("truth:{}".format(merge_psd(truth)))
        infolog.log("model:{}".format(merge_psd(predict)))
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
      psd_pairs = split_psd(sub_sentence.replace(" ", ""))
      result_pairs.append(psd_pairs)
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
  truth_result = __read_from_result(truth_path)
  predict_result = __read_from_result(predict_path)

  for (truth_pairs, predict_pairs) in (zip(truth_result, predict_result)):
    err_static.tot_seq += 1
    tmp_err_seq = 0
    if len(truth_pairs) != len(predict_pairs):
      print("ERROR for {}:{}".format(truth_pairs, predict_pairs))
    for pred, truth in zip(predict_pairs, truth_pairs):
      err_static.tot_num += 1
      if pred[0] != truth[0]:
        print("match ERROR: {}/{}".format(pred, truth))

      if pred[1] in ["3", "4"] and truth[1] in ["3", "4"]:
        # note: 不区分标点处韵律造成的错误。
        continue

      if pred[1] != truth[1]:
        err_static.err_num += 1
        tmp_err_seq += 1

    err_static.err_num += tmp_err_seq
    if tmp_err_seq > 0:
      err_static.err_seq += 1
      err_static.err_dict[tmp_err_seq].append((truth_pairs, predict_pairs))

  err_static.print_result()
  err_static.print_detail()
  return


def main():
  eval_dir = "/data1/liufeng/synthesis/frontend/models/psd_v1/eval"
  truth_path = os.path.join(eval_dir, "truth.txt")
  predict_path = os.path.join(eval_dir, "output.txt")
  infolog.init(os.path.join(eval_dir, "err_n0.log"), "baseline")
  __eval_for_phone(truth_path, predict_path)


if __name__ == '__main__':
  logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s",
                      level=logging.INFO)
  main()
