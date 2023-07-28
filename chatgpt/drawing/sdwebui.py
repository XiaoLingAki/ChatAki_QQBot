from typing import List
import base64
import httpx
import re
from graia.ariadne.message.element import Image
from loguru import logger
import openai
import requests

from constants import config
from .base import DrawingAPI


def basic_auth_encode(authorization: str) -> str:
    authorization_bytes = authorization.encode('utf-8')
    encoded_authorization = base64.b64encode(authorization_bytes).decode('utf-8')
    return f"Basic {encoded_authorization}"


def init_authorization():
    if config.sdwebui.authorization != '':
        return basic_auth_encode(config.sdwebui.authorization)
    else:
        return ''

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
    if response.status_code == 200 or response.status_code == 202:
        completion = response.json()
        return completion["choices"][0]["message"]["content"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def prompt_translator(prompt):
    history = [
        {'role': 'system', 'content': '请将以下的自然语言描述转换成由多个英语单词构成的特征描述。'},
        {'role': 'user', 'content': '一个粉红色头发的高中女孩，在夜晚的城市，穿着学生装'},
        {'role': 'assistant', 'content': 'pink hair, high school girl, city, night, school suit'},
        {'role': 'user', 'content': '一个穿着中国传统服装的少女，在古代中国风格的街道，举着一把伞'},
        {'role': 'assistant', 'content': 'chinese, china dress, ancient China, umbralla, girl'},
        {'role': 'user', 'content': '一个穿着泳装的粉红色头发少女站在阳光下的沙滩上'},
        {'role': 'assistant', 'content': 'swimsuit, girl, beach, sunshine, pink hair, stand'},
        {'role': 'user', 'content': '一个短发少女站在清晨的城市中，穿着水手服，仰望着镜头'},
        {'role': 'assistant', 'content': 'short hair, stand, girl, morning, city, from above, sailor dress'},
        {'role': 'user', 'content': '一个短发少女站在清晨的城市中，穿着水手服，俯视着镜头'},
        {'role': 'assistant', 'content': 'short hair, girl, stand, morning, city, from below, sailor dress'},
        {'role': 'user', 'content': '一个双马尾少女站在清晨的城市中，穿着水手服，仰望着镜头'},
        {'role': 'assistant', 'content': 'twin-tails, girl, stand, morning, city, sailor dress, from above'},
        {'role': 'user', 'content': '初音未来站在清晨的城市中，穿着水手服，仰望着镜头'},
        {'role': 'assistant', 'content': 'Hatsune Miku, stand, morning, city, from above, sailor dress'},
        {'role': 'user', 'content': '初音未来坐在清晨的城市中，穿着水手服，俯视着镜头'},
        {'role': 'assistant', 'content': 'Hatsune Miku, sit, morning, city, from below, sailor dress'},
        {'role': 'user', 'content': '初音未来坐在清晨的沙滩上，穿着水手服，仰望着镜头'},
        {'role': 'assistant', 'content': 'Hatsune Miku, sit, morning, beach, sailor dress, from above'},
        {'role': 'user', 'content': prompt}
               ]
    return chatgpt_pro(history)


class SDWebUI(DrawingAPI):

    def __init__(self):
        self.headers = {
            "Authorization": f"{init_authorization()}"
        }
        
    def parse_input(self, s):
        logger.debug(s)
        # 创建正则表达式对象
        prompts_pattern = re.compile(r'(.*?)\s+--')
        width_pattern = re.compile(r'--width=(\d+)')
        height_pattern = re.compile(r'--height=(\d+)')
        # 用正则表达式查找
        prompts_match = prompts_pattern.search(s)
        prompts = prompts_match.group(1) if prompts_match else s
        prompts = prompt_translator(prompts)
        logger.debug(prompts)

        width_match = width_pattern.search(s)
        width = int(width_match.group(1)) if width_match else 800

        height_match = height_pattern.search(s)
        height = int(height_match.group(1)) if height_match else 600
        
        # 把结果存入字典
        inputs = {
            'prompts': prompts,
            'width': width,
            'height': height
        }

        return inputs

    async def text_to_img(self, prompt):
        logger.debug(prompt)
        inputs = self.parse_input(str(prompt))
        logger.debug(inputs)
        
        prompts= inputs['prompts']
        width = inputs['width']
        height = inputs['height']
        logger.debug(width)
        payload = {
            'enable_hr': 'false',
            'denoising_strength': 0.45,
            'prompt': f'{config.sdwebui.prompt_prefix}, {prompts}',
            'width': width,
            'height': height,
            'steps': 15,
            'seed': -1,
            'batch_size': 1,
            'n_iter': 1,
            'cfg_scale': 7.5,
            'restore_faces': 'false',
            'tiling': 'false',
            'negative_prompt': config.sdwebui.negative_prompt,
            'eta': 0,
            'sampler_index': config.sdwebui.sampler_index
        }
        print(payload['prompt'])

        for key, value in config.sdwebui.dict(exclude_none=True).items():
            if isinstance(value, bool):
                payload[key] = 'true' if value else 'false'
            else:
                payload[key] = value

        resp = await httpx.AsyncClient(timeout=config.sdwebui.timeout).post(f"{config.sdwebui.api_url}sdapi/v1/txt2img",
                                                                            json=payload, headers=self.headers)
        resp.raise_for_status()
        r = resp.json()

        return [Image(base64=i) for i in r.get('images', [])]

    async def img_to_img(self, init_images: List[Image], prompt=''):
        # 需要调用get_bytes方法，才能获取到base64字段内容
        for x in init_images: await x.get_bytes()
        # 消息链显示字符串中有“[图片]”字样，需要过滤
        prompt = prompt.replace("[图片]", "")
        payload = {
            'init_images': [x.base64 for x in init_images],
            'enable_hr': 'false',
            'denoising_strength': 0.45,
            'prompt': f'{config.sdwebui.prompt_prefix}, {prompt}',
            'steps': 15,
            'seed': -1,
            'batch_size': 1,
            'n_iter': 1,
            'cfg_scale': 7.5,
            'restore_faces': 'false',
            'tiling': 'false',
            'negative_prompt': config.sdwebui.negative_prompt,
            'eta': 0,
            'sampler_index': config.sdwebui.sampler_index,
            "filter_nsfw": 'true' if config.sdwebui.filter_nsfw else 'false',
        }

        for key, value in config.sdwebui.dict(exclude_none=True).items():
            if isinstance(value, bool):
                payload[key] = 'true' if value else 'false'
            else:
                payload[key] = value

        resp = await httpx.AsyncClient(timeout=config.sdwebui.timeout).post(f"{config.sdwebui.api_url}sdapi/v1/img2img",
                                                                            json=payload, headers=self.headers)
        resp.raise_for_status()
        r = resp.json()
        return [Image(base64=i) for i in r.get('images', [])]
