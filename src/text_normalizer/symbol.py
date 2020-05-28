# -*- coding: utf-8 -*-


class Symbol:
    """
    Symbol类
    """

    def __init__(self):
        self._symbol_to_symbol_dict = {
          "," : "，" ,
          "：" : "，" ,
          ":" : "，" ,
          "、" : "，" ,
          "…" : "。",
          "。。" : "。",
          "!" : "！",
          "?" : "？",
          "(" : "",
          ")" : "",
          "（" : "",
          "）" : "",
          "\\" : "",
          "{" : "",
          "}" : "",
          "[" : "",
          "]" : "",
          "|" : "",
          "\'" : "",
          "\"" : "",
          "‘" : "",
          "’" : "",
          "“" : "",
          "”" : "",
          "<" : "",
          ">" : "",
          "《" : "",
          "》" : "",
          "●" : "",
          "△" : "",
          "＊" : "",
        }

        self._symbol_to_pronunciation_dict = {
          "+" : "加",
          "-" : "减",
          "*" : "乘",
          "/" : "除",
          "#" : "井号",
          "@" : "欸特",
          "." : "点",
          "&" : "和",
          "α" : "阿尔法",
          "β" : "贝塔",
          "γ" : "伽玛",
          "θ" : "西塔",
          "μ" : "缪"
        }


    def normalize(self, text):
        text = self._symbol_to_pronunciation(text)
        text = self._symbol_to_symbol(text)
        text = self._symbol_post_normalize(text)
        return text

    def _symbol_to_symbol(self, text):
        for key in self._symbol_to_symbol_dict.keys():
            value = self._symbol_to_symbol_dict[key]
            while key in text:
              text = text.replace(key, value)
        return text

    def _symbol_to_pronunciation(self, text):
        '''符号转换为对应的读音
        支持的符号：+-*/#@&αβγθμ
        '''
        for key in self._symbol_to_pronunciation_dict.keys():
            value = self._symbol_to_pronunciation_dict[key]
            text = text.replace(key, value)
        return text

    def _is_chinese(self, char):
      if char >= '\u4e00' and char <= '\u9fa5':
        return True
      else:
        return False

    def _is_alphabet(self, char):
      if (char >= '\u0041' and char <= '\u005a') or (char >= '\u0061' and char <= '\u007a'):
        return True
      else:
        return False

    def _symbol_post_normalize(self, text):
        while "  " in text:
            text = text.replace("  ", " ")
        if self._is_chinese(text) or self._is_alphabet(text):
            text = text + "。"
        return text

if __name__ == '__main__':

    # 测试
    print(Symbol('这是最新手机小米α款').normalize())
    print(Symbol('啊我忘了额...').normalize())
