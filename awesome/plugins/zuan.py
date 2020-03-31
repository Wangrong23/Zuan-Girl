import requests
import re
from nonebot import on_command, CommandSession
from nonebot.helpers import render_expression

high_level_api_url = 'https://nmsl.shadiao.app/api.php?lang=zh_cn'
min_level_api_url = 'https://nmsl.shadiao.app/api.php?level=min&lang=zh_cn'


# on_command 装饰器将函数声明为一个命令处理器
# 这里 喷 为命令的名字，同时允许使用别名「喷一下」「给我喷」
@on_command('喷', aliases=('喷一下', '给我喷'))
async def curse(session: CommandSession):
    member = session.get('member', prompt='你想喷谁呢？')
    text = await get_min_level_curse_text()
    await session.send(
                render_expression(
                    ('[CQ:at,qq={at_id}] {text}'),
                    at_id=member,
                    text=text
                )
            )

@on_command('使劲喷', aliases=('使劲喷一下', '给我使劲喷'))
async def hard_curse(session: CommandSession):
    member = session.get('member', prompt='你想喷谁呢？')
    text = await get_high_level_curse_text()
    await session.send(
                render_expression(
                    ('[CQ:at,qq={at_id}] {text}'),
                    at_id=member,
                    text=text
                )
            )


@on_command('祖安语录', aliases=('祖安话', '来点祖安语录'))
async def a_curse(session: CommandSession):
    text = await get_high_level_curse_text()
    await session.send(text)

# curse.args_parser 装饰器将函数声明为 curse 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@curse.args_parser
@hard_curse.args_parser
async def _(session: CommandSession):
    print('session',session)

    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg.strip()
    print('stripped_arg',stripped_arg)

    pattern = re.compile('[1-9]([0-9]{4,10})')
    stripped_arg = pattern.search(stripped_arg).group(0)

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            session.state['member'] = stripped_arg
        return

    if not stripped_arg:
        # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('')

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg

async def get_min_level_curse_text():
    res = requests.get(min_level_api_url)
    return res.text

async def get_high_level_curse_text():
    res = requests.get(high_level_api_url)
    return res.text
