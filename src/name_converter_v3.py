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
        """Romaji → Katakana (簡單版透過 pykakasi)"""
        hira = "".join([item["hira"] for item in self.kks.convert(romaji)])
        return "".join([chr(ord(c) + 0x60) if "ぁ" <= c <= "ん" else c for c in hira])

    def _convert_by_kanji(self, kanji, katakana="", inserted_space=""):
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
            "romaji": romaji.upper(),
            "inserted_space": inserted_space
        }

    def convert(self, kanji, katakana=""):
        # 全英文
        if all(ord(c) < 128 for c in kanji if c.strip()):
            return {"katakana": "", "romaji": kanji.upper(), "inserted_space": ""}

        # 有 katakana → 跟 v2 一樣走
        if katakana.strip():
            return self._convert_by_kanji(kanji, katakana, inserted_space="")

        # 無 katakana → 新邏輯
        katakana_guess = self.kanji_to_katakana(kanji)

        # 先查 CSV 詞典
        if kanji in self.surname_dict:
            romaji = self.surname_dict[kanji]
            katakana_from_romaji = self.romaji_to_katakana(romaji)
            return {
                "katakana": katakana_from_romaji,
                "romaji": romaji.upper(),
                "inserted_space": "N"
            }

        # CSV 無命中 → 用 katakana_guess 翻譯
        romaji = " ".join([item["hepburn"] for item in self.kks.convert(katakana_guess)])
        return {"katakana": katakana_guess, "romaji": romaji.upper(), "inserted_space": "N"}
