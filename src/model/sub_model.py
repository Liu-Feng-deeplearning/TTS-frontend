#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pickle

import kashgari
import tensorflow as tf
from kashgari.embeddings import BERTEmbedding
from tensorflow.python.keras.backend import set_session

from src.model.model_utils import h5_to_pb
# from kashgari.tasks.labeling import BiLSTM_CRF_Model
from src.model.model_v2 import BiLSTM_CRF_Model

kashgari.config.use_cudnn_cell = False


class SubModel:
  """ 目前只支持长度50，输入字符数49 + 终结符 """
  def __init__(self, bert_model_path=None, model_dir=None):
    self._bert_model_path = bert_model_path
    self._phone_model_path = os.path.join(model_dir, "phone.hdf5")
    self._prosody_model_path = os.path.join(model_dir, "prosody.hdf5")
    self._data_path = os.path.join(model_dir, "feature.pkl")
    self._psd_data_path = os.path.join(model_dir, "feature_psd.pkl")
    self._pb_dir = os.path.join(model_dir, "pb")
    os.makedirs(self._pb_dir, exist_ok=True)
    self._embed_model = None
    self._prosody_model, self._phone_model = None, None

    self.sess = None
    # self.sess = tf.Session()
    # set_session(self.sess)
    return

  def initial_total_model(self):
    # 同时加载prosody和phone
    print('=============init bert model=========================')
    print("bert model path:", self._bert_model_path)
    print("phone model path:", self._phone_model_path)
    print("prosody model path:", self._prosody_model_path)

    self.sess = tf.Session()
    set_session(self.sess)

    self._embed_model = BERTEmbedding(self._bert_model_path,
                                      task=kashgari.LABELING,
                                      sequence_length=50)

    self._prosody_model = BiLSTM_CRF_Model(self._embed_model)
    train_data, train_label, test_data, test_label = \
        pickle.load(open(self._psd_data_path, 'rb'))
    self._prosody_model.build_model(x_train=train_data, y_train=train_label,
                                    x_validate=test_data, y_validate=test_label)
    self._prosody_model.compile_model()
    self._prosody_model.tf_model.load_weights(self._prosody_model_path)

    self._phone_model = BiLSTM_CRF_Model(self._embed_model)
    train_data, train_label, test_data, test_label = \
        pickle.load(open(self._data_path, 'rb'))
    self._phone_model.build_model(x_train=train_data, y_train=train_label,
                                  x_validate=test_data, y_validate=test_label)
    self._phone_model.compile_model()
    self._phone_model.tf_model.load_weights(self._phone_model_path)
    print('============= model loaded=========================')
    return

  def _write_dict(self):
    label_path = os.path.join(self._pb_dir, "idx2label.txt")
    with open(label_path, "w", encoding="utf-8") as fr:
      for key, value in self._prosody_model.embedding.label2idx.items():
        fr.write("{} {}\n".format(value, key))

    token_path = os.path.join(self._pb_dir, "token2idx.txt")
    with open(token_path, "w", encoding="utf-8") as fr:
      for key, value in self._prosody_model.embedding.token2idx.items():
        if len(key) > 0:
          fr.write("{} {}\n".format(key, value))

  def predict(self, sentence_list):
    """ 通过句子预测韵律，标点断开 """
    bert_input = []
    for sent in sentence_list:
      assert len(sent) < 50
      bert_input.append([c for c in sent])
    print("bert-input:", bert_input)
    prosody = self._prosody_model.predict(bert_input)
    return prosody

  def compute_bert_embed(self, sentence_list):
    seq = [len(sent) for sent in sentence_list]
    bert_input = [[c for c in sent] for sent in sentence_list]
    token = self._prosody_model.embedding.process_x_dataset(bert_input)
    embedding = self._prosody_model.embed_model.predict(token)
    token = [t[0, 0:s + 2] for t, s in zip(token, seq)]  # 不输出pad符号
    return token, embedding

  def compute_post_label(self, bert_embed):
    post_label = self._prosody_model.post_model.predict(bert_embed)
    return post_label

  def save_pb(self):
    self._write_dict()
    # [print(n.name) for n in tf.get_default_graph().as_graph_def().node]
    print("===== save pb =====")
    h5_to_pb(self._prosody_model.post_model, self._pb_dir, self.sess,
             "model_embed.pb", ["output_embed"])
    print("save pb file to {}".format("model_embed.pb"))

    h5_to_pb(self._prosody_model.post_model, self._pb_dir, self.sess,
             "model_post_psd.pb", ["output_psd"])
    print("save pb file to {}".format("model_psd.pb"))

    h5_to_pb(self._prosody_model.tf_model, self._pb_dir, self.sess,
             "model_tot_psd.pb", ["output_psd"])
    print("save pb file to {}".format("model_psd.pb"))
    return
