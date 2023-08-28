from fastapi import FastAPI, Request
import uvicorn, json, datetime
import re

from extras import *
from utils import session_manager

# DEVICE = "cuda"
# DEVICE_ID = "0"
# CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE


# def torch_gc():
#     if torch.cuda.is_available():
#         with torch.cuda.device(CUDA_DEVICE):
#             torch.cuda.empty_cache()
#             torch.cuda.ipc_collect()


app = FastAPI()

per_list = ['粉毛','猫娘','猫','初音未来','定型文：开会','键政']
    
personnality = '#粉毛'
def response_create(prompt):

    global personnality
    # global session_manager
    print(personnality)
    if "#定型文：开会" in prompt:
        response = meeting(prompt)
    elif "#Readme" in prompt or "#help" in prompt or "#h" in prompt:
        response = '''聊天粉毛QQ版 beta 0.2
        命令：“#粉毛 #猫娘 #猫 #定型文：开会 #定型文：互联网黑话 #键政 #初音未来”
        默认（不加#）为粉毛
        使用“#切换功能：XX”切换默认的功能
        例如“#切换功能：猫娘”
        之后默认就是猫娘
        命令：“#保存会话记录 槽位”
        将当前会话状态保存到指定槽位（整数1-10，默认为1）
        命令：“#读取会话记录 槽位”
        从指定槽位加载会话状态
        命令：“画个/画一个 【描述】 --height=num --width=num”
        使用stable diffusion生成一张像素为width*height的图
        命令：“切换语音 编号”
        开启语音生成并切换为指定音色
        命令：“#echo”
        检查机器人是否在线
        '''
    elif "#切换功能" in prompt:
        if prompt[6:] in per_list:
            personnality = '#' + prompt[6:]
            response = "成功切换为" + personnality
        else:
            response = "切换失败，功能还在开发中"
    elif "#猫娘" in prompt:
        response = cat_girl(prompt)
    elif "#猫" in prompt:
        response = cat(prompt)
    elif "#粉毛" in prompt:
        response = serika(prompt)
    elif "#初音未来" in prompt:
        response = miku(prompt)
    elif "#键政" in prompt:
        response = politician(prompt)
    elif "#echo" in prompt:
        response = '粉毛摸鱼中，勿cue'
    elif "#重置对话记录" in prompt:
        session_manager.reset()
        response = '哔嘟~已删除聊天记录'
    elif "#保存会话状态" in prompt:
        match = re.search(r'\d+', prompt)
        id = int(match.group())
        logger.debug(id)
        session_manager.save(id)
        response = f'哔嘟~已保存聊天记录到槽位{id}'
    elif "#读取会话状态" in prompt:
        match = re.search(r'\d+', prompt)
        id = int(match.group())
        logger.debug(id)
        session_manager.load(id)
        response = f'哔嘟~已加载聊天记录自槽位{id}'
    elif "#查看聊天记录" in prompt:
        session_manager.printchat()
        response = ' '
    else:
        response = response_create(personnality + prompt)

    return response

@app.post("/")
async def create_item(request: Request):
    # global model, tokenizer
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')
    history = json_post_list.get('history')
    max_length = json_post_list.get('max_length')
    top_p = json_post_list.get('top_p')
    temperature = json_post_list.get('temperature')

    response = ""
    notice = ""
    if len(prompt) > 8000:
        prompt = prompt[0:8000]
        notice = "(输入字符数超过8000，截断后面的输入)"
        
    # try:
    #     response = response_create(prompt)
    #     response = notice + response
    #     print(response)
    # except Exception:
    #     logger.debug(response)
    #     response = "粉毛被撅晕了！正在抢修中，请坐下和放宽~"
    response = response_create(prompt)
    response = notice + response
    print(response)
    # response = "只要看到这个就说明能接收消息"
    history = []
    # response, history = model.chat(tokenizer,
    #                             prompt,
    #                             history=history,
    #                             max_length=max_length if max_length else 2048,
    #                             top_p=top_p if top_p else 0.7,
    #                             temperature=temperature if temperature else 0.95)
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": time
    }
    log = "[" + time + "] " + '", prompt:"' + prompt + '", response:"' + repr(response) + '"'
    print(log)
    # torch_gc()
    # return JsonResponse({'processed_string': prompt})
    return answer


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080, workers=1)
