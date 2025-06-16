import requests

API_URL = "http://localhost:9000"  # 改成你的後端位址

USERNAME = "admin"    # 直接寫或從 input 讀進來
PASSWORD = "admin123"

def get_all_users():
    """取得所有用戶資訊"""
    resp = requests.get(
        f"{API_URL}/admin/users",
        auth=(USERNAME, PASSWORD)
    )
    print("GET /admin/users →", resp.status_code, resp.json())
    
    users = resp.json().get('users', [])
    if not users:
        print("沒有用戶資料")
        return []
    
    print("=======================")
    print("用戶列表:")
    for user in users:
        print(f"用戶 ID: {user['id']}, 名稱: {user['username']}, IQ: {user.get('iq', '未知')}")
    print("=======================")

    return resp.json().get('users', [])

def delete_user(user_id):
    """刪除指定用戶"""
    resp = requests.delete(
        f"{API_URL}/admin/users/{user_id}",
        auth=(USERNAME, PASSWORD)
    )
    print(f"DELETE /admin/users/{user_id} →", resp.status_code, resp.json())

if __name__ == "__main__":
    get_all_users()

    # resp = requests.post(
    #     f"{API_URL}/questions/1",
    #     auth=(USERNAME, PASSWORD),
    #     json={"answer": "2"}  # 假設答案是 42
    # )

    # print(resp.status_code, resp.json())