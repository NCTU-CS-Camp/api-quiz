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
        return response.json()["api_key"]
    else:
        return None

# 任務一 使用 Gemini 生成答案
def generate_answer(question):
    GOOGLE_API_KEY = get_api_key()
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Answer question: {question}"}
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


# 任務二使用 GET 方法取得各問題
def get_question(question_id):
    response = requests.get(f"{API_URL}/questions/{question_id}", auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
    
# 任務三 使用 POST 方法提交答案
def submit_answer(question_id, answer):
    response = requests.post(
        f"{API_URL}/questions/{question_id}",
        auth=(USERNAME, PASSWORD),
        json={"answer": answer}
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"error: {response.status_code} - {response.json().get('error', '未知錯誤')}")
        return None

    
if __name__ == "__main__":
    question_id = 5  # 假設我們要取得問題 ID 為 5 的問題
    question = get_question(question_id)
    if not question: # 取得失敗及為空
        print("無法取得問題，請檢查問題 ID 或是否登入。")
        exit(1)
    print("問題:", question['question'])
    
    
    print("\n正在使用 Gemini 生成答案...")
    answer_by_gemini = generate_answer(question['question'])
    if not answer_by_gemini:
        print("無法生成答案，請檢查問題或 API 設定。")
        exit(1)
        
    print("\n\n生成的答案:", answer_by_gemini)

    answer = input("請輸入你的答案: ")
    result = submit_answer(question_id, answer)
    if result:
        print("提交結果:", result)