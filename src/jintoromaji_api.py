from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.name_converter import NameConverter  # v1 转换器
from src.name_converter_v2 import NameConverterV2  # v2 转换器

# 初始化 FastAPI
app = FastAPI()

@app.get("/")
def home():
    return {"message": "JinToRomaji API is running!"}

# 初始化姓名转换器
converter_v1 = NameConverter()  # v1 转换器
converter_v2 = NameConverterV2()  # v2 转换器

class NameItem(BaseModel):
    kanji: str
    katakana: str = ""

class NameRequest(BaseModel):
    names: list[NameItem]

@app.post("/convert_names/v1/")
def convert_names_v1(request: NameRequest):
    """API 入口，接收 JSON 请求，返回转换后的罗马拼音 (v1 版本)"""
    result = {}
    for name in request.names:
        romaji = converter_v1.convert(name.kanji, name.katakana)
        result[name.kanji] = romaji
    return {"translated_names": result}

@app.post("/convert_names/v2/")
def convert_names_v2(request: NameRequest):
    """API 入口，接收 JSON 请求，返回转换后的罗马拼音 (v2 版本)"""
    result = {}
    for name in request.names:
        romaji = converter_v2.convert(name.kanji, name.katakana)
        result[name.kanji] = romaji
    return {"translated_names": result}

@app.post("/convert_names/")
def convert_names(request: NameRequest, version: str = "v1"):
    """API 入口，接收 JSON 请求，返回转换后的罗马拼音，支持 v1 或 v2 版本"""
    if version == "v1":
        result = {}
        for name in request.names:
            romaji = converter_v1.convert(name.kanji, name.katakana)
            result[name.kanji] = romaji
        return {"translated_names": result}
    elif version == "v2":
        result = {}
        for name in request.names:
            romaji = converter_v2.convert(name.kanji, name.katakana)
            result[name.kanji] = romaji
        return {"translated_names": result}
    else:
        raise HTTPException(status_code=400, detail="Invalid version. Please use 'v1' or 'v2'.")
