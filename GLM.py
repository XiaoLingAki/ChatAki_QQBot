import requests
import jwt
import time
import os

# 鉴权函数
def generate_token(apikey: str, exp_seconds: int):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )
    
    

def text_generate_glm():
    
    api_key = os.environ["ZHIPUAI_API_KEY"]
    token = generate_token(api_key, 60)
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    data = {
        "model": "glm-4",
        "messages": [
            {
                "role": "system",
                "content": "your are a helpful assistant"
            },
            {
                "role": "user",
                "content": "can you tell me a joke?"
            }
        ],
        "max_tokens": 8192,
        "temperature": 0.8,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data)
    ans = response.json()
    
    print(ans)