"""
@Descripttion:
@Author: Markus
@Date: 2020-04-10 19:51:09
@LastEditors: Markus
@LastEditTime: 2020-04-12 23:22:18
"""
import re

from src.text_normalizer.basic_util import NumberSystem
from src.text_normalizer.digit import digit_normalize


class Date:
  def __init__(self):
    self.system = NumberSystem()

    month_day_pattern = r"((\d+)[月日号])" # 用来匹配月日号前的数字
    two_year_pattern = r"([6-9]|[0,1])[0-9]年"  # 60~99年, 00~09年, 10~19年
    four_year_pattern = r"(1[0-9][0-9][0-9]|20[0-9][0-9])年"  # 1000~1999/2000～
    year_pattern = "({}|{})".format(two_year_pattern, four_year_pattern)
    month_pattern = r"((0?[1-9]|1[0-2])月)"  # (0)1~(0)9月，10~12月
    day_pattern = r"((0?[1-9]|[1-3][0-9])[日号])"  # (0)1~(0)9日/号，10~39日/号
    date_pattern = r"({0}|{1}|{2})".format(
      year_pattern, month_pattern, day_pattern)

    self.date_re = re.compile(date_pattern)
    self.month_day_re = re.compile(month_day_pattern)

  def normalize(self, text):
    matchers = self.date_re.findall(text)
    if matchers:
      for matcher in matchers:
        target = matcher[0]
        target = self._date_num_normalize(target)
        target = digit_normalize(target)
        text = text.replace(matcher[0], target)
    return text

  def _date_num_normalize(self, text):
    matchers = self.month_day_re.findall(text)
    if matchers:
      for matcher in matchers:
        target = matcher[0]
        target = target.lstrip('0')
        text = text.replace(matcher[0], target)
    return text

if __name__ == '__main__':
  print(Date().normalize('今年是09年3月16日啊'))
  print(Date().normalize('今年是09年03月31日啊'))
  print(Date().normalize('今年是3月20日啊'))
  print(Date().normalize('3月20日'))
  print(Date().normalize('1929年'))
