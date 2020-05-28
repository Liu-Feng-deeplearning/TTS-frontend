#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/7/26 21:15
# @Author  : liufeng

PUNC = ["，", "。", "、", "！", "？"]
ENG = "abcdefghijklmnopqrstuvwxyz"


def clean_sentence(sentence):
  sentence = sentence.replace("：", "，")
  sentence = sentence.replace("、", "，")
  sentence = sentence.replace("；", "，")
  sentence = sentence.replace("“", "")
  sentence = sentence.replace("”", "")
  sentence = sentence.replace("（", "")
  sentence = sentence.replace("）", "")
  sentence = sentence.replace("《", "")
  sentence = sentence.replace("》", "")
  sentence = sentence.replace("/", "")
  sentence = sentence.replace(",", "，")
  sentence = sentence.replace("?", "？")
  sentence = sentence.replace("!", "！")
  sentence = sentence.replace("-", "杠")
  sentence = sentence.replace(".", "点")
  sentence = sentence.replace("@", "艾特")
  sentence = sentence.replace("&", "和")
  if sentence[-1] not in PUNC:
    sentence += "。"
  return sentence


def rm_prosody(line):
  line = line.replace("#1", "")
  line = line.replace("#2", "")
  line = line.replace("#3", "")
  line = line.replace("#4", "")
  return line


def read_lines(data_path):
  lines = []
  with open(data_path, encoding="utf-8") as fr:
    for line in fr.readlines():
      if len(line.strip().replace(" ", "")):
        lines.append(line.strip())
  print("read {} lines from {}".format(len(lines), data_path))
  return lines


def write_lines(data_path, lines):
  with open(data_path, "w", encoding="utf-8") as fw:
    for line in lines:
      fw.write("{}\n".format(line))
    print("write {} lines to {}".format(len(lines), data_path))


def merge_psd(pairs):
  """
  input: 三是组织上反复酝酿。0200101045
  output:三是#2组织上#1反复#1酝酿#4。
  """
  text = "".join([c + "#" + psd for c, psd in pairs])
  text = text.replace("#0", "").replace("#5", "")
  return text


