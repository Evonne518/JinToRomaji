from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
from src.name_converter import NameConverter
from src.name_converter_v2 import NameConverterV2
from src.name_converter_v3 import NameConverterV3 
from src.name_converter_v4 import NameConverterV4  # ⬅️ 新增

app = FastAPI()

@app.get("/")
def home():
    return {"message": "JinToRomaji API is running!"}

converter_v1 = NameConverter()
converter_v2 = NameConverterV2()
converter_v3 = NameConverterV3() 
converter_v4 = NameConverterV4()  # ⬅️ 新增

class NameItem(BaseModel):
    kanji: str
    katakana: str = ""

class NameRequest(BaseModel):
    names: list[NameItem]

def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'[\uFE00-\uFE0F\U000E0100-\U000E01EF\u200B-\u200D\u2060]', '', text)

def process_request(request: NameRequest, version: str):
    result = {}
    for name in request.names:
        kanji_clean = clean_text(name.kanji)
        katakana_clean = clean_text(name.katakana)

        if version == "v1":
            romaji = converter_v1.convert(kanji_clean, katakana_clean)
        elif version == "v2":
            romaji = converter_v2.convert(kanji_clean, katakana_clean)
        elif version == "v3":  
            romaji = converter_v3.convert(kanji_clean, katakana_clean)
        elif version == "v4":  # ⬅️ 新增
            romaji = converter_v4.convert(kanji_clean, katakana_clean)
        else:
            raise HTTPException(status_code=400, detail="Invalid version. Please use 'v1', 'v2' or 'v3'.")

        result[name.kanji] = romaji
    return {"translated_names": result}

@app.post("/convert_names/v1/")
def convert_names_v1(request: NameRequest):
    return process_request(request, "v1")

@app.post("/convert_names/v2/")
def convert_names_v2(request: NameRequest):
    return process_request(request, "v2")

@app.post("/convert_names/v3/") 
def convert_names_v3(request: NameRequest):
    return process_request(request, "v3")

@app.post("/convert_names/v4/")  # ⬅️ 新增
def convert_names_v4(request: NameRequest):
    return process_request(request, "v4")

@app.post("/convert_names/")
def convert_names(request: NameRequest, version: str = "v1"):
    return process_request(request, version)
