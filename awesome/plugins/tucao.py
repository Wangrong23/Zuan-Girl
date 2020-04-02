from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from jieba import posseg
import random


# on_natural_language 装饰器将函数声明为一个自然语言处理器
# keywords 表示需要响应的关键词，类型为任意可迭代对象，元素类型为 str
# 如果不传入 keywords，则响应所有没有被当作命令处理的消息
@on_natural_language()
async def _(session: NLPSession):
    reply_words = ['个锤子', '个几把','个头','个篮子']
    # 去掉消息首尾的空白符
    stripped_msg = session.msg_text.strip()

    rand_int = random.randint(0,3)
    if rand_int>0:
        return

    # 对消息进行分词
    words = posseg.lcut(stripped_msg)

    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    await session.send(words[0]+reply_words[rand_int], at_sender=True)