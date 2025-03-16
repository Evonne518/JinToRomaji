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
            return self.kks.convert(katakana)[0]["hepburn"].upper()

        # 2️⃣ 先查姓氏
        for surname in self.surname_dict:
            if kanji.startswith(surname):
                surname_romaji = self.surname_dict[surname]
                given_name_kanji = kanji[len(surname):]
                
                # 尝试匹配名字
                given_name_romaji = self.given_name_dict.get(given_name_kanji, self.kks.convert(given_name_kanji)[0]["hepburn"])
                
                return f"{surname_romaji}{given_name_romaji}".upper()

        # 3️⃣ 没有匹配到姓氏，直接转换
        return self.kks.convert(jaconv.hira2kata(kanji))[0]["hepburn"].upper()
