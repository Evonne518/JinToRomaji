import pandas as pd
import pykakasi

class NameConverterV2:
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
            print(f"无法加载 {file_path}: {e}")
            return {}

    def split_katakana_by_kanji_parts(self, kanji, katakana):
        """
        嘗試將 katakana 根據 kanji 的姓氏進行切分。
        若姓氏的羅馬拼音能對應 katakana 的前段，就切開。
        若姓氏無法切開，再嘗試名字進行匹配。
        """
        if " " not in katakana and " " in kanji:
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
        if katakana.strip():
            # 如果 katakana 无空格，尝试根据 kanji 拆分
            if " " not in katakana and " " in kanji:
                split_result = self.split_katakana_by_kanji_parts(kanji, katakana)
                if split_result[2] == "Y":
                    words = split_result[:2]
                else:
                    words = katakana.split(" ")
            else:
                words = katakana.split(" ")

            romaji_words = [" ".join([item["hepburn"] for item in self.kks.convert(word)]).strip() for word in words]
            return {
                "katakana": " ".join(words),
                "romaji": " ".join(romaji_words).upper(),
                "inserted_space": split_result[2] if " " not in katakana and " " in kanji else ""  # 返回是否插入了空格
            }

        # 按空格分割姓氏和名字
        parts = kanji.split()
        if len(parts) == 2:
            surname_kanji, given_name_kanji = parts
        else:
            surname_kanji, given_name_kanji = parts[0], ""

        surname_romaji = self.surname_dict.get(surname_kanji,
                        " ".join([item["hepburn"] for item in self.kks.convert(surname_kanji)]))

        if given_name_kanji:
            given_name_romaji = self.given_name_dict.get(
                given_name_kanji,
                " ".join([item["hepburn"] for item in self.kks.convert(given_name_kanji)])
            )
            return {
                "katakana": "",
                "romaji": f"{surname_romaji} {given_name_romaji}".upper(),
                "inserted_space": ""  # 没有插入空格
            }

        return {
            "katakana": "",
            "romaji": surname_romaji.upper(),
            "inserted_space": ""  # 没有插入空格
        }
