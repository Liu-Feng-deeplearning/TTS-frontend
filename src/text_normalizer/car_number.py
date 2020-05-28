# -*- coding: utf-8 -*-

"""
@Descripttion:
@Author: Markus
@Date: 2020-04-16 14:07:51
@LastEditors: Markus
@LastEditTime: 2020-04-16 15:44:10
"""

import re

from src.text_normalizer.digit import digit_normalize

SHORT_PAUSE_SYMBOL = " "  # 短停顿文本标志
LONG_PAUSE_SYMBOL = " "  # 长廷顿文本标志


class CarNumber:
  def __init__(self):
    """ 车牌号码正则: 前缀+后端序列
    前缀: 前缀由各地省份缩写+大写字母构成
    后端序列: 序列为4-6位数字+大写字母构成
    """
    car_prefix_re = \
        r"([京津沪渝蒙新藏宁桂港澳黑吉辽晋冀青鲁豫苏皖浙闽赣湘鄂粤琼甘贵云陕台][A-Z])"
    car_sequence_pattern = r"([\dA-Z]{4,6})"
    car_num_re = "({0}\s?{1})".format(car_prefix_re, car_sequence_pattern)
    self.car_number_re = re.compile(car_num_re)

  def normalize(self, text):
    """ 在车牌首字和车牌尾序列之间添加停顿 """
    matchers = self.car_number_re.findall(text)
    if matchers:
      for matcher in matchers:
        target = matcher[0]
        target = target.replace(" ", "")  # 移除"粤A D74821"中的空格
        prefix = target[:2]
        remain = digit_normalize(target[2:])
        target = prefix + SHORT_PAUSE_SYMBOL + remain
        text = text.replace(matcher[0], target)
    return text


if __name__ == '__main__':
  # 测试
  print(CarNumber().normalize('我的车牌是粤AD74821。'))
  print(CarNumber().normalize('我的车牌是粤A D74821。'))
