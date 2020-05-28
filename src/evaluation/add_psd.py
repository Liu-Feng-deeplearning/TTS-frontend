#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019-10-11 14:05
# @Author  : liufeng

import logging
import os

from src.train.extract_psd_feature import split_psd
from src.utils import phone2pairs
from src.utils import read_lines, write_lines, rm_prosody, clean_sentence
from src.utils import split_sentence


def main():
  model_dir = "/data1/liufeng/synthesis/frontend/models/v2"
  eval_dir = os.path.join(model_dir, "eval")
  os.makedirs(eval_dir, exist_ok=True)

  # data_path = os.path.join(model_dir, "metadata_dev.txt")
  data_path = "/data1/liufeng/synthesis/feature/feature_prosody/" \
              "bzn/dev.txt"
  metadata = read_lines(data_path)
  print(metadata[0:2])
  # dev_corpus = [line.split("|")[6] for line in read_lines(data_path)]
  # dev_phones = [line.split("|")[5] for line in read_lines(data_path)]
  # print(dev_corpus[0])
  # line = dev_corpus[0]
  # x, y = split_psd(line)
  # print(x, y)
  #
  # exit()
  # metadata = [line for line in metadata if "bzn" in line]
  # print(metadata[0:3])

  text_path = os.path.join(eval_dir, "corpus.txt")
  corpus = [rm_prosody(line.split("|")[6].replace(" ", "")) for line in
            metadata]
  # print(corpus[0:3])
  write_lines(text_path, corpus)
  # exit()

  sub_count = 0
  # truth_path = os.path.join(eval_dir, "bc_dev.txt")
  truth_path = "output.txt"
  with open(truth_path, "w", encoding="utf-8") as fr:
    for sent_id, meta in enumerate(metadata):

      phone = (meta.split("|")[5])
      sentence = clean_sentence(meta.split("|")[6].replace(" ", ""))
      _ss = sentence
      print(phone, sentence)
      # x, y = split_psd(sentence)
      # sentence = "".join(x)
      # assert len(y) == len(sentence)

      # if not check_exist_eng(sentence):
      #   continue

      fr.write("\nid:{}\n{}\n".format(sent_id, _ss))
      print("\nid:{}\n{}".format(sent_id, _ss))

      sub_sentences = split_sentence(sentence)
      sub_phones = split_sentence(phone, split_type="phone")
      # print(len(y), len(sub_phones), len(sub_sentences))
      for split_id, (sent, phone) in enumerate(zip(sub_sentences, sub_phones)):
        x, y = split_psd(sent)
        sent = "".join(x)
        print(sent, phone)
        pairs = phone2pairs(sent, phone)
        new_pairs = [(_x[0], _x[1], _y) for _x, _y in zip(pairs, y)]
        new_phone = [_y + " #" + _z for _x, _y, _z in new_pairs]
        new_phone = " ".join(new_phone).replace(" #0", "")
        fr.write("split-id:{} | {}\n{}\n".format(split_id, sent, new_phone))
        print("split-id:{} | {} | {}".format(split_id, sent, new_phone))
        sub_count += 1
      fr.write("split-end\n")
      # exit()

  print("\nsub count:{}".format(sub_count))
  print("write other_files to {}".format(truth_path))


if __name__ == '__main__':
  logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s",
                      level=logging.INFO)
  main()
