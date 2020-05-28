#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:liufeng
# datetime:2020/3/30 8:52 PM
# software: PyCharm


from typing import Dict, Any

from kashgari.layers import L
from kashgari.layers.crf import CRF
from kashgari.tasks.labeling.base_model import BaseLabelingModel
from kashgari.utils import custom_objects
from tensorflow import keras

custom_objects['CRF'] = CRF


class BiLSTM_CRF_Model(BaseLabelingModel):
  """Bidirectional LSTM CRF Sequence Labeling Model"""

  @classmethod
  def get_default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
    """
    Get hyper parameters of model
    Returns:
        hyper parameters dict
    """
    return {
      'layer_blstm': {
        'units': 128,
        'return_sequences': True
      },
      'layer_dense': {
        'units': 64,
        'activation': 'tanh'
      }
    }

  def build_model_arc(self):
    """
    build model architectural
    """
    output_dim = len(self.processor.label2idx)
    config = self.hyper_parameters
    embed_model = self.embedding.embed_model

    layer_blstm = L.Bidirectional(L.LSTM(**config['layer_blstm']),
                                  name='layer_blstm')
    layer_dense = L.Dense(**config['layer_dense'], name='layer_dense')
    layer_crf_dense = L.Dense(output_dim, name='layer_crf_dense')
    layer_crf = CRF(output_dim, name='layer_crf')
    self.layer_crf = layer_crf

    print("build embed model:")
    print("input:", embed_model.inputs)
    print("output:", embed_model.output)
    self.embed_model = keras.Model(embed_model.inputs, embed_model.output)

    print("build post model:")
    second_input_0 = keras.Input(shape=embed_model.outputs[0].shape[1:],
                                 name="second_input")
    print("input:", second_input_0)
    # second_input_1 = tf.keras.Input(shape=embed_model.outputs[1].shape[1:])
    # self.post_model = post_model(second_input_0)
    tensor = layer_blstm(second_input_0)
    tensor = layer_dense(tensor)
    tensor = layer_crf_dense(tensor)
    output_tensor = layer_crf(tensor)
    self.post_model = keras.Model(second_input_0, output_tensor)

    print("build total model:")
    tensor = layer_blstm(embed_model.output)
    tensor = layer_dense(tensor)
    tensor = layer_crf_dense(tensor)
    output_tensor = layer_crf(tensor)
    self.tf_model = keras.Model(embed_model.inputs, output_tensor)
    print("finished")

  def compile_model(self, **kwargs):
    if kwargs.get('loss') is None:
      kwargs['loss'] = self.layer_crf.loss
    if kwargs.get('metrics') is None:
      kwargs['metrics'] = [self.layer_crf.viterbi_accuracy]
    super(BiLSTM_CRF_Model, self).compile_model(**kwargs)


if __name__ == '__main__':
  pass
