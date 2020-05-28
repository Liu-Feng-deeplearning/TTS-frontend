#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019-10-11 14:05
# @Author  : liufeng

import argparse
import logging
import os
import pickle
from collections import namedtuple

import yaml

from src.get_model_path import get_model_path
from src.model.char2phone import TranscriptToPinyin
from src.text_normalizer.text import Text
from src.utils import read_lines, write_lines
from src.utils import split_sentence, clean_sentence

ROOT_DIR = "/data1/liufeng/synthesis/TACOTRON-2-refined"
os.environ["CUDA_VISIBLE_DEVICES"] = "{}".format(-1)


def __load_hparams(yaml_path):
  with open(yaml_path, encoding="utf-8") as yaml_file:
    hp_yaml = yaml.load(yaml_file.read())
  Hparams = namedtuple('Hparams', hp_yaml.keys())
  hparams = Hparams(*hp_yaml.values())
  return hparams


def __compute_psd_result(hparams, sentences, load_memory=False):
  from src.model.prosody import BertProsody
  psd_predict = BertProsody()
  bert_result_path = os.path.join(hparams.psd_model_dir, "bert_result.pkl")
  if os.path.exists(bert_result_path) and load_memory:
    with open(bert_result_path, "rb") as fr:
      bert_psd_result = pickle.load(fr)
  else:
    bert_input = []
    for sent_id, sentence in enumerate(sentences):
      sentence = clean_sentence(sentence)
      sub_sentences = split_sentence(sentence)
      bert_input.extend(sub_sentences)
    model_path, init_epoch = get_model_path(
      os.path.join(hparams.psd_model_dir, "hdf5"))
    psd_predict.initial_model(bert_model_path=hparams.bert_model_path,
                              psd_model_path=model_path)
    bert_psd_result = psd_predict.predict(bert_input)
    with open(bert_result_path, "wb") as fw:
      pickle.dump(bert_psd_result, fw)
    print("completed bert inference")
  return psd_predict, bert_psd_result


def __compute_nnet_phone_result(hparams, sentences, load_memory=False):
  from src.model.phone import BertPolyPhone
  phone_predictor = BertPolyPhone()
  bert_result_path = os.path.join(hparams.poly_model_dir, "bert_result.pkl")

  if os.path.exists(bert_result_path) and load_memory:
    with open(bert_result_path, "rb") as fr:
      bert_phone_result = pickle.load(fr)
  else:
    bert_input = []
    for sent_id, sentence in enumerate(sentences):
      sentence = clean_sentence(sentence)
      sub_sentences = split_sentence(sentence)
      bert_input.extend(sub_sentences)
    print("total sub sentences:{}".format(len(bert_input)))
    model_path, init_epoch = get_model_path(
      os.path.join(hparams.poly_model_dir, "hdf5"))
    phone_predictor.inialize_model(bert_model_path=hparams.bert_model_path,
                                   poly_model_path=model_path)
    bert_phone_result = phone_predictor.predict(bert_input)
    with open(bert_result_path, "wb") as fw:
      pickle.dump(bert_phone_result, fw)
    print("completed bert inference")
  return phone_predictor, bert_phone_result


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('yaml_path', help='config path for frontend')
  parser.add_argument('input_path', help='input path(txt)')
  parser.add_argument('output_path', help='output path(txt)')
  args = parser.parse_args()

  # todo: add sil label
  hparams = __load_hparams(args.yaml_path)

  text_path = args.input_path
  frontend_path = args.output_path
  flag_psd = hparams.flag_psd

  if hparams.norm_text:
    raw_file_lines = read_lines(text_path)
    sentences = []
    print("text normalize:")
    for line in raw_file_lines:
      new_line = Text().normalize(line)
      sentences.append(new_line.replace(" ", ""))
      if not new_line == line:
        print("{}->{}".format(line, new_line))
  else:
    sentences = read_lines(text_path)
  write_lines("norm.txt", sentences)
  # exit()

  trans = TranscriptToPinyin(dic_path=hparams.dict_path,
                             eng_dic_path=hparams.eng_dict_path, )

  if hparams.nnet_psd and hparams.flag_psd:
    psd_predict, bert_psd_result = __compute_psd_result(
      hparams, sentences, hparams.load_memory_psd)
  else:
    psd_predict, bert_psd_result = None, None

  if hparams.nnet_phone:
    phone_predictor, bert_phone_result = __compute_nnet_phone_result(
      hparams, sentences, hparams.load_memory_phone)
  else:
    phone_predictor, bert_phone_result = None, None

  sub_count, count = 0, 0
  with open(frontend_path, "w", encoding="utf-8") as frontend_file:
    for sent_id, sentence in enumerate(sentences[0:]):
      # sentence = num2hanzi(clean_sentence(sentence))
      frontend_file.write("\nid:{}\n{}\n".format(sent_id, sentence))
      print("\nid:{}\n{}".format(sent_id, sentence))

      sub_sentences = split_sentence(sentence)
      for split_id, sub_sentence in enumerate(sub_sentences):
        sub_count += 1
        phone_pairs = trans.get_phone_pairs(
          sub_sentence, change_eng_symbol=hparams.eng_symbol)
        new_ = []
        if hparams.nnet_phone:
          bert_phone = bert_phone_result[count]
          if len(sub_sentence) == len(bert_phone):
            phone = phone_predictor.modify_result(bert_phone, phone_pairs)
            for i, (c, ph, p) in enumerate(phone_pairs):
              new_.append((c, phone[i], p))
            phone_pairs = new_
          else:
            print("Error for bert result")

        if flag_psd and not hparams.nnet_psd:
          phone = " ".join([ph + " #" + psd for _, ph, psd in phone_pairs])
          phone = phone.replace("#0", "").replace("#5", "")
          sub_sentence = "".join([c + "#" + psd for c, _, psd in phone_pairs])
          sub_sentence = sub_sentence.replace("#0", "").replace("#5", "")
        elif flag_psd and hparams.nnet_psd:
          new_pairs = []
          for new_psd, (char, ph, _) in zip(bert_psd_result[count],
                                            phone_pairs):
            new_pairs.append((char, ph, new_psd))
          new_pairs = psd_predict.change_by_rules(new_pairs)
          phone = " ".join([ph + " #" + psd for _, ph, psd in new_pairs])
          phone = phone.replace("#0", "").replace("#5", "")
          sub_sentence = "".join([c + "#" + psd for c, _, psd in new_pairs])
          sub_sentence = sub_sentence.replace("#0", "").replace("#5", "")
        else:
          phone = " ".join([ph for _, ph, _ in phone_pairs])
          sub_sentence = "".join([c for c, _, _ in phone_pairs])

        count += 1
        frontend_file.write(
          "split-id:{} | {}\n{}\n".format(split_id, sub_sentence, phone))
        print("split-id:{} | {} | {}".format(split_id, sub_sentence, phone))
      frontend_file.write("split-end\n")

  # todo: 改善停顿。
  # todo: 重构，废弃kashagri，使用keras-bert
  print("\nsub count:{}".format(sub_count))
  print("write output data to {}".format(frontend_path))


if __name__ == '__main__':
  logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s",
                      level=logging.INFO)
  main()
