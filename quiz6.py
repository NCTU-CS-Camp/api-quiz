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
    
# TODO 使用 Gemini 生成答案
def generate_answer(question):
    full_text = ""
    return full_text

# TODO 取得各問題
def get_question(question_id):
    pass
    
    
# TODO 提交答案
def submit_answer(question_id, answer):
    pass

    
if __name__ == "__main__":
    question_id = 2  # 假設我們要取得問題 ID 為 2 的問題
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