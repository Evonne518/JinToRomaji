import pandas as pd
import re
import pykakasi

class NameConverterV3:
    def __init__(self):
        self.surname_dict = self.load_csv("data/surnames.csv")
        self.given_name_dict = self.load_csv("data/given_names.csv")
        self.kks = pykakasi.kakasi()

    def load_csv(self, file_path):
        try:
            df = pd.read_csv(file_path)
            return dict(zip(df["Kanji"], df["Romaji"]))
        except Exception as e:
            print(f"⚠️ 無法載入 {file_path}: {e}")
            return {}

    def _join_romaji_smooth(self, text):
        """
        合併多餘空格：DAI RA → DAIRA, KAN TA → KANTA, I CHI ROU → ICHIROU
        但保留姓與名之間的空格
        """
        # 將單字中間的小空格合併
        text = re.sub(r"\b([A-Z]{1,3})\s+([A-Z]{1,3})\b", r"\1\2", text)
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()

    def _convert_by_kanji(self, kanji, katakana="", inserted_space=""):
        """
        原始轉換邏輯：
        - 字典命中 → Romaji 用字典，Katakana 根據 Romaji 生成
        - 字典未命中 → pykakasi 轉整段漢字
        """
        parts = kanji.split()
        romaji_parts = []
        katakana_parts = []

        for part in parts:
            surname_romaji = self.surname_dict.get(part)
            given_romaji = self.given_name_dict.get(part)
            if surname_romaji or given_romaji:
                romaji = surname_romaji or given_romaji
                romaji_parts.append(romaji.upper())
                katakana_part = "".join([x["kana"] for x in self.kks.convert(romaji.lower())])
                katakana_parts.append(katakana_part)
            else:
                converted = self.kks.convert(part)
                romaji_parts.append(" ".join([x["hepburn"] for x in converted]).upper())
                katakana_parts.append("".join([x["kana"] for x in converted]))

        # 先拼接，再套用空格修正
        romaji_result = self._join_romaji_smooth(" ".join(romaji_parts))
        katakana_result = " ".join(katakana_parts).strip()

        return {
            "katakana": katakana_result,
            "romaji": romaji_result,
            "inserted_space": inserted_space
        }

    def split_katakana_by_kanji_parts(self, kanji, katakana):
        if " " not in katakana and " " in kanji and len(kanji.split()) == 2:
            surname, given = kanji.split()
            expected_surname_romaji = "".join([x["hepburn"] for x in self.kks.convert(surname)]).lower()
            for i in range(1, len(katakana)):
                first = katakana[:i]
                katakana_surname_romaji = "".join([x["hepburn"] for x in self.kks.convert(first)]).lower()
                if katakana_surname_romaji == expected_surname_romaji:
                    return [first, katakana[i:], "Y"]

            expected_given_romaji = self.kks.convert(given)[0]["hepburn"].lower()
            for i in range(len(katakana) - 1, 0, -1):
                last = katakana[i:]
                katakana_given_romaji = "".join([x["hepburn"] for x in self.kks.convert(last)]).lower()
                if katakana_given_romaji == expected_given_romaji:
                    return [katakana[:i], last, "Y"]

        return [katakana, "", "N"]

    def convert(self, kanji, katakana=""):
        if all(ord(c) < 128 for c in kanji if c.strip()):
            return {"katakana": "", "romaji": kanji.upper(), "inserted_space": ""}

        if katakana.strip():
            if " " not in katakana and " " in kanji:
                split_result = self.split_katakana_by_kanji_parts(kanji, katakana)
                if split_result[2] == "Y":
                    words = split_result[:2]
                    romaji_words = [
                        " ".join([x["hepburn"] for x in self.kks.convert(word)]).strip()
                        for word in words
                    ]
                    romaji_result = self._join_romaji_smooth(" ".join(romaji_words))
                    return {
                        "katakana": " ".join(words),
                        "romaji": romaji_result.upper(),
                        "inserted_space": "Y"
                    }
                else:
                    return self._convert_by_kanji(kanji, katakana=katakana, inserted_space="N")
            else:
                words = katakana.split(" ")
                romaji_words = [
                    " ".join([x["hepburn"] for x in self.kks.convert(word)]).strip()
                    for word in words
                ]
                romaji_result = self._join_romaji_smooth(" ".join(romaji_words))
                return {
                    "katakana": " ".join(words),
                    "romaji": romaji_result.upper(),
                    "inserted_space": ""
                }

        return self._convert_by_kanji(kanji, inserted_space="N")
