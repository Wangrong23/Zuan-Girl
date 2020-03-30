import requests
import re
from nonebot import on_command, CommandSession


# on_command 装饰器将函数声明为一个命令处理器
# 这里 舔 为命令的名字，同时允许使用别名「舔一下」「给我舔」
@on_command('舔', aliases=('舔一下', '给我舔'))
async def lick(session: CommandSession):
    # 从会话状态（session.state）中获取成员名称（member），如果当前不存在，则询问用户
    member = session.get('member', prompt='你想舔谁呢？')
    # 获取城市的天气预报
    lick_report = await get_lick(member)
    # 向用户发送天气预报
    await session.send(lick_report)

@on_command('舔狗语录', aliases=('彩虹屁', '来点舔狗语录' , '来点彩虹屁'))
async def a_lick(session: CommandSession):
    api_url = 'https://chp.shadiao.app/api.php'
    res = requests.get(api_url)
    await session.send(res.text)

# lick.args_parser 装饰器将函数声明为 lick 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@lick.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            # 舔一下 [CQ:at,qq=1301236461]
            pattern = re.compile('[1-9]([0-9]{5,11})')
            print(pattern.search(stripped_arg))
            session.state['member'] = pattern.search(stripped_arg)[0]
        return

    if not stripped_arg:
        # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('你想舔谁呢？')

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg

async def get_lick(member: str) -> str:
    api_url = 'https://chp.shadiao.app/api.php'
    res = requests.get(api_url)
    return f'[CQ:at,qq={member}] {res.text}'