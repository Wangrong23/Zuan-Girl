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
    for word in words:
        # 每个元素是一个 pair 对象，包含 word 和 flag 两个属性，分别表示词和词性
        if word.flag == 'n':
            # n	普通名词	f	方位名词	s	处所名词	t	时间
            # nr	人名	ns	地名	nt	机构名	nw	作品名
            # nz	其他专名	v	普通动词	vd	动副词	vn	名动词
            # a	形容词	ad	副形词	an	名形词	d	副词
            # m	数量词	q	量词	r	代词	p	介词
            # c	连词	u	助词	xc	其他虚词	w	标点符号
            # PER	人名	LOC	地名	ORG	机构名	TIME	时间
            await session.send(word.word+reply_words[rand_int], at_sender=True)
            break

    