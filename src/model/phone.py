#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pickle

import kashgari
import tensorflow as tf
from kashgari.embeddings import BERTEmbedding
from kashgari.tasks.labeling import BiLSTM_CRF_Model
from tensorflow.python.keras.backend import set_session

from src.model.char2phone import sandhi
from src.model.model_utils import h5_to_pb
from src.utils import read_lines
from src.utils import split_phone_format

# kashgari.config.use_cudnn_cell = True
kashgari.config.use_cudnn_cell = False


def change_qingyin(bert_phone, upper_lines):
  """清音规则，通过查字典 """
  qingyin_word_path = "/data1/liufeng/synthesis/frontend/data/qingyin_word"
  with open(qingyin_word_path, encoding="utf-8") as fr:
    qingyin_words = [i.strip() for i in fr.readlines()]
  sentence = upper_lines
  for qingyin_word in qingyin_words:
    if qingyin_word in sentence:
      print("modify qingyin word {}".format(qingyin_word))
      index = sentence.index(qingyin_word)
      bert_phone[index + len(qingyin_word) - 1] = \
          bert_phone[index + len(qingyin_word) - 1][:-1] + '5'
  return bert_phone


class BertPolyPhone:
  """ 拼音预测主类"""
  def __init__(self):
    super().__init__()
    self.poly_dict = dict()
    poly_dict_path = "/data1/liufeng/synthesis/frontend/data/simple_poly_dict"
    for line in read_lines(poly_dict_path):
      line = line.replace(" ", "").replace("*", "")
      key = line.split(":")[0]
      value = line.split(":")[1].split(",")
      self.poly_dict[key] = value
    self.model, self.model_dir = None, None
    self.sess = None

  def inialize_model(self, bert_model_path, poly_model_path):
    print('=============init phone model=========================')
    print("bert model path:", bert_model_path)
    print("crf model path:", poly_model_path)
    # 需要训练数据的路径构建字典
    self.sess = tf.Session()
    set_session(self.sess)
    self.model_dir = os.path.dirname(os.path.dirname(poly_model_path))
    data_path = os.path.join(self.model_dir, "feature.pkl")

    train_data, train_label, test_data, test_label = \
        pickle.load(open(data_path, 'rb'))

    bert_embed = BERTEmbedding(bert_model_path, task=kashgari.LABELING,
                               sequence_length=50)
    self.model = BiLSTM_CRF_Model(bert_embed)

    self.model.build_model(x_train=train_data, y_train=train_label,
                           x_validate=test_data, y_validate=test_label)
    self.model.compile_model()
    self.model.tf_model.load_weights(poly_model_path)
    print('=============successful loaded=========================')

  def _lookup_dict(self, bert_result, pred_ph_pairs):
    """查字典的方法对拼音进行修正 """
    # todo: 如果词在词典中，不用bert的结果。
    bert_phone_result = []
    for index_c, (char, ph, _) in enumerate(pred_ph_pairs):
      if char in self.poly_dict.keys():
        # 如果bert预测结果不在多音字字典中，就是预测结果跑偏了
        if bert_result[index_c] not in self.poly_dict[char]:
          bert_phone_result.append((char, ph))
        else:
          bert_result[index_c] = split_phone_format(bert_result[index_c])
          bert_phone_result.append((char, bert_result[index_c]))
          if ph != bert_result[index_c]:
            print("using bert result {}:{} instead of {}".format(
              char, bert_result[index_c], ph))
      else:
        bert_phone_result.append((char, ph))
    return bert_phone_result

  def predict(self, sentence_list):
    """ 通过句子预测韵律，标点断开 """
    bert_input = []
    for sent in sentence_list:
      assert len(sent) < 50
      bert_input.append([c for c in sent])
    print("bert-input:", bert_input)
    prosody = self.model.predict(bert_input)
    return prosody

  def save_pb(self):
    self._write_dict()
    pb_dir = os.path.join(self.model_dir, "pb")
    os.makedirs(pb_dir, exist_ok=True)
    h5_to_pb(self.model.tf_model, pb_dir, self.sess, "model_phone.pb",
             ["output_phone"])
    return

  def _write_dict(self):
    label_path = os.path.join(self.model_dir, "pb/phone_idx2label.txt")
    with open(label_path, "w", encoding="utf-8") as fr:
      for key, value in self.model.embedding.label2idx.items():
        fr.write("{} {}\n".format(value, key))
    print("write {}".format(label_path))

    token_path = os.path.join(self.model_dir, "pb/phone_token2idx.txt")
    with open(token_path, "w", encoding="utf-8") as fr:
      for key, value in self.model.embedding.token2idx.items():
        if len(key) > 0:
          fr.write("{} {}\n".format(key, value))
    print("write {}".format(token_path))
    return

  def compute_embed(self, sentence_list):
    bert_input = [[c for c in sent] for sent in sentence_list]
    print("bert-input:", bert_input)
    import numpy as np
    tensor = self.model.embedding.process_x_dataset(bert_input)
    print("debug:", np.shape(tensor), tensor)
    res = self.model.tf_model.predict(tensor)
    import numpy as np
    print("debug:", np.shape(res), res[0][0: len(sentence_list[0]+1)])
    return tensor

  @staticmethod
  def _merge_eng_char(bert_phone_result, dict_phone_pairs):
    from src.utils import check_all_chinese
    index = 0
    new_bert_phone = []
    for word, _, _ in dict_phone_pairs:
      if (not check_all_chinese(word)) and len(word) > 1:
        new_bert_phone.append(bert_phone_result[index])
        index += len(word)
      else:
        new_bert_phone.append(bert_phone_result[index])
        index += 1
    return new_bert_phone

  def modify_result(self, bert_result, dict_phone_pairs):
    bert_result = self._merge_eng_char(bert_result, dict_phone_pairs)
    bert_phone_pairs = self._lookup_dict(bert_result, dict_phone_pairs)
    phone_pairs = bert_phone_pairs
    # phone_pairs = change_yi(phone_pairs)
    # phone_pairs = change_bu(phone_pairs)
    phone_pairs = sandhi(phone_pairs)
    bert_result = [ph for _, ph in phone_pairs]
    chars = "".join([c for c, _ in phone_pairs])
    bert_result = change_qingyin(bert_result, chars)
    return bert_result


if __name__ == "__main__":
  pass
