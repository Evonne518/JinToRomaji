import pandas as pd
import re
import pykakasi

class NameConverterV3:
    def __init__(self):
        # 載入 CSV 字典
        self.surname_dict = self.load_csv("data/surnames.csv")
        self.given_name_dict = self.load_csv("data/given_names.csv")

        # 初始化 pykakasi
        self.kks = pykakasi.kakasi()

    def load_csv(self, file_path):
        """從 CSV 文件載入字典"""
        try:
            df = pd.read_csv(file_path)
            return dict(zip(df["Kanji"], df["Romaji"]))
        except Exception as e:
            print(f"⚠️ 無法載入 {file_path}: {e}")
            return {}

    def _convert_by_kanji(self, kanji, inserted_space="N"):
        """根據漢字轉換成羅馬拼音與片假名"""
        parts = kanji.split()
        romaji_parts = []
        katakana_parts = []

        for part in parts:
            romaji = (
                self.surname_dict.get(part)
                or self.given_name_dict.get(part)
            )

            if romaji:
                # 命中字典 → 用字典的羅馬拼音
                romaji_parts.append(romaji.upper())
                # 用漢字（非羅馬字）生成假名，避免 Romaji→Kana 錯誤
                converted = self.kks.convert(part)
                katakana_parts.append("".join([x["kana"] for x in converted]))
            else:
                # 未命中字典 → pykakasi 全自動轉換
                converted = self.kks.convert(part)
                romaji_parts.append(
                    " ".join([x["hepburn"] for x in converted]).upper()
                )
                katakana_parts.append("".join([x["kana"] for x in converted]))

        # 合併後清理多餘空格
        katakana_result = re.sub(r"\s+", " ", " ".join(katakana_parts)).strip()
        romaji_result = re.sub(r"\s+", " ", " ".join(romaji_parts)).strip()

        return {
            "katakana": katakana_result,
            "romaji": romaji_result,
            "inserted_space": inserted_space,
        }

    def split_katakana_by_kanji_parts(self, kanji, katakana):
        """
        嘗試依據姓氏匹配在片假名中插入空格。
        若成功切開 → 回傳 [姓, 名, "Y"]
        若失敗 → 回傳 [原片假名, "", "N"]
        """
        if " " not in katakana and " " in kanji and len(kanji.split()) == 2:
            surname, given = kanji.split()

            # 將姓氏轉為羅馬拼音
            expected_surname_romaji = "".join(
                [x["hepburn"] for x in self.kks.convert(surname)]
            ).lower()

            # 嘗試從片假名前段比對姓氏發音
            for i in range(1, len(katakana)):
                first = katakana[:i]
                katakana_surname_romaji = "".join(
                    [x["hepburn"] for x in self.kks.convert(first)]
                ).lower()
                if katakana_surname_romaji == expected_surname_romaji:
                    return [first, katakana[i:], "Y"]

            # 若姓氏無法切出，再嘗試名字部分
            expected_given_romaji = "".join(
                [x["hepburn"] for x in self.kks.convert(given)]
            ).lower()
            for i in range(len(katakana) - 1, 0, -1):
                last = katakana[i:]
                katakana_given_romaji = "".join(
                    [x["hepburn"] for x in self.kks.convert(last)]
                ).lower()
                if katakana_given_romaji == expected_given_romaji:
                    return [katakana[:i], last, "Y"]

        return [katakana, "", "N"]

    def convert(self, kanji, katakana=""):
        """轉換姓名為羅馬拼音與片假名"""
        # 若全為英文
        if all(ord(c) < 128 for c in kanji if c.strip()):
            return {
                "katakana": "",
                "romaji": kanji.upper(),
                "inserted_space": "",
            }

        # ✅ 有提供片假名的情況
        if katakana.strip():
            # 嘗試拆分姓與名
            if " " not in katakana and " " in kanji:
                split_result = self.split_katakana_by_kanji_parts(
                    kanji, katakana
                )
                if split_result[2] == "Y":
                    words = split_result[:2]
                    romaji_words = [
                        " ".join(
                            [item["hepburn"] for item in self.kks.convert(word)]
                        ).strip()
                        for word in words
                    ]
                    return {
                        "katakana": " ".join(words),
                        "romaji": re.sub(
                            r"\s+", " ", " ".join(romaji_words).upper()
                        ).strip(),
                        "inserted_space": "Y",
                    }

            # 未拆成功 → 原樣轉換
            words = katakana.split()
            romaji_words = [
                " ".join(
                    [item["hepburn"] for item in self.kks.convert(word)]
                ).strip()
                for word in words
            ]
            return {
                "katakana": " ".join(words),
                "romaji": re.sub(
                    r"\s+", " ", " ".join(romaji_words).upper()
                ).strip(),
                "inserted_space": "N",
            }

        # ✅ 無 katakana → 用 kanji 轉換
        return self._convert_by_kanji(kanji, inserted_space="N")
