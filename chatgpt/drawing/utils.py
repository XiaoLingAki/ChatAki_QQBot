import openai
import requests
import os


model_list = ["gpt-3.5-turbo","gpt-4-0613"]

def chatgpt_pro(history):
    # print(openai.api_key)
    print(type(history))
    print(history)
    
    prompt_len = 0
    for h in history:
        print(h)
        prompt_len += len(h['content'])
        print(prompt_len)
    
    while prompt_len > 4399:
        prompt_len = prompt_len - len(history[1]['content'])
        history = [history[0]] + history[2:]
    
    # url = "https://api.openai-proxy.com/v1/chat/completions"
    # url = "https://api.openai.com/v1/chat/completions"
    url = openai.api_base + "/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }
    payload = {
        "model": "gpt-4-0613",
        "messages": history
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        completion = response.json()
        return completion["choices"][0]["message"]["content"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None




if __name__ == '__main__':
    # print(openai.api_key)
    print(chatgpt_pro([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "There are 9 birds in the tree, the hunter shoots one, how many birds are left in the tree？"}
    ]))
    # print(openai.Model.list())