#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/04/16 11:15
# @Author  : liufeng


class ChUnit:
  """ 读法单位 """

  def __init__(self, power, simplified):
    self.power = power
    self.simplified = simplified

  def __str__(self):
    return '10^{}'.format(self.power)


class ChDigit:
  """ 中文数字字符 """

  def __init__(self, value, simplified):
    self.value = value
    self.simplified = simplified

  def __str__(self):
    return str(self.value)


class ChMath:
  """ 中文小数点 """

  def __init__(self, symbol, simplified):
    self.symbol = symbol
    self.simplified = simplified
    return


class NumberSystem:
  def __init__(self):
    power = [1, 2, 3, 4, 8]
    simplified = [s for s in '十百千万亿']
    self.units = [ChUnit(i, v) for i, v in zip(power, simplified)]
    nums = '零一二三四五六七八九'
    self.digits = [ChDigit(i, v) for i, v in enumerate(nums)]
    self.point = ChMath('.', '点')
    return


def __get_value(value_str, system):
  """ 使用迭代方法，计算数值和对应单位
  eg: 10260.03 -> [1, 10^4, 2, 10^2, 6, 10^1, 点, 0, 3]

  """
  striped_string = value_str.lstrip('0')
  if not striped_string:
    return []
  elif len(striped_string) == 1:
    return [system.digits[int(striped_string)]]
  else:
    result_unit = next(u for u in reversed(
      system.units) if u.power < len(striped_string))
    result_string = value_str[:-result_unit.power]
    return __get_value(result_string, system) + [result_unit] + __get_value(
      striped_string[-result_unit.power:], system)


def seq_num_to_chn(number_string, system):
  """ 序列数字转成对应读法
    eg: 1234 -> 一二三四(序列型读法)

    Args:
      number_string: 字符串型数字
      system: 数字读音系统

    Returns:
      str
    """
  int_string = number_string
  result_symbols = [system.digits[int(c)] for c in int_string]
  result = ''.join([s.simplified for s in result_symbols])
  return result


def val_num_to_chn(number_string, system):
  """ 数值数字转成对应读法
  eg: 1234 -> 一千二百三十四(数值型读法)

  Args:
    number_string: 字符串型数字
    system: 数字读音系统

  Returns:
    str
  """
  if number_string[0] == "-":
    return "负" + val_num_to_chn(number_string[1:], system)

  int_dec = number_string.split('.')
  if len(int_dec) == 1:
    int_string, dec_string = int_dec[0], ""
  elif len(int_dec) == 2:
    int_string, dec_string = int_dec[0], int_dec[1]
  else:
    raise ValueError(
      "invalid input with more than one dot: {}".format(number_string))

  if len(int_string) > 1:
    result_symbols = __get_value(int_string, system)
  else:
    result_symbols = [system.digits[int(c)] for c in int_string]

  if dec_string:
    dec_symbols = [system.digits[int(c)] for c in dec_string]
    result_symbols += [system.point] + dec_symbols

  result = ''.join([s.simplified for s in result_symbols])

  if len(result) >= 2 and result[0] == "一" and result[1] == "十":
    result = result[1:]  # 11 -> 十一（not 一十一）
  return result


if __name__ == '__main__':
  # 测试程序
  num_sys = NumberSystem()
  print()
  print('0:', val_num_to_chn('0', num_sys))
  print('10:', val_num_to_chn('10', num_sys))
  print('10260.03:', val_num_to_chn('10260.03', num_sys))
  print('1234:', val_num_to_chn('1234', num_sys))
  print('320000:', val_num_to_chn('320000', num_sys))
  print('123456789:', val_num_to_chn('123456789', num_sys))
  print('-197.4:', val_num_to_chn('-197.4', num_sys))
  print('120000:', seq_num_to_chn('120000', num_sys))
