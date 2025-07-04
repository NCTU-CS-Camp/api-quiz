import utf8_basic_patch
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

API_URL  = os.getenv("API_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


# TODO: 註冊帳號
def register(username, password):
    """
    TODO: 呼叫 /users，並印出回應狀態與 JSON
    """
    resp = requests.?????(                      # <1> HTTP 方法
        f"{API_URL}/users",
        json={"username": username, "password": password}
    )
    print("register →", resp.status_code, resp.json()) 


# TODO: 取得個人資料
def get_my_account():
    """
    TODO: 呼叫 /user，並印出回應狀態與 JSON
    """
    resp = requests.?????(                     # <2> HTTP 方法
        f"{API_URL}/users/me",
        auth=(USERNAME, PASSWORD)
    )
    print("/user →", resp.?????, resp.?????)   # <3> 印出狀態碼 & JSON
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"error: {resp.status_code} - {resp.json()['error']}")
        return None



if __name__ == "__main__":
    register(USERNAME, PASSWORD)   # 註冊用戶
    user = get_my_account()        # 取得自己的帳號資訊
    if user is not None:           # 非空代表成功取得用戶資訊
        # 顯示用戶資訊
        print("=== 我的帳號資訊 ===")
        print(f"用戶名稱: {user['username']}, 所在組別: {user['team']}, IQ: {user['iq']}")
