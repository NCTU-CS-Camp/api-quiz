import utf8_basic_patch
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

API_URL  = os.getenv("API_URL", "http://localhost:9000")
USERNAME = os.getenv("USERNAME", "your_username")
PASSWORD = os.getenv("PASSWORD", "your_password")

# 任務一 使用 GET 方法取得問題
def get_questions():
    response = requests.get(f"{API_URL}/questions", auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        print(f"error: {response.status_code} - {response.json()['error']}")
        return None

# 任務二 使用 GET 方法取得各問題
def get_question(question_id):
    response = requests.get(f"{API_URL}/questions/{question_id}", auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"error: {response.status_code} - {response.json()['error']}")
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
        print(f"error: {response.status_code} - {response.json()['error']}")
        return None

    
if __name__ == "__main__":
    get_questions()
    question_id = int(input("請輸入問題 ID: "))
    question = get_question(question_id)
    if not question: # 取得失敗及為空
        print("無法取得問題，請檢查問題 ID 或是否登入。")
        exit(1)
    print("問題:", question['question'])
    
    answer = input("請輸入你的答案: ")
    result = submit_answer(question_id, answer)
    if result:
        print("提交結果:", result)