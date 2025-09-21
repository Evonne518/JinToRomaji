import pandas as pd
import pykakasi

class NameConverterV3:
    def __init__(self):
        # 载入 CSV 词典
        self.surname_dict = self.load_csv("data/surnames.csv")
        self.given_name_dict = self.load_csv("data/given_names.csv")

        # 初始化 pykakasi
        self.kks = pykakasi.kakasi()

    def load_csv(self, file_path):
        """从 CSV 文件加载字典"""
        try:
            df = pd.read_csv(file_path)
            return dict(zip(df["Kanji"], df["Romaji"]))
        except Exception as e:
            print(f"無法載入 {file_path}: {e}")
            return {}

    def _convert_by_kanji(self, kanji, katakana="", inserted_space=""):
        """根據 kanji 轉換為 Romaji，同時生成 Katakana 並保持空格與 Romaji 一致"""
        parts = kanji.split()  # 按空格拆漢字段
    
        # 如果 katakana 为空或連寫，按 kanji 拆段生成 Katakana
        if not katakana.strip() or (" " not in katakana and len(parts) > 1):
            katakana_parts = []
            for part in parts:
                converted = self.kks.convert(part)
                katakana_part = "".join([x["kana"] for x in converted])
                katakana_parts.append(katakana_part)
            katakana = " ".join(katakana_parts)  # 用空格分隔，每段對應 Romaji
    
        # 生成 Romaji
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
            romaji_parts = []
            for part in parts:
                if part.strip():
                    romaji_part = " ".join([item["hepburn"] for item in self.kks.convert(part)])
                    romaji_parts.append(romaji_part)
            romaji = " ".join(romaji_parts)
    
        return {
            "katakana": katakana,
            "romaji": romaji.upper(),
            "inserted_space": inserted_space
        }

    
    def split_katakana_by_kanji_parts(self, kanji, katakana):
        """
        嘗試將 katakana 根據 kanji 的姓氏進行切分。
        若姓氏的羅馬拼音能對應 katakana 的前段，就切開。
        若姓氏無法切開，再嘗試名字進行匹配。
        """
        if " " not in katakana and " " in kanji and len(kanji.split()) == 2:
            surname, given = kanji.split()

            # 將姓氏轉為羅馬拼音
            expected_surname_romaji = "".join([x["hepburn"] for x in self.kks.convert(surname)]).lower()


            # 嘗試在 katakana 裡找到姓氏的羅馬拼音
            for i in range(1, len(katakana)):
                first = katakana[:i]
                katakana_surname_romaji = "".join([x["hepburn"] for x in self.kks.convert(first)]).lower()
                if katakana_surname_romaji == expected_surname_romaji:
                    return [first, katakana[i:], "Y"]  # 切開姓氏部分並標註插入空格成功

            # 若姓氏無法切開，再嘗試從後面往前檢查名字部分
            expected_given_romaji = self.kks.convert(given)[0]["hepburn"].lower()
            for i in range(len(katakana) - 1, 0, -1):  # 從後面往前檢查
                last = katakana[i:]
                katakana_given_romaji = "".join([x["hepburn"] for x in self.kks.convert(last)]).lower()
                if katakana_given_romaji == expected_given_romaji:
                    return [katakana[:i], last, "Y"]  # 切開名字部分並標註插入空格成功

        return [katakana, "", "N"]  # 無法切開就返回原始 katakana 並標註無插入空格

    def convert(self, kanji, katakana=""):
        """转换姓名为罗马拼音"""
        # 如果 kanji 是全英文
        if all(ord(c) < 128 for c in kanji if c.strip()):
            return {
                "katakana": "",
                "romaji": kanji.upper(),
                "inserted_space": ""
            }
    
        if katakana.strip():
            if " " not in katakana and " " in kanji:
                split_result = self.split_katakana_by_kanji_parts(kanji, katakana)
                if split_result[2] == "Y":
                    words = split_result[:2]
                    romaji_words = [
                        " ".join([item["hepburn"] for item in self.kks.convert(word)]).strip()
                        for word in words
                    ]
                    return {
                        "katakana": " ".join(words),
                        "romaji": " ".join(romaji_words).upper(),
                        "inserted_space": "Y"
                    }
                else:
                    return self._convert_by_kanji(kanji, katakana=katakana, inserted_space="N")
            else:
                words = katakana.split(" ")
                romaji_words = [
                    " ".join([item["hepburn"] for item in self.kks.convert(word)]).strip()
                    for word in words
                ]
                return {
                    "katakana": " ".join(words),
                    "romaji": " ".join(romaji_words).upper(),
                    "inserted_space": ""
                }
    
        # katakana 是空 → 直接用 kanji 转换，同时生成 katakana
        return self._convert_by_kanji(kanji, inserted_space="N")
