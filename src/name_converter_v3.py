import pandas as pd
import pykakasi

class NameConverterV3:
    def __init__(self):
        # 載入 CSV 詞典
        self.surname_dict = self.load_csv("data/surnames.csv")
        self.given_name_dict = self.load_csv("data/given_names.csv")
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

    # 沿用 V2 的拆分邏輯
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
            for i in range(len(katakana)-1, 0, -1):
                last = katakana[i:]
                katakana_given_romaji = "".join([x["hepburn"] for x in self.kks.convert(last)]).lower()
                if katakana_given_romaji == expected_given_romaji:
                    return [katakana[:i], last, "Y"]
        return [katakana, "", "N"]

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
            "romaji": " ".join(romaji.split()).upper(),
            "inserted_space": inserted_space
        }

    def convert(self, kanji, katakana=""):
        # 全英文
        if all(ord(c) < 128 for c in kanji if c.strip()):
            return {"katakana": "", "romaji": kanji.upper(), "inserted_space": ""}

        # 有 katakana → 沿用 V2
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

        # 無 katakana → 推測 Katakana
        katakana_guess = self.kanji_to_katakana(kanji)
        split_result = self.split_katakana_by_kanji_parts(kanji, katakana_guess)
        if split_result[2] == "Y":
            words = split_result[:2]
            romaji_words = [" ".join([item["hepburn"] for item in self.kks.convert(w)]).strip() for w in words]
            return {"katakana": " ".join(words), "romaji": " ".join(romaji_words).upper(), "inserted_space": "N"}
        else:
            return self._convert_by_kanji(kanji, katakana=katakana_guess, inserted_space="N")
