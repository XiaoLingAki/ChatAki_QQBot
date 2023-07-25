import sqlite3
import json

def insert_chat_record_to_db(chat_id, chat_description, json_file_index):
    # 连接数据库（如果不存在，则创建一个新的数据库文件）
    conn = sqlite3.connect('chatbot.db')

    # 创建表格（如果表格不存在）
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS chat_records (id TEXT UNIQUE, description TEXT, json_file_index TEXT)')

    # 插入数据
    cursor.execute('INSERT INTO chat_records (id, description, json_file_index) VALUES (?, ?, ?)',
                   (chat_id, chat_description, json_file_index))
    
    # 提交更改
    conn.commit()

    # 关闭连接
    conn.close()
