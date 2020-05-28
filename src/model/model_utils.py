#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:liufeng
# datetime:2020/3/19 11:56 AM
# software: PyCharm

import tensorflow as tf
from tensorflow.python.framework import graph_io


def h5_to_pb(h5_model, output_dir, sess, model_name, output_name):
  tf.keras.backend.set_learning_phase(0)
  for i in range(len(h5_model.inputs)):
    print("input-tensor name and shape：", h5_model.inputs[i])
  assert len(h5_model.outputs) == len(output_name)

  out_nodes = []
  for i in range(len(h5_model.outputs)):
    out_nodes.append(output_name[i])
    tf.identity(h5_model.outputs[i], output_name[i])
    print("change output node {} to {}".format(h5_model.outputs[i],
                                               output_name[i]))

  init_graph = sess.graph.as_graph_def()
  # main_graph = graph_util.convert_variables_to_constants(sess, init_graph,
  #                                                        out_nodes)
  from src.tf_modify import convert_variables_to_constants
  # Note: tf原版函数有bug，LSTM和GRU无法存图
  # 改动函数来自: https://github.com/intel-analytics/analytics-zoo/blob/master/
  # pyzoo/zoo/util/tf_graph_util.py#L226
  main_graph = convert_variables_to_constants(sess, init_graph, out_nodes)
  graph_io.write_graph(main_graph, output_dir, name=model_name,
                       as_text=False)
  # print("save pb file to {}".format(model_name))
  graph_io.write_graph(main_graph, output_dir,
                       name=model_name.replace(".pb", "_txt.pb"),
                       as_text=True)
  # print("save pb file to {}".format(model_name.replace(".pb", "_txt.pb")))
  return


if __name__ == '__main__':
  pass
