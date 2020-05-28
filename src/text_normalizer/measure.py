# -*- coding: utf-8 -*-

import re

from src.text_normalizer.basic_util import val_num_to_chn, NumberSystem

SHORT_PAUSE_SYMBOL = " "  # 短停顿文本标志
LONG_PAUSE_SYMBOL = " "  # 长廷顿文本标志

MEASURE_NUMBER_PATTERN = r"(-?[\d,]+(\.\d+)?)"  # 匹配包括小数点的数字

measure_suffix_single_pattern = \
  r"(匹|张|座|回|场|尾|条|个|首|阙|阵|网|炮|顶|丘|棵|只|支|袭|辆|挑|担|颗|壳|窠|曲|墙|群|腔|\
     砣|座|客|贯|扎|捆|刀|令|打|手|罗|坡|山|岭|江|溪|钟|队|单|双|对|出|口|头|脚|板|跳|枝|件|贴| \
     针|线|管|名|位|身|堂|课|本|页|家|户|层|丝|毫|厘|分|钱|两|斤|担|铢|石|钧|锱|忽| \
     毫|厘|分|寸|尺|丈|里|寻|常|铺|程|撮|勺|合|升|斗|石|盘|碗|碟|叠|桶|笼|盆|' \
     盒|杯|钟|斛|锅|簋|篮|盘|桶|罐|瓶|壶|卮|盏|箩|箱|煲|啖|袋|钵|年|月|日|季|刻|时|周|天|秒|分|旬|' \
     纪|岁|世|更|夜|春|夏|秋|冬|代|伏|辈|丸|泡|粒|颗|幢|堆|条|根|支|道|面|片|张|颗|块|克|米)"
measure_suffix_double_pattern = \
  r"(公里|小时)"
measure_suffix_complex_pattern = \
  r"((千|分|厘|毫|微)米|(千|毫|微)克)"

measure_suffix_pattern = r"({0}|{1}|{2})".format(
  measure_suffix_complex_pattern, measure_suffix_double_pattern,
  measure_suffix_single_pattern)

MEASURE_PATTERN = r"({0}{1})".format(
  MEASURE_NUMBER_PATTERN, measure_suffix_pattern)


class Measure:
  def __init__(self):
    self.system = NumberSystem()
    self._measure_re = re.compile(MEASURE_PATTERN)
    self._measure_number_re = re.compile(MEASURE_NUMBER_PATTERN)

  def normalize(self, text):
    matchers = self._measure_re.findall(text)
    if matchers:
      for matcher in matchers:
        target = matcher[0]
        target = self._measure_number_normalize(target)
        text = text.replace(matcher[0], target)
    return text

  def _measure_number_normalize(self, text):
    matchers = self._measure_number_re.findall(text)
    if matchers:
      for matcher in matchers:
        target = matcher[0]
        target = val_num_to_chn(target, self.system)
        text = text.replace(matcher[0], target)
    return text


if __name__ == '__main__':
  print(Measure().normalize('我的车牌是粤AD74821。'))
  print(Measure().normalize("一共是10个人"))
  print(Measure().normalize("路程是10.23公里"))
  print(Measure().normalize("我今年83岁半了"))
