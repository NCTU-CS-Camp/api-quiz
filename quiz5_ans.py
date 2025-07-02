import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

API_URL  = os.getenv("API_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

def get_api_key():
    response = requests.get(f"{API_URL}/api-key")
    if response.status_code == 200:
        return response.json()["api_key"]
    else:
        return None
    
    
# 任務一：使用 Google Gemini API 生成內容
def generate_content():
    GOOGLE_API_KEY = get_api_key()

    print("正在使用 Google Gemini 生成內容...")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    question = "How does AI work?"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": question}
                ]
            }
        ]
    }

    response = requests.post(
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
        candidate = data["candidates"][0]

        parts = candidate["content"]["parts"]       # 取 content、再取 parts
            
        # 將所有 parts 的文字串起來
        full_text = "".join(part["text"] for part in parts)

        return full_text
            
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

if __name__ == "__main__":
    result = generate_content()
    if result:
        print("生成的內容:", result)