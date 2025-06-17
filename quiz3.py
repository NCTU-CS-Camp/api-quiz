import requests
import json

# joke 網站: https://jokeapi.dev/

def get_joke():
    """從 JokeAPI 獲取笑話"""
    url = "https://v2.jokeapi.dev/joke/Any"

    # 發送 GET 請求
    response = requests.get(url)
    
    # 檢查請求是否成功
    if response.status_code == 200:
        joke_data = response.json()
        
        # 檢查笑話類型
        if joke_data['type'] == 'single':
            # 單行笑話
            print(f"笑話: {joke_data['joke']}")
        elif joke_data['type'] == 'twopart':
            # 兩段式笑話
            print(f"問題: {joke_data['setup']}")
            print(f"答案: {joke_data['delivery']}")
        
        print(f"分類: {joke_data['category']}")
        print("-" * 50)
        
    else:
        print(f"請求失敗，狀態碼: {response.status_code}")
        

if __name__ == "__main__":
    print("=== JokeAPI 笑話產生器 ===")
    
    while True:
        choice = input("\n按 Enter 獲取笑話，輸入 'q' 退出: ")
        
        if choice.lower() == 'q':
            print("再見！")
            break
        
        get_joke()