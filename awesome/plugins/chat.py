""" 机器人插件
"""

""" 腾讯机器人
https://ai.qq.com/
智能闲聊 功能
"""
import hashlib
import json
import random
import string
import time
from typing import Optional
from urllib import parse

import httpx
from nonebot import CommandSession
from nonebot.helpers import context_id

TENCENT_AI_APP_ID = '2131029764'
TENCENT_AI_APP_KEY = 'x4BKsoVmTHKJQvXO'


from aiocqhttp.message import escape
from nonebot import (
    CommandSession, IntentCommand, NLPSession, on_command, on_natural_language
)
from nonebot.helpers import render_expression



# 定义无法获取机器人回复时的「表达（Expression）」
EXPR_DONT_UNDERSTAND = (
    '我现在还不太明白你在说什么呢，但没关系，以后的我会变得更强呢！',
    '我有点看不懂你的意思呀，可以跟我聊些简单的话题嘛',
    '其实我不太明白你的意思...',
    '抱歉哦，我现在的能力还不能够明白你在说什么，但我会加油的～'
) # yapf: disable


# 注册一个仅内部使用的命令，不需要 aliases
@on_command('robot')
async def robot(session: CommandSession):
    # 获取可选参数，这里如果没有 message 参数，命令不会被中断，message 变量会是 None
    message = session.state.get('message')

    # 通过封装的函数获取机器人的回复
    reply = await call_tencent_api(session, message)
    if reply:
        await session.send(escape(reply), at_sender=True)
        return

    # 如果调用失败，或者它返回的内容我们目前处理不了，发送无法获取回复时的「表达」
    # 这里的 render_expression() 函数会将一个「表达」渲染成一个字符串消息
    await session.send(render_expression(EXPR_DONT_UNDERSTAND), at_sender=True)


@on_natural_language(only_short_message=False)
async def _(session: NLPSession):
    # 以置信度 60.0 返回 robot 命令
    # 确保任何消息都在且仅在其它自然语言处理器无法理解的时候使用 robot 命令
    return IntentCommand(60.0, 'robot', args={'message': session.msg_text})


async def call_tencent_api(session: CommandSession,
                           text: str) -> Optional[str]:
    """ 调用腾讯机器人的 API 获取回复
    """
    if not TENCENT_AI_APP_KEY:
        return None

    if not text:
        return None

    url = 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat'

    # 构造请求数据
    payload = {
        'app_id':
        int(TENCENT_AI_APP_ID),
        'time_stamp':
        int(time.time()),
        'nonce_str':
        ''.join(random.sample(string.ascii_letters + string.digits, 32)),
        'session':
        context_id(session.ctx, use_hash=True),
        'question':
        text
    }
    # 接口鉴权 签名
    payload['sign'] = gen_sign_string(payload, TENCENT_AI_APP_KEY)

    try:
        # 使用 httpx 库发送最终的请求
        async with httpx.AsyncClient() as client:
                resp = await client.get(url, params=payload)
                if resp.status_code != 200:
                    # 如果 HTTP 响应状态码不是 200，说明调用失败
                    return None

                resp_payload = json.loads(resp.text)
                if resp_payload['ret'] != 0:
                    # 返回非 0 表示出错
                    return None

                return resp_payload['data']['answer']
    except (httpx.HTTPError, json.JSONDecodeError, KeyError):
        # 抛出上面任何异常，说明调用失败
        return None


def gen_sign_string(parser, app_key: str):
    """ 获取请求签名，接口鉴权 https://ai.qq.com/doc/auth.shtml
    1.将 <key, value> 请求参数对按 key 进行字典升序排序，得到有序的参数对列表 N
    2.将列表 N 中的参数对按 URL 键值对的格式拼接成字符串，得到字符串 T（如：key1=value1&key2=value2），
        URL 键值拼接过程 value 部分需要 URL 编码，URL 编码算法用大写字母，例如 %E8，而不是小写 %e8
    3.将应用密钥以 app_key 为键名，组成 URL 键值拼接到字符串 T 末尾，得到字符串 S（如：key1=value1&key2=value2&app_key = 密钥)
    4.对字符串 S 进行 MD5 运算，将得到的 MD5 值所有字符转换成大写，得到接口请求签名
    :param parser: dect
    :param app_key: str
    :return: str,签名
    """
    params = sorted(parser.items())
    uri_str = parse.urlencode(params, encoding='UTF-8')
    sign_str = '{}&app_key={}'.format(uri_str, app_key)
    # print('sign =', sign_str.strip())
    hash_md5 = hashlib.md5(sign_str.encode('UTF-8'))
    return hash_md5.hexdigest().upper()