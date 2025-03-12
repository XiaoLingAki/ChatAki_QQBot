import json
import sqlite3
import os

from loguru import logger



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
        
        
class ChatSessionManager_GLM:
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