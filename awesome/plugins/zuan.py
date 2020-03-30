import requests
from nonebot import on_command, CommandSession


# on_command 装饰器将函数声明为一个命令处理器
# 这里 喷 为命令的名字，同时允许使用别名「喷一下」「给我喷」
@on_command('[CQ:at,qq=2461784356] 喷', aliases=('[CQ:at,qq=2461784356] 喷一下', '[CQ:at,qq=2461784356] 给我喷'))
async def curse(session: CommandSession):
    # 从会话状态（session.state）中获取成员名称（member），如果当前不存在，则询问用户
    member = session.get('member', prompt='你想喷谁呢？')
    # 获取城市的天气预报
    curse_report = await get_curse(member)
    # 向用户发送天气预报
    await session.send(curse_report)


# curse.args_parser 装饰器将函数声明为 curse 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@curse.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

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

async def get_curse(member: str) -> str:
    api_url = 'https://nmsl.shadiao.app/api.php?level=min&lang=zh_cn'
    res = requests.get(api_url)
    return f'[CQ:at,qq={member}] {res.text}'