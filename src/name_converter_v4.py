import os
import pandas as pd
import re
import pykakasi
import jaconv  # 將羅馬拼音轉片假名


class NameConverterV4:
    def __init__(self):
        # 嘗試載入 full_names.csv，沒有也不會報錯
        self.full_name_dict = self.load_csv("data/full_names.csv") if os.path.exists("data/full_names.csv") else {}
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
        """
        合併多餘空格，但保留單個空格（保持姓+名間隔）
        """
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    def _convert_kanji_segment(self, segment):
        """
        漢字整段轉拼音，保持姓 + 名空格，全大寫
        """
        # 嘗試空格拆段，沒有空格整段處理
        parts = segment.split() if " " in segment else [segment]
        romaji_parts = []
        katakana_parts = []

        for part in parts:
            # 字典匹配優先
            if part in self.full_name_dict:
                romaji = self.full_name_dict[part].upper()
                katakana = self._romaji_to_katakana(romaji)
            elif part in self.surname_dict:
                romaji = self.surname_dict[part].upper()
                katakana = self._romaji_to_katakana(romaji)
            elif part in self.given_name_dict:
                romaji = self.given_name_dict[part].upper()
                katakana = self._romaji_to_katakana(romaji)
            else:
                # 字典未命中 → pykakasi 整段轉換
                converted = self.kks.convert(part)
                romaji = "".join([x["hepburn"].upper() for x in converted])
                katakana = "".join([x["kana"] for x in converted])

            romaji_parts.append(romaji)
            katakana_parts.append(katakana)

        romaji_result = " ".join(romaji_parts)
        katakana_result = " ".join(katakana_parts)
        romaji_result = self._join_romaji_smooth(romaji_result)
        katakana_result = self._join_romaji_smooth(katakana_result)
        return romaji_result, katakana_result

    def convert(self, kanji, katakana=""):
        # 完全英文直接返回
        if all(ord(c) < 128 for c in kanji if c.strip()):
            return {"katakana": "", "romaji": kanji.upper(), "inserted_space": ""}

        # 清理文字
        kanji = re.sub(r'[\uFE00-\uFE0F\U000E0100-\U000E01EF\u200B-\u200D\u2060]', '', kanji)
        katakana = re.sub(r'[\uFE00-\uFE0F\U000E0100-\U000E01EF\u200B-\u200D\u2060]', '', katakana)

        # 如果提供片假名
        if katakana.strip():
            words = katakana.split(" ")
            romaji_words = []
            for word in words:
                converted = self.kks.convert(word)
                romaji_words.append("".join([x["hepburn"].upper() for x in converted]))
            romaji_result = self._join_romaji_smooth(" ".join(romaji_words))
            return {
                "katakana": " ".join(words),
                "romaji": romaji_result,
                "inserted_space": ""
            }

        # 漢字轉拼音
        romaji_result, katakana_result = self._convert_kanji_segment(kanji)
        return {
            "katakana": katakana_result,
            "romaji": romaji_result,
            "inserted_space": ""
        }
