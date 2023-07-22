import openai
import time
import requests

openai.api_key = "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"
# openai.api_key = "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"  # OpenAI高级会员


def chatgpt_pro(history):

    url = "https://api.openai-proxy.com/v1/chat/completions"
    # url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": history
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        completion = response.json()
        return completion["choices"][0]["message"]["content"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

