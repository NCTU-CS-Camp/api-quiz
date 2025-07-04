import utf8_basic_patch
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

API_URL  = os.getenv("API_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# TODO 取得問題數``
def get_questions():
    """
    TODO: 呼叫 /questions，並回傳 JSON 結果
    """
    response = requests.?????(                 # <1> HTTP 方法
        f"{API_URL}/questions",
        auth=(USERNAME, PASSWORD)
    )
    if response.status_code == ?????:           # <2> 狀態碼
        print(response.json())
        return response.json()
    else:
        print(f"error: {response.status_code} - {response.json()['error']}")
        return None

# TODO 取得各問題
def get_question(question_id):
    """
    TODO: 呼叫 /questions/{question_id}，並回傳 JSON 結果
    """
    response = requests.?????(                 # <3> HTTP 方法
        f"{API_URL}/questions/{question_id}",
        auth=(USERNAME, PASSWORD)
    )
    if response.status_code == ?????:           # <4> 狀態碼
        return response.json()
    else:
        print(f"error: {response.status_code} - {response.json()['error']}")
        return None
    
    
# TODO 提交答案
def submit_answer(question_id, answer):
    """
    TODO: 呼叫 /questions/{question_id}，並提交答案
    """
    response = requests.?????(                  # <5> HTTP 方法
        f"{API_URL}/questions/{question_id}",
        auth=(USERNAME, PASSWORD),
        json={"answer": answer}
    )
    if response.status_code == ?????:           # <6> 狀態碼
        return response.json()
    else:
        print(f"error: {response.status_code} - {response.json()['error']}")
        return None
    
if __name__ == "__main__":
    get_questions()
    question_id = int(input("請輸入問題 ID: "))
    question = get_question(question_id)
    if ?????:        # <7> 檢查問題是否存在
        print("無法取得問題，請檢查問題 ID 或是否登入。")
        exit(1)
    print("問題:", question['question'])
    # http://140.113.168.192:9000/name 查看隊輔名字
    
    answer = input("請輸入你的答案: ")
    result = submit_answer(question_id, answer)
    if result:
        print("提交結果:", result)