import requests

API_URL = "http://localhost:9000"

USERNAME = "alice"
PASSWORD = "123"


# 任務一: 使用 POST 方法註冊帳號
def register(username, password):
    resp = requests.post(
        f"{API_URL}/register",
        json={"username": username, "password": password}
    )
    print("register →", resp.status_code, resp.json())


# 任務二: 使用 GET 方法取得個人資料
def get_my_account():
    """取得自己的帳號資訊"""
    resp = requests.get(
        f"{API_URL}/user",
        auth=(USERNAME, PASSWORD)
    )
    print("GET /user →", resp.status_code, resp.json())
    if resp.status_code == 200:
        return resp.json()
    else:
        return None



if __name__ == "__main__":
    register(USERNAME, PASSWORD)   # 註冊用戶
    user = get_my_account()        # 取得自己的帳號資訊
    if user:
        # 顯示用戶資訊
        print("=== 我的帳號資訊 ===")
        print(f"用戶名稱: {user['username']}, 所在組別: {user['team']}, IQ: {user['iq']}")
