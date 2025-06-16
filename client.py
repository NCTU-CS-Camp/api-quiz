import requests

API_URL = "http://localhost:9000"  # 改成你的後端位址

USERNAME = "alice"    # 直接寫或從 input 讀進來
PASSWORD = "secret"

def register(username, password):
    resp = requests.post(
        f"{API_URL}/register",
        json={"username": username, "password": password}
    )
    print("register →", resp.status_code, resp.json())


def delete_my_account():
    """刪除自己的帳號"""
    resp = requests.delete(
        f"{API_URL}/user",
        auth=(USERNAME, PASSWORD)
    )
    print("DELETE /user →", resp.status_code, resp.json())


def get_my_account():
    """取得自己的帳號資訊"""
    resp = requests.get(
        f"{API_URL}/user",
        auth=(USERNAME, PASSWORD)
    )
    print("GET /user →", resp.status_code, resp.json())
    
def get_my_iq():
    """取得自己的 IQ"""
    resp = requests.get(
        f"{API_URL}/user/iq",
        auth=(USERNAME, PASSWORD)
    )
    print("GET /user/iq →", resp.status_code, resp.json())


if __name__ == "__main__":
    # register(USERNAME, PASSWORD)   # 註冊用戶
    # delete_my_account()            # 刪除自己的帳號
    # get_my_account()                 # 取得自己的帳號資訊
    # get_my_iq()                      # 取得自己的 IQ
    
    resp = requests.post(
        f"{API_URL}/questions/1",
        auth=(USERNAME, PASSWORD),
        json={"answer": "2"}  # 假設答案是 42
    )

    print(resp.status_code, resp.json())