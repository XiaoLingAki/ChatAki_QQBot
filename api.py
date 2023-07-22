from fastapi import FastAPI, Request
import uvicorn, json, datetime

from extras import *

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
    print(personnality)
    if "#定型文：开会" in prompt:
        response = meeting(prompt)
    elif "#Readme" in prompt or "#help" in prompt or "#h" in prompt:
        response = '''聊天粉毛QQ版 beta 0.1
        命令：“#粉毛 #猫娘 #猫 #定型文：开会 #定型文：互联网黑话 #键政 #初音未来”
        默认（不加#）为粉毛
        使用“#切换功能：XX”切换默认的功能
        例如“#切换功能：猫娘”
        之后默认就是猫娘'''
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

    # response = chatgpt(prompt)
    response = response_create(prompt)
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
    return answer


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000, workers=1)