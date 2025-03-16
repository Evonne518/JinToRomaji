from fastapi import FastAPI
from pydantic import BaseModel
from src.name_converter import NameConverter

# 初始化 FastAPI
app = FastAPI()

# 初始化姓名转换器
converter = NameConverter()

class NameItem(BaseModel):
    kanji: str
    katakana: str = ""

class NameRequest(BaseModel):
    names: list[NameItem]

@app.post("/convert_names/")
def convert_names(request: NameRequest):
    """API 入口，接收 JSON 请求，返回转换后的罗马拼音"""
    result = {}
    for name in request.names:
        romaji = converter.convert(name.kanji, name.katakana)
        result[name.kanji] = romaji
    return {"translated_names": result}
