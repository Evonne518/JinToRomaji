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
        合併不必要的空格，例如:
        DAI RA → DAIRA,  KAN TA → KANTA,  I CHI ROU → ICHIROU
        """
        # 去掉單字中間的空格，但保留姓與名間的空格
        text = re.sub(r"\b([A-Z]{1,3})\s+([A-Z]{1,3})\b", r"\1\2", text)
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()

    def _convert_part(self, text):
        """單段轉換"""
        converted = self.kks.convert(text)
        romaji = " ".join([x["hepburn"] for x in converted]).upper()
        katakana = "".join([x["kana"] for x in converted])
        return romaji, katakana

    def _convert_by_kanji(self, kanji, inserted_space="N"):
        parts = kanji.split()
        romaji_parts, katakana_parts = [], []

        for part in parts:
            romaji = self.surname_dict.get(part) or self.given_name_dict.get(part)
            if romaji:
                romaji_parts.append(romaji.upper())
                _, kana = self._convert_part(part)
                katakana_parts.append(kana)
            else:
                r, k = self._convert_part(part)
                romaji_parts.append(r)
                katakana_parts.append(k)

        romaji_result = self._join_romaji_smooth(" ".join(romaji_parts))
        katakana_result = re.sub(r"\s+", " ", " ".join(katakana_parts)).strip()
        return {"katakana": katakana_result, "romaji": romaji_result, "inserted_space": inserted_space}

    def split_katakana_by_kanji_parts(self, kanji, katakana):
        if " " not in katakana and " " in kanji and len(kanji.split()) == 2:
            surname, given = kanji.split()
            expected_surname_romaji = "".join([x["hepburn"] for x in self.kks.convert(surname)]).lower()

            for i in range(1, len(katakana)):
                first = katakana[:i]
                katakana_surname_romaji = "".join([x["hepburn"] for x in self.kks.convert(first)]).lower()
                if katakana_surname_romaji == expected_surname_romaji:
                    return [first, katakana[i:], "Y"]
        return [katakana, "", "N"]

    def convert(self, kanji, katakana=""):
        if all(ord(c) < 128 for c in kanji if c.strip()):
            return {"katakana": "", "romaji": kanji.upper(), "inserted_space": ""}

        if katakana.strip():
            if " " not in katakana and " " in kanji:
                split_result = self.split_katakana_by_kanji_parts(kanji, katakana)
                if split_result[2] == "Y":
                    words = split_result[:2]
                    romaji_words = []
                    for word in words:
                        r, _ = self._convert_part(word)
                        romaji_words.append(self._join_romaji_smooth(r))
                    return {
                        "katakana": " ".join(words),
                        "romaji": " ".join(romaji_words).upper(),
                        "inserted_space": "Y"
                    }

            # 沒拆成功
            romaji, _ = self._convert_part(katakana)
            return {"katakana": katakana, "romaji": self._join_romaji_smooth(romaji), "inserted_space": "N"}

        # 無 katakana
        return self._convert_by_kanji(kanji, inserted_space="N")
