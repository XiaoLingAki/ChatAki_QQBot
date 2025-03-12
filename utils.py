import openai
import requests
import time
import json
import sqlite3
import os
import jwt
import base64
from PIL import Image
from io import BytesIO

from loguru import logger
from session import ChatSessionManager_GLM as CM
from zhipuai import ZhipuAI

model_list = ["gpt-3.5-turbo","gpt-4-0613"]
# openai.api_base = "https://api.xty.app/v1"

session_manager = CM()

# GLM API鉴权函数
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

def image_generate_glm(prompt):
    api_key = os.environ["ZHIPUAI_API_KEY"]
    client = ZhipuAI(api_key) # 请填写您自己的APIKey
    response = client.images.generations(
        model="cogview-3", #填写需要调用的模型名称
        prompt=prompt,
    )
    image_url = response.data[0].url
    image_data = requests.get(image_url)

    image_stream = BytesIO(image_data.content)

    image = Image.open(image_stream)
    image.save('output_image.png')

    result = base64.b64encode(image_data.content)
    return result

# GLM API生成函数
def text_generate_glm(history):
    
    # logger.debug(history)
    api_key = os.environ["ZHIPUAI_API_KEY"]
    token = generate_token(api_key, 60)
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    data = {
        "model": "glm-3-turbo",
        "messages": history,
        "max_tokens": 8192,
        "temperature": 0.8,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data)
    ans = response.json()
    result = ans['choices'][0]['message']['content']
    # logger.debug("模型生成：" + result)
    
    return ans['choices'][0]['message']['content']


def chatgpt_pro(history):
    # print(openai.api_key)
    # print(type(history))
    logger.debug(history)
    # logger.debug(openai.api_key)
    # openai.api_base = "http://localhost:8000/v1"
    # openai.api_key = "none"
    prompt_len = 0
    for h in history:
        logger.debug(h)
        prompt_len += len(h['content'])
        logger.debug(prompt_len)
    
    while prompt_len > 4399:
        prompt_len = prompt_len - len(history[1]['content'])
        history = [history[0]] + history[2:]
    url = "http://127.0.0.1:11434/api/chat"
    # url = "https://localhost:8005/v1/chat/completions"
    # url = "https://api.openai-proxy.com/v1/chat/completions"
    # url = "https://api.xty.app/chat/completions"
    # url = "https://api.openai.com/v1/chat/completions"
    # url = "https://ngapi.xyz/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }
    payload = {
        "model": "deepseek-r1:32b",
        "messages": history,
        "stream": False,
        "options": {"temperature": 0.3}
    }
    time1 = time.time()
    logger.debug(time1)
    try:
        response = requests.post(url, headers=headers, json=payload)
        logger.debug(response.text)
    except Exception as e:
        response = f"出错了喵！【大模型接口】{e}"
        logger.debug(response)
        return response

    time2 = time.time()
    if response.status_code == 200 or response.status_code == 202:
        completion = response.json()
        logger.debug(time2-time1)
        logger.debug(completion)

        # GPT接口用这个返回语句
        # return completion["choices"][0]["message"]["content"]

        # DEEPSEEK-R1接口用这个返回语句
        return completion["message"]["content"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return f"出错了喵！：Error: {response.status_code} - {response.text}"

def chatglm_pro(history):
    # print(openai.api_key)
    # print(type(history))
    logger.debug(history)
    logger.debug(openai.api_key)
    openai.api_base = "http://localhost:8003/v1"
    openai.api_key = "none"
    prompt_len = 0
    for h in history:
        print(h)
        prompt_len += len(h['content'])
        print(prompt_len)
    
    while prompt_len > 4399:
        prompt_len = prompt_len - len(history[1]['content'])
        history = [history[0]] + history[2:]
    
    url = "https://localhost:8003/v1/chat/completions"
    # url = "https://api.openai-proxy.com/v1/chat/completions"
    # url = "https://api.openai.com/v1/chat/completions"
    # url = "https://ngapi.xyz/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": history
    }
    time1 = time.time()
    response = requests.post(url, headers=headers, json=payload)
    time2 = time.time()
    if response.status_code == 200 or response.status_code == 202:
        completion = response.json()
        logger.debug(time2-time1)
        return completion["choices"][0]["message"]["content"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def chatglm(prompt, history = []):
    url = "http://localhost:8005"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "history": history
    }
    # logger.debug(prompt)
    response = requests.post(url, headers=headers, json=data)
    logger.debug(response.text)
    response_data = json.loads(response.text)
    
    return response_data

def digital_person_chat(prompt = '', text = '你好', personality = "#粉毛", processer = "chatgpt"):
    
    # logger.debug(f"prompt = {prompt}")
    logger.debug("用户: "+ text)
    logger.debug(processer)
    chat_histories = session_manager.chat_histories

    if personality not in chat_histories:

        if processer == "chatgpt":
        # 如果当前prompt对应的history列表不存在，则创建一个新的空列表
            # print(prompt,text,personality,processer)
            chat_histories[personality] = [{"role": "system", "content": prompt}]
        else:
            # print(prompt,text,personality,processer)
            chat_histories[personality] = [{"role": "system", "content": prompt}]

    print('生成中……\n')
    try:
        if processer == "chatgpt":
            logger.debug("processor=chatgpt")
            chat_histories[personality].append({"role": "user", "content": text})
            logger.debug(chat_histories[personality])
            # logger.debug(prompt + history + text)
            result = chatgpt_pro(chat_histories[personality])
            chat_histories[personality].append({"role": "assistant", "content": result})
            logger.debug(result)
            
        elif processer == "chatglm":
            # logger.debug("processor=chatglm")
            chat_histories[personality].append({"role": "user", "content": text})
            # logger.debug(chat_histories[personality])
            
            # logger.debug(chat_histories[prompt])
            # logger.debug(prompt + history + text)
            result = text_generate_glm(chat_histories[personality])
            
            chat_histories[personality].append({"role": "assistant", "content": result})
            logger.debug("模型生成: "+ result)
            
        else:
            logger.debug("processor=chatglm")
            chat_histories[personality].append({"role": "user", "content": text})
            logger.debug(chat_histories[personality])
            
            # logger.debug(chat_histories[prompt])
            # logger.debug(prompt + history + text)
            result = text_generate_glm(chat_histories[prompt])
            
            chat_histories[personality].append({"role": "assistant", "content": result})
            logger.debug(result)
            
    except Exception as e:
        print(f"连接断开了喵！")
        result = f"出错了喵！【对话生成模块】"

    # result = "测试中~"
    return result


def response_generate(prompt, history = []):
    url = "http://123.207.0.178:8000"
    data = {
        "prompt": prompt,
        "history": history
    }
    response = requests.post(url, json=data)
    return response.text


if __name__ == '__main__':
    # print(openai.api_key)
    # print(chatgpt_pro([
    # {"role": "system", "content": "You are a helpful assistant."},
    # {"role": "user", "content": "There are 9 birds in the tree, the hunter shoots one, how many birds are left in the tree？"}
    # ]))
    # print(openai.Model.list())

    print(chatgpt_pro([{'role': 'system', 'content': ''}, {'role': 'user', 'content': '下午好'}]))
    # image_generate_glm("一只猫")
    
    