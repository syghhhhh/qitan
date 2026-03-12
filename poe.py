import os
import requests

api_key = os.getenv("POE_API_KEY")

url = "https://api.poe.com/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
# print(headers)
data = {
    # "model": "gemini-3-flash",
    "model": "gpt-5.4",
    "messages": [
        {"role": "user", "content": "你好"}
    ]
}

# 设置代理
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

try:
    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    response.raise_for_status()
    result = response.json()
    print(result["choices"][0]["message"]["content"])
except Exception as e:
    print(f"错误: {e}")