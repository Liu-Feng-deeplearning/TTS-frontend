# -*- coding: utf-8 -*-

import re

from src.text_normalizer.basic_util import val_num_to_chn, NumberSystem

num_pattern = r"([\d,]+(\.\d+)?)"  # 匹配包括小数点的数字
jinzhi_pattern = r"(亿|千万|百万|万|千|百)"
money_mark_pattern = r"([元块角毛分])"
money_currecy_pattern = '(人民币|美元|日元|英镑|欧元|马克|法郎|加拿大元|澳元|港币|先令|芬兰马克|爱尔兰镑|' \
                 '里拉|荷兰盾|埃斯库多|比塞塔|印尼盾|林吉特|新西兰元|比索|卢布|新加坡元|韩元|泰铢)'
currency_pattern = r"({0}|{0}?({1}|{2}))".format(jinzhi_pattern, money_mark_pattern, money_currecy_pattern)
money_pattern = r"(({0}[多余几]|{0}[多余几]?{1})+)".format(num_pattern, currency_pattern)


class Money:
  def __init__(self):
    self.system = NumberSystem()
    self.money_pattern = re.compile(money_pattern)
    self.num_pattern = re.compile(num_pattern)

  def normalize(self, text):
    matchers = self.money_pattern.findall(text)
    if matchers:
      for matcher in matchers:
        target = matcher[0]
        target = self._money_num_normalize(target)
        text = text.replace(matcher[0], target)
    return text

  def _money_num_normalize(self, text):
    matchers = self.num_pattern.findall(text)
    if matchers:
      for matcher in matchers:
        target = matcher[0]
        target = target.replace(",", "")  # 从129,000.123移除,符号
        text = text.replace(matcher[0], val_num_to_chn(target, self.system))
    return text


if __name__ == '__main__':
  print(Money().normalize('21.5万元'))
  print(Money().normalize('230块5毛'))
  print(Money().normalize('总共为30,000多'))
  print(Money().normalize('总共为30,000人民币'))
