import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

API_URL  = os.getenv("API_URL", "http://localhost:9000")
USERNAME = os.getenv("USERNAME", "your_username")
PASSWORD = os.getenv("PASSWORD", "your_password")

def get_api_key():
    response = requests.get(f"{API_URL}/api-key")
    if response.status_code == 200:
        return response.json().get("api_key")
    else:
        return None


# TODO：使用 Google Gemini API 生成內容
def generate_content():
    GOOGLE_API_KEY = get_api_key()

    print("正在使用 Google Gemini 生成內容...")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    question = ?????     # <1> 問題內容

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": question}
                ]
            }
        ]
    }

    response = requests.?????(              # <2> HTTP 方法
        f"{url}?key={GOOGLE_API_KEY}",
        json=payload
    )

    if response.ok:
        data = response.json()
        
        # 基本檢查
        if "candidates" not in data or not data["candidates"]:
            print("No candidates returned.")
            exit(1)
            
        # 取第一個 candidate
        candidate = data["candidates"][?????] # <3> 取第一個候選者

        # 取 content、再取 parts
        content = candidate.get(?????, {})    # <4> 取 content
        parts = content.get(?????, [])        # <5> 取 parts
        if not parts:
            print("No parts in content.")
            exit(1)
            
        # 將所有 parts 的文字串起來
        full_text = "".join(part.get("text", "") for part in parts)

        print("Model 回覆：")
        print(full_text)
            
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    generate_content()