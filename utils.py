import openai
import requests
import time
import json
import sqlite3
import os

from loguru import logger

model_list = ["gpt-3.5-turbo","gpt-4-0613"]
# openai.api_key = "sk-8Pv9elfAVKqS6UpxEa00Ec09391f421f856dB68eDbE29072"
# openai.api_base = "https://ngapi.xyz/v1"


class ChatSessionManager:
    def __init__(self, histories = {}):
        self.chat_histories = histories
        # self.chat_id = 0
        # self.chat_name = ''
        # 建立数据库连接
        self.conn = sqlite3.connect('chats.db')
        self.cursor = self.conn.cursor()

        # 创建表格
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sessions
                              (id INTEGER PRIMARY KEY, content TEXT, filename TEXT)''')


    def reset(self):
        self.chat_histories = {}
        
    def save(self, id = 1):
        logger.debug(f"保存到槽位{id}")
        # 生成JSON文件名
        save_directory = "save"
        os.makedirs(save_directory, exist_ok=True)
        filename = os.path.join(save_directory, f'session_{id}.json')

        # 将chat_histories保存为JSON文件
        with open(filename, 'w') as file:
            json.dump(self.chat_histories, file)

        # 执行插入或更新语句
        self.cursor.execute("INSERT OR REPLACE INTO sessions (id, filename) VALUES (?, ?)", (id, filename))

        # 提交更改
        self.conn.commit()

        
    def load(self, id = 1):
        logger.debug(f"读取到槽位{id}")
        # 查询指定id的记录
        self.cursor.execute("SELECT filename FROM sessions WHERE id=?", (id,))
        result = self.cursor.fetchone()

        # 如果找到记录，则读取对应的JSON文件，并将内容反序列化为chat_histories
        if result is not None:
            filename = result[0]
            with open(filename, 'r') as file:
                self.chat_histories = json.load(file)
        else:
            logger.warning("对应槽位没有数据！")
            self.chat_histories = {}
        
    def printchat(self):
        print(self.chat_histories)
        
session_manager = ChatSessionManager()

def chatgpt_pro(history):
    # print(openai.api_key)
    # print(type(history))
    logger.debug(history)
    logger.debug(openai.api_key)
    
    prompt_len = 0
    for h in history:
        print(h)
        prompt_len += len(h['content'])
        print(prompt_len)
    
    while prompt_len > 4399:
        prompt_len = prompt_len - len(history[1]['content'])
        history = [history[0]] + history[2:]
    
    url = "https://api.openai-proxy.com/v1/chat/completions"
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

def digital_person_chat(prompt, text, user_name='用户'):
    
    chat_histories = session_manager.chat_histories

    if prompt not in chat_histories:
        # 如果当前prompt对应的history列表不存在，则创建一个新的空列表
        chat_histories[prompt] = [{"role": "system", "content": prompt}]


    print('生成中……\n')

    chat_histories[prompt].append({"role": "user", "content": text})
    # print(chat_histories[prompt])
    # print(prompt_pre + prompt + prompt_rea + history + text)
    result = chatgpt_pro(chat_histories[prompt])
    # result = "测试中~"
    chat_histories[prompt].append({"role":"assistant","content":result})
    # print(chat_histories[prompt])
    return result


if __name__ == '__main__':
    # print(openai.api_key)
    # print(chatgpt_pro([
    # {"role": "system", "content": "You are a helpful assistant."},
    # {"role": "user", "content": "There are 9 birds in the tree, the hunter shoots one, how many birds are left in the tree？"}
    # ]))
    print(openai.Model.list())