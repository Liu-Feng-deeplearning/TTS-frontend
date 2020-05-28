#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pickle

import kashgari
import tensorflow as tf
from kashgari.embeddings import BERTEmbedding
from kashgari.tasks.labeling import BiLSTM_CRF_Model
from tensorflow.python.keras.backend import set_session

from src.model.model_utils import h5_to_pb

kashgari.config.use_cudnn_cell = False


class BertProsody:
  """ 目前只支持长度50，输入字符数49 + 终结符 """
  def __init__(self):
    self.model, self.model_dir, self.model_path = None, None, None
    self.sess = None
    return

  def initial_model(self, bert_model_path, psd_model_path):
    print('=============init bert model=========================')
    print("bert model path:", bert_model_path)
    print("crf model path:", psd_model_path)
    self.sess = tf.Session()
    set_session(self.sess)
    self.model_dir = os.path.dirname(os.path.dirname(psd_model_path))
    self.model_path = psd_model_path
    data_path = os.path.join(self.model_dir, "feature_psd.pkl")
    train_data, train_label, test_data, test_label = \
        pickle.load(open(data_path, 'rb'))

    bert_embed = BERTEmbedding(bert_model_path, task=kashgari.LABELING,
                               sequence_length=50)
    self.model = BiLSTM_CRF_Model(bert_embed)
    self.model.build_model(x_train=train_data, y_train=train_label,
                           x_validate=test_data, y_validate=test_label)
    self.model.compile_model()
    self.model.tf_model.load_weights(psd_model_path)
    print('=============bert model loaded=========================')
    return

  def _write_dict(self):
    label_path = os.path.join(self.model_dir, "idx2label.txt")
    with open(label_path, "w", encoding="utf-8") as fr:
      for key, value in self.model.embedding.label2idx.items():
        fr.write("{} {}\n".format(value, key))

    token_path = os.path.join(self.model_dir, "token2idx.txt")
    with open(token_path, "w", encoding="utf-8") as fr:
      for key, value in self.model.embedding.token2idx.items():
        if len(key) > 0:
          fr.write("{} {}\n".format(key, value))

  def predict(self, sentence_list):
    """ 通过句子预测韵律，标点断开 """
    bert_input = []
    for sent in sentence_list:
      assert len(sent) < 50
      bert_input.append([c for c in sent])
    print("bert-input:", bert_input)
    prosody = self.model.predict(bert_input)
    return prosody

  def compute_embed(self, sentence_list):
    bert_input = [[c for c in sent] for sent in sentence_list]
    print("bert-input:", bert_input)
    tensor = self.model.embedding.process_x_dataset(bert_input)
    res = self.model.tf_model.predict(tensor)
    import numpy as np
    print("debug:", np.shape(res), res[0])
    return tensor

  def save_pb(self):
    self._write_dict()
    pb_dir = os.path.join(self.model_dir, "pb")
    os.makedirs(pb_dir, exist_ok=True)
    # [print(n.name) for n in tf.get_default_graph().as_graph_def().node]
    h5_to_pb(self.model.tf_model, pb_dir, self.sess, "model_psd.pb",
             ["output_psd"])
    return

  @staticmethod
  def change_by_rules(old_pairs):
    """ 强制规则:
    1. 逗号之前是#3，句号之前是#4
    2. 其他位置，#3 -> #2
    """
    new_pairs = []
    for i, (char, ph, psd) in enumerate(old_pairs[0:-1]):
      next_char, _, _ = old_pairs[i+1]
      if next_char == "，":
        new_pairs.append((char, ph, "3"))
      elif next_char in ["。", "?", "!"]:
        new_pairs.append((char, ph, "4"))
      else:
        if psd == "3":
          new_pairs.append((char, ph, "2"))
        else:
          new_pairs.append((char, ph, psd))
    new_pairs.append(old_pairs[-1])
    return new_pairs
