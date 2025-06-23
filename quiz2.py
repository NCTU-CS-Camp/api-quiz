import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

API_URL  = os.getenv("API_URL", "http://localhost:9000")
USERNAME = os.getenv("USERNAME", "your_username")
PASSWORD = os.getenv("PASSWORD", "your_password")


# TODO 更新個人資料
def update_my_account(new_info):
    """
    TODO: 呼叫 /user，帶入 JSON 更新欄位，並回傳 JSON 結果
    """
    resp = requests.?????(              # <1> HTTP 方法
        f"{API_URL}/users/me",
        auth=(USERNAME, PASSWORD),
        json=?????                      # <2> 帶入更新的 JSON 資料
    )
    print("更新個人資料")
    print("/users/me →", resp.status_code, resp.json())
    return resp.json()

# TODO 刪除個人帳號
def delete_my_account():
    """刪除自己的帳號"""
    resp = requests.?????(               # <3> HTTP 方法
        f"{API_URL}/users/me",
        auth=(USERNAME, PASSWORD)
    )
    print("刪除個人帳號")   
    print("/users/me →", resp.status_code, resp.json())
    return resp.json()


if __name__ == "__main__":
    new_info = {
        # "username": "new_username",
        # "password": "new_password",
        "team": "100",
        "iq": 150
    }
    update_my_account(new_info)
    delete_my_account()        # 刪除了怎麼辦？再去 quiz1.py 重新註冊一次

  