import pandas as pd
import pykakasi

class NameConverterV3:
    def __init__(self):
        # 載入 CSV 詞典
        self.surname_dict = self.load_csv("data/surnames.csv")
        self.given_name_dict = self.load_csv("data/given_names.csv")
        # 初始化 pykakasi
        self.kks = pykakasi.kakasi()

    def load_csv(self, file_path):
        try:
            df = pd.read_csv(file_path)
            return dict(zip(df["Kanji"], df["Romaji"]))
        except Exception as e:
            print(f"無法載入 {file_path}: {e}")
            return {}

    def kanji_to_katakana(self, text: str) -> str:
        """Kanji → 平假名 → 片假名"""
        hira = "".join([item["hira"] for item in self.kks.convert(text)])
        return "".join([chr(ord(c) + 0x60) if "ぁ" <= c <= "ん" else c for c in hira])

    def romaji_to_katakana(self, romaji: str) -> str:
        """Romaji → Katakana"""
        hira = "".join([item["hira"] for item in self.kks.convert(romaji)])
        return "".join([chr(ord(c) + 0x60) if "ぁ" <= c <= "ん" else c for c in hira])

    def split_katakana_by_kanji_parts(self, kanji, katakana):
        """沿用 V2 拆分邏輯"""
        if " " not in katakana and " " in kanji and len(kanji.split()) == 2:
            surname, given = kanji.split()
            expected_surname_romaji = "".join([x["hepburn"] for x in self.kks.convert(surname)]).lower()
            for i in range(1, len(katakana)):
                first = katakana[:i]
                katakana_surname_romaji = "".join([x["hepburn"] for x in self.kks.convert(first)]).lower()
                if katakana_surname_romaji == expected_surname_romaji:
                    return [first, katakana[i:], "Y"]
            expected_given_romaji = self.kks.convert(given)[0]["hepburn"].lower()
            for i in range(len(katakana)-1, 0, -1):
                last = katakana[i:]
                katakana_given_romaji = "".join([x["hepburn"] for x in self.kks.convert(last)]).lower()
                if katakana_given_romaji == expected_given_romaji:
                    return [katakana[:i], last, "Y"]
        return [katakana, "", "N"]

    def _convert_by_kanji(self, kanji, katakana="", inserted_space=""):
        """V2 轉換核心"""
        parts = kanji.split()
        if len(parts) == 2:
            surname_kanji, given_name_kanji = parts
            surname_romaji = self.surname_dict.get(
                surname_kanji,
                " ".join([item["hepburn"] for item in self.kks.convert(surname_kanji)])
            )
            given_name_romaji = self.given_name_dict.get(
                given_name_kanji,
                " ".join([item["hepburn"] for item in self.kks.convert(given_name_kanji)])
            )
            romaji = f"{surname_romaji} {given_name_romaji}"
        else:
            romaji = " ".join([item["hepburn"] for item in self.kks.convert(kanji)])

        return {
            "katakana": katakana,
            "romaji": " ".join(romaji.split()).upper(),
            "inserted_space": inserted_space
        }

    def convert(self, kanji, katakana=""):
        # 全英文直接返回
        if all(ord(c) < 128 for c in kanji if c.strip()):
            return {"katakana": "", "romaji": kanji.upper(), "inserted_space": ""}

        # 有 katakana → 沿用 V2 邏輯
        if katakana.strip():
            if " " not in katakana and " " in kanji:
                split_result = self.split_katakana_by_kanji_parts(kanji, katakana)
                if split_result[2] == "Y":
                    words = split_result[:2]
                    romaji_words = [" ".join([item["hepburn"] for item in self.kks.convert(w)]).strip() for w in words]
                    return {"katakana": " ".join(words), "romaji": " ".join(romaji_words).upper(), "inserted_space": "Y"}
                else:
                    return self._convert_by_kanji(kanji, katakana=katakana, inserted_space="N")
            else:
                words = katakana.split(" ")
                romaji_words = [" ".join([item["hepburn"] for item in self.kks.convert(w)]).strip() for w in words]
                return {"katakana": " ".join(words), "romaji": " ".join(romaji_words).upper(), "inserted_space": ""}

        # 無 katakana → 分拆 Kanji
        parts = kanji.split() if " " in kanji else [kanji]
        surname_kanji = parts[0]
        given_name_kanji = parts[1] if len(parts) > 1 else ""

        romaji_words = []
        katakana_words = []

        # 處理姓氏
        if surname_kanji in self.surname_dict:
            surname_romaji = self.surname_dict[surname_kanji]
            surname_kata = self.romaji_to_katakana(surname_romaji)
        else:
            surname_kata = self.kanji_to_katakana(surname_kanji)
            surname_romaji = " ".join([item["hepburn"] for item in self.kks.convert(surname_kata)])
        romaji_words.append(surname_romaji)
        katakana_words.append(surname_kata)

        # 處理名字
        if given_name_kanji:
            if given_name_kanji in self.given_name_dict:
                given_romaji = self.given_name_dict[given_name_kanji]
                given_kata = self.romaji_to_katakana(given_romaji)
            else:
                given_kata = self.kanji_to_katakana(given_name_kanji)
                given_romaji = " ".join([item["hepburn"] for item in self.kks.convert(given_kata)])
            romaji_words.append(given_romaji)
            katakana_words.append(given_kata)

        inserted_space = "Y" if len(romaji_words) == 2 else "N"

        return {
            "katakana": " ".join(katakana_words),
            "romaji": " ".join(romaji_words).upper(),
            "inserted_space": inserted_space
        }
