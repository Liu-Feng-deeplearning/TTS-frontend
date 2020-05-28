# -*- coding: utf-8 -*-
"""DIGIT类

"""


import re

from src.text_normalizer.basic_util import seq_num_to_chn, NumberSystem


def long_to_short(text, split=" "):
  text_len = len(text)
  new_text = ""

  if text_len < 6:  # 1, 2, 3, 4, 5
    return text
  elif text_len == 6:
    return text[0:3] + split + text[3:6]
  else:
    last_part = ""
    # todo: 这段代码可以写的更清晰。

    while text_len % 4 != 0:
      last_part = text[-3:] + split + last_part
      text = text[:-3]
      text_len = len(text)

    for i in range(int(text_len / 4)):
      new_text += text[i * 4: (i + 1) * 4] + split

    new_text += last_part
    new_text = new_text[:-1]  # 消除最后一个空格
    return new_text


def digit2chntext(text, alt_one=False, split_long=True):
  num_sys = NumberSystem()
  text = seq_num_to_chn(text, num_sys)
  if split_long:
    text = long_to_short(text)
  if alt_one ==True:
    text = text.replace("一", "幺")

  return text

def digit_normalize(text, alt_one=False, split_long=True):
  pattern = re.compile(r"((\d+))")
  matchers = pattern.findall(text)
  if matchers:
    for matcher in matchers:
      target = matcher[0]
      target = digit2chntext(target, alt_one=False, split_long=True)
      text = text.replace(matcher[0], target, 1)
  return text


if __name__ == '__main__':
  print(digit_normalize('编号：31520181154418。'))
  print(digit2chntext('12345672234', alt_one=True))


