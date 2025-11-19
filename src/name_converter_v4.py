import pandas as pd
import re
import pykakasi
import jaconv  # 將羅馬拼音轉片假名


class NameConverterV4:
    def __init__(self):
        # 載入各種字典
        self.full_name_dict = self.load_csv("data/full_names.csv")
        self.surname_dict = self.load_csv("data/surnames.csv")
        self.given_name_dict = self.load_csv("data/given_names.csv")
        self.kks = pykakasi.kakasi()

    def load_csv(self, file_path):
        """讀取 CSV 轉成字典"""
        try:
            df = pd.read_csv(file_path)
            return dict(zip(df["Kanji"], df["Romaji"]))
        except Exception as e:
            print(f"⚠️ 無法載入 {file_path}: {e}")
            return {}

    def _romaji_to_katakana(self, romaji: str) -> str:
        """羅馬拼音轉片假名"""
        return jaconv.alphabet2kata(romaji.lower())

    def _join_romaji_smooth(self, text):
        """合併多餘空格，但保留英文原本空格"""
        def merge_romaji(match):
            return match.group(0).replace(" ", "")
        
        text = re.sub(r'\b([A-Z]{1,3})\s+([A-Z]{1,3})\b', merge_romaji, text)
        text = re.sub(r'\s{2,}', " ", text)
        return text.strip()

    def _convert_kanji_segment(self, segment):
        """轉換單一漢字段"""
        if segment in self.full_name_dict:
            romaji = self.full_name_dict[segment].upper()
            katakana = self._romaji_to_katakana(romaji)
            return romaji, katakana

        # 試姓氏 + 名字字典匹配
        if segment in self.surname_dict:
            romaji = self.surname_dict[segment].upper()
            katakana = self._romaji_to_katakana(romaji)
            return romaji, katakana
        if segment in self.given_name_dict:
            romaji = self.given_name_dict[segment].upper()
            katakana = self._romaji_to_katakana(romaji)
            return romaji, katakana

        # 字典未命中，用 pykakasi 整段轉換
        converted = self.kks.convert(segment)
        romaji = " ".join([x["hepburn"] for x in converted]).upper()
        katakana = "".join([x["kana"] for x in converted])
        return romaji, katakana

    def convert(self, kanji, katakana=""):
        # 完全英文直接返回
        if all(ord(c) < 128 for c in kanji if c.strip()):
            return {"katakana": "", "romaji": kanji.upper(), "inserted_space": ""}

        # 清理文字
        kanji = re.sub(r'[\uFE00-\uFE0F\U000E0100-\U000E01EF\u200B-\u200D\u2060]', '', kanji)
        katakana = re.sub(r'[\uFE00-\uFE0F\U000E0100-\U000E01EF\u200B-\u200D\u2060]', '', katakana)

        # 如果提供片假名，嘗試拆分與拼音匹配
        if katakana.strip():
            # 拆空格
            words = katakana.split(" ")
            romaji_words = []
            for word in words:
                converted = self.kks.convert(word)
                romaji_words.append("".join([x["hepburn"] for x in converted]).upper())
            romaji_result = self._join_romaji_smooth(" ".join(romaji_words))
            return {
                "katakana": " ".join(words),
                "romaji": romaji_result,
                "inserted_space": ""
            }

        # 無片假名，用漢字轉
        # 嘗試完整姓名字典匹配
        romaji, kata = self._convert_kanji_segment(kanji)
        return {
            "katakana": kata,
            "romaji": romaji,
            "inserted_space": ""
        }
