# -*- coding: utf-8 -*-

from src.text_normalizer.car_number import CarNumber
from src.text_normalizer.date import Date
# from src.text_normalizer.cardinal import cardinal2chntext, cardinal_normalize
from src.text_normalizer.digit import digit_normalize
from src.text_normalizer.english import English
from src.text_normalizer.measure import Measure
from src.text_normalizer.money import Money
from src.text_normalizer.special import Special
from src.text_normalizer.symbol import Symbol
from src.text_normalizer.telephone import TelePhone


class Text:
  def __init__(self):
    self._date = Date()
    self._money = Money()
    self._car_number = CarNumber()
    self._measure = Measure()
    self._telephone = TelePhone()
    self._english = English()
    self._special = Special()
    self._symbol = Symbol()
    pass

  @staticmethod
  def _preprocess(text):
    text = '^' + text + '$'
    text = text.replace('％', '%')
    return text

  @staticmethod
  def _postprocess(text):
    return text.lstrip('^').rstrip('$')

  def normalize(self, text):
    text = self._preprocess(text)

    # 非抢占性正则
    text = self._date.normalize(text)  # 规范化日期
    text = self._money.normalize(text)
    text = self._car_number.normalize(text)  # 规范车牌
    text = self._measure.normalize(text)
    # 抢占性正则
    text = self._telephone.normalize(text) # 规范化固话/手机号码
    text = self._english.normalize(text)  # 规范英文
    text = self._special.normalize(text)  # 规范分数以及百分比

    # 通用正则
    text = digit_normalize(text)  #规范化数字编号
    text = self._symbol.normalize(text)   # 规范化符号

    text = self._postprocess(text)
    return text



if __name__ == '__main__':
  # 测试程序
  print(Text().normalize('固话：059523865596或23880880。'))
  print(Text().normalize('手机：19859213959或15659451527。'))
  print(Text().normalize('分数：32477/76391。'))
  print(Text().normalize('百分数：80.30%。'))
  print(Text().normalize('编号：31520181154418。'))
  print(Text().normalize('纯数：2983.60克或12345.60米。'))
  print(Text().normalize('日期：1999年2月20日或09年3月15号。'))
  print(Text().normalize('金钱：12块5，34.5元，20.1万'))
  print(Text().normalize('车牌：粤A7482的轿车'))
  print(Text().normalize('特殊：O2O或B2C。'))
  print(Text().normalize('邮箱：zhangyue@163.com。'))
  print(Text().normalize('其它：名字格式为：首字+尾字'))
  print(Text().normalize('奥迪A5。'))
