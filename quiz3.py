import requests
import json

def get_joke():
    """從 JokeAPI 獲取笑話"""
    url = "https://v2.jokeapi.dev/joke/Any"
    
    try:
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
            
    except requests.exceptions.RequestException as e:
        print(f"網路請求錯誤: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON 解析錯誤: {e}")
    except KeyError as e:
        print(f"資料格式錯誤: {e}") 

if __name__ == "__main__":
    print("=== JokeAPI 笑話產生器 ===")
    
    while True:
        choice = input("\n按 Enter 獲取笑話，輸入 'q' 退出: ")
        
        if choice.lower() == 'q':
            print("再見！")
            break
        
        get_joke()