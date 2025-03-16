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
            return " ".join([item["hepburn"] for item in self.kks.convert(katakana)]).upper()
        # 2️⃣ 按姓氏长度从长到短排序
        sorted_surnames = sorted(self.surname_dict.keys(), key=len, reverse=True)
    
        # 3️⃣ 先查姓氏
        for surname in self.surname_dict:
            if kanji.startswith(surname):
                surname_romaji = self.surname_dict[surname]
                given_name_kanji = kanji[len(surname):].strip()  # 去掉多余的空格

                # 处理名字
                if given_name_kanji:
                    if given_name_kanji in self.given_name_dict:
                        given_name_romaji = self.given_name_dict[given_name_kanji]
                    else:
                        given_name_romaji = " ".join([item["hepburn"] for item in self.kks.convert(given_name_kanji)])
                    return f"{surname_romaji} {given_name_romaji}".upper()  # 姓名之间加空格
                else:
                    return surname_romaji.upper()  # 只有姓氏，直接返回

        # 3️⃣ 没有匹配到姓氏，直接转换（不额外加空格）
        return " ".join([item["hepburn"] for item in self.kks.convert(jaconv.hira2kata(kanji))]).upper()
