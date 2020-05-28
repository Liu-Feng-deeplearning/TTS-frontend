#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019-10-25 17:23
# @Author  : liufeng

import jieba

from src.utils import PUNC
from src.utils import check_all_chinese
from src.utils import read_dict


class TranscriptToPinyin:
  """ 带有标点的文本转换为带有标点的拼音 """
  def __init__(self, dic_path, eng_dic_path=None):
    self.dict = read_dict(dic_path)
    if eng_dic_path:
      self.eng_dict = read_dict(eng_dic_path)
    else:
      self.eng_dict = None

  def get_phone_pairs(self, sentence, change_eng_symbol=False,
                      modify_by_rules=True):
    """获得(字符-拼音-韵律)文本对"""
    phone_pairs = []
    transcript = jieba.lcut(sentence)
    psd_pairs = []
    for word in transcript:
      if word in self.dict.keys():
        phone = self.dict[word.lower()]
        phone_pairs.append((word, phone))
      else:
        for char in word:
          phone = self.dict[char.lower()]
          phone_pairs.append((char, phone))

      if word in PUNC:
        psd_pairs.append("5")
      else:
        if (not check_all_chinese(word)) and (word in self.dict.keys()):
          psd_pairs.append("1")
        else:
          psd_pairs.extend(["0"]*(len(word)-1))
          psd_pairs.append("1")

    phone_pairs = self._split_pairs(phone_pairs)
    if change_eng_symbol:
      phone_pairs = self._change_eng_symbol(phone_pairs)

    if modify_by_rules:
      phone_pairs = change_yi(phone_pairs)
      phone_pairs = change_bu(phone_pairs)
      phone_pairs = sandhi(phone_pairs)

    assert len(phone_pairs) == len(psd_pairs)

    total_pairs = [(char, ph, psd) for (char, ph), psd in
                   zip(phone_pairs, psd_pairs)]
    new_total_pairs = []
    for i in range(len(total_pairs)-1):
      if total_pairs[i+1][0] == "，":
        new_total_pairs.append((total_pairs[i][0], total_pairs[i][1], "3"))
      elif total_pairs[i+1][0] == "。":
        new_total_pairs.append((total_pairs[i][0], total_pairs[i][1], "4"))
      else:
        new_total_pairs.append(total_pairs[i])
    new_total_pairs.append(total_pairs[-1])
    return new_total_pairs

  def _change_eng_symbol(self, sent_phones):
    eng_sent_phones = []
    for char, phone in sent_phones:
      if char.lower() in self.eng_dict.keys() and len(char) == 1:
        phone_modified = self.eng_dict[char.lower()]
      else:
        phone_modified = phone
      eng_sent_phones.append((char, phone_modified))
    return eng_sent_phones

  def _split_pairs(self, phone_pairs):
    new_phone_pairs = []
    for chars, phones in phone_pairs:
      if (not check_all_chinese(chars)) and (chars.lower() in self.dict.keys()):
        new_phone_pairs.append((chars, phones))
      else:
        for index, char in enumerate(chars):
          sub_phone = " ".join(phones.split()[index * 3:index * 3 + 3])
          new_phone_pairs.append((char, sub_phone))
    return new_phone_pairs


def change_yi(pairs):
  """ for 一的特殊规则。 规则：四声之前变二声，一二三声之前变四声。  """
  new_pairs = []
  for index, (char, phone) in enumerate(pairs):
    if char == "一" and index < len(pairs) - 1:
      if pairs[index + 1][0] in "零一二三四五六七八九十":
        # new_pairs.append((char, phone))
        new_pairs.append((char, "ii i *1"))
      elif pairs[index + 1][1].split()[-1] == "*4":
        # new_pairs.append((char, phone.replace("*1", "*2")))
        new_pairs.append((char, "ii i *2"))
      elif pairs[index + 1][1].split()[-1] == "*3":
        new_pairs.append((char, "ii i *4"))
      elif pairs[index + 1][1].split()[-1] == "*2":
        new_pairs.append((char, "ii i *4"))
      elif pairs[index + 1][1].split()[-1] == "*1":
        new_pairs.append((char, "ii i *4"))
      else:
        # new_pairs.append((char, phone))
        new_pairs.append((char, "ii i *1"))
    else:
      new_pairs.append((char, phone))
  return new_pairs


def change_bu(pairs):
  """ for 不对特殊规则替换。 规则：四声之前变二声，一二三声之前变四声。"""
  new_pairs = []
  for index, (char, phone) in enumerate(pairs):
    if char == "不" and index < len(pairs) - 1:
      if pairs[index + 1][1].split()[-1] == "*4":
        new_pairs.append((char, phone.replace("*4", "*2")))
      else:
        new_pairs.append((char, phone))
    else:
      new_pairs.append((char, phone))
  return new_pairs


def coarticulate(pairs):
  """协同发音 or 语流音变 33 -> 23 333 -> 223"""
  new_pairs = []
  for index, (char, phone) in enumerate(pairs[1:]):
    if phone[-1] == '3' and pairs[index][1][-1] == '3':
      new_pairs.append((pairs[index][0], pairs[index][1][:-1] + "2"))
    else:
      new_pairs.append(pairs[index])
  new_pairs.append(pairs[-1])
  return new_pairs


def sandhi(pairs):
  """基于规则的语音变调系统 """
  # Note: 默认要求如果英文为小写代表单词，大写代表字母。
  # 如果英文单词（小写形式）不在词典内，会报错。
  sentence = "".join([c for c, _ in pairs])
  transcript = jieba.lcut(sentence)
  new_pairs, index = [], 0
  for word in transcript:
    if not check_all_chinese(word) and word.lower() == word:
      _pairs = pairs[index:index + 1]
      index += 1
      new_pairs.extend(_pairs)
    else:
      old_pairs = pairs[index:index+len(word)]
      _pairs = old_pairs
      index += len(word)
      _pairs = change_yi(_pairs)
      _pairs = change_bu(_pairs)
      _pairs = coarticulate(_pairs)
      if old_pairs != _pairs:
        print("sandhi for {}: {}->{}".format(
          "".join([c for c, _ in old_pairs]),
          " ".join([p for _, p in old_pairs]),
          " ".join([p for _, p in _pairs])))
      new_pairs.extend(_pairs)
  return new_pairs


if __name__ == '__main__':
  dict_path = "/data1/liufeng/synthesis/frontend/data/pronunciation_dictionary"
  eng_dict_path = "/data1/liufeng/synthesis/TACOTRON-2-refined/data/" \
                  "pronunciation/pronunciation_dictionary_ph1"
  tran = TranscriptToPinyin(dict_path, eng_dict_path)
  phone_pair = tran.get_phone_pairs("哦一个是八三八的邮箱。")
  print(phone_pair)
