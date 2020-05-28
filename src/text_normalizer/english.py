'''
@Descripttion: 英文字母以及单词正则
@Author: Markus
@Date: 2020-04-16 19:21:10
@LastEditors: Markus
@LastEditTime: 2020-04-17 19:56:08
'''

import re

from src.text_normalizer.digit import long_to_short


class English:
  """
  English类
  1. 大写字母串均会按照字母的方式，逐个大写字母输出
  2. 小写字母串如果支持中文读法，则会按照中文读法输出；否则按照字母的方式，逐个大写字母
  """
  def __init__(self):
    self._english_word_re = re.compile(r"(([a-zA-Z])+)")
    self._english_phoneme_list = []
    with open("/data1/liufeng/synthesis/frontend/data/english_word_dict") as f:
      for line in f:
        self._english_phoneme_list.append(line.split(" ")[0])

  def normalize(self, text):
    return self._english_word_normalize(text)

  def _english_word_normalize(self, text):
    matchers = self._english_word_re.findall(text)
    if matchers:
      for matcher in matchers:
        target = matcher[0]
        if target not in self._english_phoneme_list:
          # 如果在字典中，就说明这个这个英文单词是需要额外单独处理的
          target = target.upper()
          target = long_to_short(target)
        text = text.replace(matcher[0], target)
    return text


if __name__ == '__main__':
  print(English().normalize('hello'))
  print(English().normalize('abcdefghijklmnopqrstuvwxyz'))
  print(English().normalize('这个问题就像abc一样简单'))
