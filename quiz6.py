import requests

API_URL = "http://localhost:9000"

USERNAME = "David"
PASSWORD = "123"

# 任務一 使用 Gemini 生成答案
def generate_answer(question):
    full_text = ""
    return full_text

# 任務二 使用 GET 方法取得各問題
def get_question(question_id):
    pass
    
    
# 任務三 使用 POST 方法提交答案
def submit_answer(question_id, answer):
    pass

    
if __name__ == "__main__":
    question_id = 3
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