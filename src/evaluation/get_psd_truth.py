#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019-10-11 14:05
# @Author  : liufeng

import logging
import os

from src.utils import read_lines, write_lines, rm_prosody, clean_sentence
from src.utils import split_sentence


def main():
  model_dir = "/data1/liufeng/synthesis/frontend/models/psd_v1"
  eval_dir = os.path.join(model_dir, "eval")
  os.makedirs(eval_dir, exist_ok=True)

  # data_path = os.path.join(model_dir, "metadata_dev.txt")
  data_path = "/data1/liufeng/synthesis/feature/feature_taco/feat_0307/" \
              "dev_psd.txt"
  metadata = read_lines(data_path)
  print(metadata[0:2])

  text_path = os.path.join(eval_dir, "corpus.txt")
  corpus = [rm_prosody(line.split("|")[6].replace(" ", "")).upper()
            for line in metadata]
  write_lines(text_path, corpus)

  sub_count = 0
  # truth_path = "output.txt"
  truth_path = os.path.join(eval_dir, "truth.txt")
  with open(truth_path, "w", encoding="utf-8") as fr:
    for sent_id, meta in enumerate(metadata):
      phone = (meta.split("|")[5])
      sentence = clean_sentence(meta.split("|")[6].replace(" ", "").upper())
      fr.write("\nid:{}\n{}\n".format(sent_id, sentence))
      print("\nid:{}\n{}".format(sent_id, sentence))

      sub_sentences = split_sentence(sentence)
      sub_phones = split_sentence(phone, split_type="phone")

      for split_id, (sent, phone) in enumerate(zip(sub_sentences, sub_phones)):
        fr.write("split-id:{} | {}\n{}\n".format(split_id, sent, phone))
        print("split-id:{} | {} | {}".format(split_id, sent, phone))
        sub_count += 1
      fr.write("split-end\n")

  print("\nsub count:{}".format(sub_count))
  print("write other_files to {}".format(truth_path))


if __name__ == '__main__':
  logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s",
                      level=logging.INFO)
  main()
