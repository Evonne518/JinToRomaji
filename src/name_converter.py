import pandas as pd
import pykakasi
import fugashi  # 加入 fugashi

class NameConverter:
    def __init__(self, use_fugashi=True):
        # 载入 CSV 词典
        self.surname_dict = self.load_csv("data/surnames.csv")
        self.given_name_dict = self.load_csv("data/given_names.csv")

        # 初始化 pykakasi
        self.kks = pykakasi.kakasi()

        # 初始化 fugashi（選用）
        self.use_fugashi = use_fugashi
        self.tagger = fugashi.Tagger() if use_fugashi else None

    def load_csv(self, file_path):
        """从 CSV 文件加载字典"""
        try:
            df = pd.read_csv(file_path)
            return dict(zip(df["Kanji"], df["Romaji"]))
        except Exception as e:
            print(f"无法加载 {file_path}: {e}")
            return {}

    def katakana_to_romaji(self, katakana):
        """处理片假名转换成罗马拼音"""
        if self.use_fugashi:
            # 用 fugashi 分词
            words = [word.surface for word in self.tagger(katakana)]
        else:
            # 用空格拆分
            words = katakana.split()

        romaji_words = [
            " ".join([item["hepburn"] for item in self.kks.convert(word)]).strip()
            for word in words
        ]
        return " ".join(romaji_words).upper()

    def convert(self, kanji, katakana=""):
        """转换姓名为罗马拼音"""
        # 1️⃣ 如果有片假名，优先处理
        if katakana.strip():
            return self.katakana_to_romaji(katakana)

        # 2️⃣ 按空格分割姓氏和名字（Kanji）
        parts = kanji.split()
        if len(parts) == 2:
            surname_kanji, given_name_kanji = parts
        else:
            surname_kanji, given_name_kanji = parts[0], ""

        # 3️⃣ 处理姓氏
        surname_romaji = self.surname_dict.get(
            surname_kanji,
            " ".join([item["hepburn"] for item in self.kks.convert(surname_kanji)])
        )

        # 4️⃣ 处理名字
        if given_name_kanji:
            given_name_romaji = self.given_name_dict.get(
                given_name_kanji,
                " ".join([item["hepburn"] for item in self.kks.convert(given_name_kanji)])
            )
            return f"{surname_romaji} {given_name_romaji}".upper()

        return surname_romaji.upper()
