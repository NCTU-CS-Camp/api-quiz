import requests


API_URL = "http://localhost:9000"

USERNAME = "your_username"  # 替換為你的用戶名
PASSWORD = "your_password"  # 替換為你的密碼


# 任務三 更新個人資料
def update_my_account(username, team, iq):
    """
    TODO: 呼叫 PATCH /user，帶入 JSON 更新欄位，並回傳 JSON 結果
    """
    resp = requests._____(              # <1> HTTP 方法
        f"{API_URL}/users/me",
        auth=(USERNAME, PASSWORD),
        json={"username": username, "team": team, "iq": iq}
    )
    print("更新個人資料")
    print("/users/me →", resp.status_code, resp.json())
    return resp.json()

# 任務四 刪除個人帳號
def delete_my_account():
    """刪除自己的帳號"""
    resp = requests._____(               # <2> HTTP 方法
        f"{API_URL}/users/me",
        auth=(USERNAME, PASSWORD)
    )
    print("刪除個人帳號")   
    print("/users/me →", resp.status_code, resp.json())
    return resp.json()


if __name__ == "__main__":
    my_name = "alice"
    my_team = "100"
    my_iq = 100
    update_my_account(my_name, my_team, my_iq)
    delete_my_account()        # 刪除了怎麼辦？再去 quiz1.py 重新註冊一次

  