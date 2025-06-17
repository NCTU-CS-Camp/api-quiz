import requests


API_URL = "http://localhost:9000"

USERNAME = "alice"
PASSWORD = "123"


# 任務三 使用 PATCH 方法更新個人資料
def update_my_account(username, team, iq):
    """更新自己的帳號資訊"""
    resp = requests.patch(
        f"{API_URL}/user",
        auth=(USERNAME, PASSWORD),
        json={"username": username, "team": team, "iq": iq}
    )
    print("PATCH /user →", resp.status_code, resp.json())
    return resp.json()

# 任務四 使用 DELETE 方法刪除個人帳號
def delete_my_account():
    """刪除自己的帳號"""
    resp = requests.delete(
        f"{API_URL}/user",
        auth=(USERNAME, PASSWORD)
    )
    print("DELETE /user →", resp.status_code, resp.json())
    return resp.json()


if __name__ == "__main__":
    # update_my_account("alice", "3", 100)
    delete_my_account()

  