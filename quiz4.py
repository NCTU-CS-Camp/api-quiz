import requests

API_URL = "http://localhost:9000"

USERNAME = "your_username"  # 替換為你的用戶名
PASSWORD = "your_password"  # 替換為你的密碼

# 任務一 取得問題數
def get_questions():
    response = requests._____(f"{API_URL}/questions", auth=(USERNAME, PASSWORD)) # <1> HTTP 方法
    if response.status_code == _____:  # <2> 狀態碼
        print(response.json())
        return response.json()
    else:
        return None

# 任務二 取得各問題
def get_question(question_id):
    response = requests._____(f"{API_URL}/questions/{question_id}", auth=(USERNAME, PASSWORD)) # <3> HTTP 方法
    if response.status_code == _____:  # <4> 狀態碼
        return response.json()
    else:
        return None
    
    
# 任務三 提交答案
def submit_answer(question_id, answer):
    response = requests._____(                  # <5> HTTP 方法
        f"{API_URL}/questions/{question_id}",
        auth=(USERNAME, PASSWORD),
        json={"answer": answer}
    )
    if response.status_code == _____:           # <6> 狀態碼
        return response.json()
    else:
        print(f"error: {response.status_code} - {response.json().get('error', '未知錯誤')}")
        return None
    
if __name__ == "__main__":
    get_questions()
    question_id = 1  # 假設我們要取得問題 ID 為 1 的問題
    question = get_question(question_id)
    if _____:        # <7> 檢查問題是否存在
        print("無法取得問題，請檢查問題 ID 或是否登入。")
        exit(1)
    print("問題:", question['question'])
    
    answer = input("請輸入你的答案: ")
    result = submit_answer(question_id, answer)
    if result:
        print("提交結果:", result)