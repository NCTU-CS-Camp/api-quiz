import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

API_URL  = os.getenv("API_URL", "http://localhost:9000")
USERNAME = os.getenv("USERNAME", "your_username")
PASSWORD = os.getenv("PASSWORD", "your_password")


# 任務一 使用 PATCH 方法更新個人資料
def update_my_account(new_info):
    """更新自己的帳號資訊"""
    resp = requests.patch(
        f"{API_URL}/users/me",
        auth=(USERNAME, PASSWORD),
        json=new_info
    )
    print("PATCH /users/me →", resp.status_code, resp.json())
    return resp.json()

# 任務二 使用 DELETE 方法刪除個人帳號
def delete_my_account():
    """刪除自己的帳號"""
    resp = requests.delete(
        f"{API_URL}/users/me",
        auth=(USERNAME, PASSWORD)
    )
    print("DELETE /users/me →", resp.status_code, resp.json())
    return resp.json()


if __name__ == "__main__":
    new_info = {
        # "username": "new_username",
        # "password": "new_password",
        "team": "100",
        "iq": 150
    }
    update_my_account(new_info)
    # delete_my_account() # 刪除了怎麼辦？再去 quiz1.py 重新註冊一次

  