import requests


# joke 網站: https://jokeapi.dev/

# TODO 從 JokeAPI 獲取笑話並印出來
def get_joke():
    """從 JokeAPI 獲取笑話"""
    url = "https://v2.jokeapi.dev/joke/Any"

    # 發送請求
    response = requests.?????(url)              # <1> HTTP 方法 
    
    # 檢查請求是否成功
    if response.status_code == ?????:           # <2> 狀態碼  
        joke_data = response.?????()            # <3> 解析 JSON
        
        # 檢查笑話類型
        if joke_data['type'] == 'single':
            # 單行笑話
            print(f"笑話: {joke_data[?????]}")   # <4> 笑話內容 (去JokeAPI 網站 查看)
        elif joke_data['type'] == 'twopart':
            # 兩段式笑話
            print(f"問題: {joke_data[?????]}") # <5> 笑話問題
            print(f"答案: {joke_data[?????]}") # <6> 笑話答案
        
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