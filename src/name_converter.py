import pandas as pd
import pykakasi
import jaconv

class NameConverter:
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

    def convert(self, kanji, katakana=""):
        """转换姓名为罗马拼音"""
        # 1️⃣ 片假名优先
        if katakana.strip():
            words = katakana.split(" ")  # 按原始空格拆分
            romaji_words = [" ".join([item["hepburn"] for item in self.kks.convert(word)]).strip() for word in words]
            return " ".join(romaji_words).upper()  # 重新拼接，保持原空格

        # 2️⃣ 按空格分割姓氏和名字
        parts = kanji.split()  # 你自己提供的空格
        if len(parts) == 2:
            surname_kanji, given_name_kanji = parts
        else:
            surname_kanji, given_name_kanji = parts[0], ""

        # 3️⃣ 处理姓氏
        surname_romaji = self.surname_dict.get(surname_kanji, 
                          " ".join([item["hepburn"] for item in self.kks.convert(surname_kanji)]))

        # 4️⃣ 处理名字（如果有）
        if given_name_kanji:
            given_name_romaji = self.given_name_dict.get(
                given_name_kanji,
                " ".join([item["hepburn"] for item in self.kks.convert(given_name_kanji)])
            )
            return f"{surname_romaji} {given_name_romaji}".upper()

        return surname_romaji.upper()  # 只有姓氏时返回

