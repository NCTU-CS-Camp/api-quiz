import requests

def gererate_content():
    GOOGLE_API_KEY = "AIzaSyCxbVjDyqLssYuc4VWqbHK34YDeuCz7_uQ"

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    question = "How does AI work?"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": question}
                ]
            }
        ]
    }

    response = requests.post(
        f"{url}?key={GOOGLE_API_KEY}",
        json=payload
    )

    if response.ok:
        data = response.json()
        
        # 基本檢查
        if "candidates" not in data or not data["candidates"]:
            print("No candidates returned.")
            exit(1)
            
        # 取第一個 candidate
        candidate = data["candidates"][0]

        # 取 content、再取 parts
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        if not parts:
            print("No parts in content.")
            exit(1)
            
        # 將所有 parts 的文字串起來
        full_text = "".join(part.get("text", "") for part in parts)

        print("Model 回覆：")
        print(full_text)
            
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    gererate_content()