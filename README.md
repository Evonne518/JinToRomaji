# JinToRomaji

---

## **🔄 使用 API 進行日文姓名轉換**

本服務提供 API 來將日文姓名轉換為羅馬拼音。你可以使用 `curl` 或其他 HTTP 工具來發送請求。

### **📌 API 端點**

```
POST https://jintoromaji.onrender.com/convert_names/
```

### **📥 請求格式（JSON）**

```json
{
  "names": [
    {
      "kanji": "山田太郎",
      "katakana": "ヤマダタロウ"
    }
  ]
}
```

### **📤 回應格式（JSON）**

```json
{
  "results": [
    {
      "kanji": "山田太郎",
      "romaji": "YAMADA TAROU"
    }
  ]
}
```

### **🚀 使用 `curl` 測試**

```sh
curl -X POST "https://jintoromaji.onrender.com/convert_names/" \
     -H "Content-Type: application/json" \
     -d '{"names":[{"kanji":"山田太郎","katakana":"ヤマダタロウ"}]}'
```

### **🐍 使用 Python 測試**

```python
import requests

url = "https://jintoromaji.onrender.com/convert_names/"
headers = {"Content-Type": "application/json"}
data = {
    "names": [
        {"kanji": "山田太郎", "katakana": "ヤマダタロウ"}
    ]
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

## **⚙️ API 處理流程**

```
使用者 → FastAPI 接收請求
       → clean_text (移除零寬/特殊字元)
       → 判斷版本 (v1 或 v2)

v1: NameConverter.convert()
    → 回傳 Romaji 字串

v2: NameConverterV2.convert()
    → 回傳 dict {katakana, romaji, inserted_space}

最後 → 組裝 JSON 回應 → 傳回使用者
```

---

## **📝 v1 流程**

```
開始 convert()
  ├─ 全英文？
  │    └─ 直接回傳大寫
  ├─ 有 katakana？
  │    └─ 按空格切分 → pykakasi 轉換 → 大寫回傳
  ├─ kanji 有空格？
  │    ├─ 兩段：姓 + 名 → 詞典查找 → pykakasi → 大寫
  │    └─ 一段：只處理姓 → 詞典查找 → pykakasi → 大寫
```

---

## **📝 v2 流程**

```
開始 convert()
  ├─ 全英文？
  │    └─ 回傳 {romaji, katakana:"", inserted_space:""}
  ├─ 有 katakana？
  │    ├─ 無空格且 kanji 有空格 → 嘗試 split_katakana_by_kanji_parts
  │    │      ├─ 成功 → 回傳結果，inserted_space="Y"
  │    │      └─ 失敗 → _convert_by_kanji()，inserted_space="N"
  │    └─ 已有空格 → 分段轉換 → 回傳結果
  └─ 無 katakana → _convert_by_kanji()，inserted_space="N"
```