def split_psd(text, pairs=True):
  """input:三是#2组织上#1反复#1酝酿#4。
  output: 三是组织上反复酝酿。0200101045
  """
  num = "012345"

  norm_text = []
  for i in range(len(text)-1):
    if text[i] == "#" or text[i] in num:
      norm_text.append(text[i])
    elif text[i] in PUNC:
      norm_text.append(text[i])
      norm_text.append("#5")
    else:
      if text[i+1] == "#" or text[i+1] in num:
        norm_text.append(text[i])
      else:
        norm_text.append(text[i])
        norm_text.append("#0")

  if text[-1] not in num:
    norm_text.append(text[-1])
    norm_text.append("#5")
  else:
    norm_text.append(text[-1])
  norm_text = "".join(norm_text)

  # print(text, norm_text)
  assert len(norm_text) % 3 == 0
  x = [norm_text[3*i] for i in range(len(norm_text)//3)]
  y = [norm_text[3*i+2] for i in range(len(norm_text)//3)]
  psd_pairs = [(norm_text[3*i], norm_text[3*i+2])
               for i in range(len(norm_text)//3)]
  if pairs:
    return psd_pairs
  else:
    return x, y


def phone2pairs(sentence, phone):
  """ 返回文字和拼音的映射对 """
  sent_phone = []
  phone_list = phone.split()
  ph_index = 0

  for char in sentence:
    # print(char, ph_index)
    if phone_list[ph_index] in ["sil", "breath"]:
      sent_phone.append((phone_list[ph_index], phone_list[ph_index]))
      ph_index += 1

    if char in ["。", "！", "？", "，", "、"]:
      sent_phone.append((char, phone_list[ph_index]))
      ph_index += 1
    elif char in ["sil", "breath"]:
      pass
    elif char.lower() in ["f", "h", "l", "m", "r", "s"]:
      sent_phone.append((char, " ".join(phone_list[ph_index: ph_index + 6])))
      ph_index += 6
    elif char.lower() in ["w", "x"]:
      sent_phone.append((char, " ".join(phone_list[ph_index: ph_index + 9])))
      ph_index += 9
    else:
      sent_phone.append((char, " ".join(phone_list[ph_index: ph_index + 3])))
      ph_index += 3
      pass

  if not ph_index == len(phone_list):
    print("Error: num mismath", sent_phone)
    return None
  return sent_phone


def read_dict(dict_path):
  pron_dict = dict()
  with open(dict_path, encoding="utf-8") as fr:
    for line in fr.readlines():
      key = line.split()[0]
      value = (" ".join(line.split()[1:]))
      value = split_tone(value)
      if key in pron_dict.keys():
        print("Error: same phone {}".format(key))
      else:
        pron_dict[key] = value
  return pron_dict


def check_all_chinese(text):
  """ 判断传入字符串是否包含中文

  Args:
    text: 待判断字符串

  Return:
    True:包含中文  False:不包含中文

  """
  for char in text:
    if is_chinese(char):
      return True
  return False


def check_exist_eng(line):
  for char in line:
    if char.lower() in ENG:
      return True
  return False


def get_align_pairs(align_path):
  align_lines = read_lines(align_path)
  align_dict = dict()
  for line in align_lines:
    key = line.strip().split("|")[0]
    pairs = []
    for pair in line.strip().split("|")[1:]:
      pairs.append((pair.split(",")[0], float(pair.split(",")[1]),
                    float(pair.split(",")[2])))
    align_dict[key] = pairs
  return align_dict


def __sentence_punc_clean(sentence, split_label):
  if sentence[-1] not in PUNC:
    if split_label == "":
      sentence += "。"
    elif split_label == " ":
      sentence += " 。"
    else:
      pass
  return sentence


def get_sentences(text_path):
  sentences = []
  with open(text_path, encoding="utf-8") as fr:
    for line in fr.readlines():
      if line.strip() == "END":
        return sentences
      elif len(line.strip()) == 0 or line[0] == "#":
        continue
      else:
        sentences.append(line.strip())
  return sentences


def split_sentence(sentence, split_type="char"):
  """ split sentence using punc

  Args:
    sentence: str
    split_type: 可以是" "（空格），针对拼音等以空格分割的格式；
                 也可以是None（""），针对汉字。

  Returns:
    list[str,str ...]

  """
  if split_type == "phone":
    split_label = " "
  elif split_type == "char":
    split_label = ""
  else:
    raise Exception("Error")

  sentence = __sentence_punc_clean(sentence, split_label)
  sentence_split = []
  sub_sentence_list = []
  if split_label == " ":
    chars = sentence.split()
  else:
    chars = [char for char in sentence]
  for char in chars:
    if char in PUNC:
      sub_sentence_list.append(char)
      sentence_split.append(split_label.join(sub_sentence_list))
      sub_sentence_list = []
    else:
      sub_sentence_list.append(char)
  return sentence_split


def split_phone_format(old_ph):
  """将字典拼音格式改成标准格式 ‘iii4’ -> 'ii i *4' """

  _characters_i = ['b', 'd', 'c', 'ch', 'f', 'g', 'h', 'p', 'x', 'z', 'zh',
                   'q', 'r', 's', 'sh', 'j', 'k', 'l', 'm', 'n', 't', 'ii',
                   'uu', 'vv', 'oo', 'aa', 'ee', ]

  _characters_s = ['a', 'ai', 'an', 'ang', 'ao', 'e', 'ei', 'en', 'eng',
                     'er', 'i', 'ia', 'ian', 'iang', 'iao', 'ie', 'in', 'ing',
                     'io', 'iong', 'iu', 'ix', 'iy', 'iz', 'o', 'ong', 'ou',
                     'u', 'ua', 'uai', 'uan', 'uang', 'ueng', 'ui',
                     'un', 'uo', 'v', 'van', 've', 'vn']

  if old_ph in ['。', '！', '？', '，']:
    new_ph = old_ph
  else:
    j = old_ph
    for sy in _characters_i:
      if sy == j[:len(sy)] and j[len(sy):-1] in _characters_s:
        j = j[:len(sy)] + " " + j[len(sy):-1] + " *" + j[-1]
        break
    new_ph = j
  return new_ph

# 英文发音字典
eng_char_dict = {'a': 'EE EI1',
                 'b': 'B I4',
                 'c': 'S I1',
                 'd': 'D I4',
                 'e': 'II I4',
                 'f': 'EE EI1 F U2',
                 'g': 'J I4',
                 'h': 'EE EI1 Q U1',
                 'i': 'AA AI4',
                 'j': 'J IE4',
                 'k': 'K IE4',
                 'l': 'EE EI1 L E5',
                 'm': 'EE EI1 M ENG5',
                 'n': 'EE EN1',
                 'o': 'OO OU1',
                 'p': 'P I1',
                 'q': 'Q OU1',
                 'r': 'AA AI1 EE ER5',
                 's': 'EE EI1 S IY1',
                 't': 'T I4',
                 'u': 'II IU1',
                 'v': 'UU UI1',
                 'w': 'D A2 B U5 L IU5',
                 'x': 'EE EI1 K IE5 S IY1',
                 'y': 'UU UAI1',
                 'z': 'Z E4'}


def has_poly_char(corpus, poly_dict):
  for char in corpus:
    if char in poly_dict.keys():
      return True
  return False


def is_chinese(uchar):
  """ 判断传入字符是否为中文 """
  assert len(uchar) == 1
  return '\u4e00' <= uchar <= '\u9fff'


def is_number(uchar):
  """判断一个unicode是否是数字"""
  if u'\u0030' <= uchar <= u'\u0039':
    return True
  else:
    return False


def is_alphabet(uchar):
  """判断一个unicode是否是英文字母"""
  if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
    return True
  else:
    return False


def split_tone(phone):
  phone = phone.replace("1", " *1").replace("2", " *2").replace("3", " *3")
  phone = phone.replace("4", " *4").replace("5", " *5")
  return phone


def load_poly_dict(poly_dict_path="/data1/liufeng/synthesis/"
                                  "frontend/data/simple_poly_dict"):
  poly_dict = dict()
  for line in read_lines(poly_dict_path):
    key = line.split(":")[0]
    value = line.split(":")[1].split(",")
    poly_dict[key] = value
  print("poly dict has {} items".format(len(poly_dict)))
  return poly_dict


if __name__ == '__main__':
  print(split_phone_format("shu4"))
