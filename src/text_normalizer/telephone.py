# -*- coding: utf-8 -*-
"""TELEPHONE类
电话号码 <=> 中文字符串 方法
中文字符串 <=> 电话号码 方法
"""
import re

from src.text_normalizer.digit import digit2chntext

SHORT_PAUSE_SYMBOL = " "

begin_pattern = r"([^\d]+|^)" # 开始标志
end_pattern = r"([^\d]+|$)" # 结尾标志
num_pattern = r"((\d)+)"

telephone_area_num_pattern = r"(010|02\d|03\d{2}|04\d\d|05\d\d|07\d\d\|08\d\d|09\d\d)" # 区号 010，02x，03xx，04xx，05xx，07xx，08xx，09xx
telephone_landline_branch_pattern = r"(\d{7,8})"#7或8位座机号
telephone_landline_pattern = r"({0}{1}?{2}{3})".format(
    begin_pattern, telephone_area_num_pattern,
    telephone_landline_branch_pattern, end_pattern) # 区号+座机号
telephone_area_num_pattern = r"(139|138|137|136|135|134|159|158|157|150|151|"\
    "152|188|187|182|183|184|178|198|130|131|132|156|155|186|185|176|"\
    "133|153|189|180|181|177)"
telephone_mobile_pattern = r"({0}{1}\d{{8}}{2})".format(
    begin_pattern, telephone_area_num_pattern, end_pattern)


class TelePhone:
  """TELEPHONE类
  """
  def __init__(self):
    self._telephone_landline_re = re.compile(telephone_landline_pattern)
    self._telephone_mobile_re = re.compile(telephone_mobile_pattern)
    self._telephone_num_re = re.compile(num_pattern)

  def normalize(self, text):
    text = self._telephone_mobile_normalize(text)
    text = self._telephone_landline_normalize(text)
    return text

  def _telephone_landline_normalize(self, text):
    matchers = self._telephone_landline_re.findall(text)
    while matchers:
      for matcher in matchers:
        target = matcher[0]
        target = self._telephone_number_normalize(target, is_mobile=False)
        text = text.replace(matcher[0], target)
      matchers = self._telephone_landline_re.findall(text)
    return text

  def _telephone_mobile_normalize(self, text):
    matchers = self._telephone_mobile_re.findall(text)
    while matchers:
      for matcher in matchers:
        target = matcher[0]
        target = self._telephone_number_normalize(target, is_mobile=True)
        text = text.replace(matcher[0], target)
      matchers = self._telephone_mobile_re.findall(text)
    return text

  def _telephone_number_normalize(self, text, is_mobile=True):
    matchers = self._telephone_num_re.findall(text)
    if matchers:
      for matcher in matchers:
        target = matcher[0]
        if is_mobile:
          target = digit2chntext(target, alt_one=True, split_long=False)
          target = target[:3] + SHORT_PAUSE_SYMBOL + target[3:7] + SHORT_PAUSE_SYMBOL + target[7:11]
        else:
          target = digit2chntext(target, alt_one=True, split_long=True)
        text = text.replace(matcher[0], target, 1)
    return text

if __name__ == '__main__':
    # 测试程序
    print(TelePhone().normalize('欢迎拨打电话4930286呀'))
    print(TelePhone().normalize('欢迎拨打电话62552560呀'))
    print(TelePhone().normalize('欢迎拨打电话01062552560呀'))
    print(TelePhone().normalize('我的手机是15190990987'))
    print(TelePhone().normalize('手机：19859213959或15659451527。'))
