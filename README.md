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

你也可以用 **Postman** 或 **Python (requests)** 來測試：
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
