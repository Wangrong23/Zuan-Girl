import re
import base64
from urllib import parse
import requests
import time
from nonebot import on_command,on_natural_language, CommandSession, NLPSession, IntentCommand
from nonebot.helpers import render_expression

@on_command('搜磁力', aliases=('磁力搜索', '搜种'))
async def search(session: CommandSession):
    keyword = session.get('keyword', prompt='你想搜啥？')
    await session.send("等会儿，我找找")
    result = await to_search(keyword)
    await session.send(result)

@search.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            session.state['keyword'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('你想搜啥？')

    session.state[session.current_key] = stripped_arg


async def to_search(keyword):
    url = "https://ciligou.app/search?word="+keyword+'&sort=rele&p=1'

    # res = requests.get(url,headers=headers)
    res = requests.get(url)
    ret = res.text

    itemTitleCode = re.findall(r'<a style="border-bottom:none;" href="/information/.*?" class="SearchListTitle_result_title">(.*?)</a>', ret, re.S)
    magnetCode = re.findall(r'<a style="border-bottom:none;" href="/information/(.*?)" class="SearchListTitle_result_title">', ret, re.S)
    fileType = re.findall(r'<em>文件格式：</em>(.*?)</div>', ret, re.S)
    fileSize = re.findall(r'<em>文件大小：</em>(.*?)<em>', ret, re.S)

    titleList = []
    fileTypeList = []
    fileSizeList = []
    magnetList = []

    itemAmount = len(itemTitleCode) if len(itemTitleCode)<=5 else 5

    result_text = ''
    for m in range(itemAmount):
        a = re.sub('[+"]', '', itemTitleCode[m])
        b = parse.unquote(a)
        c = re.compile(r'<[^>]+>',re.S)
        itemTitle = c.sub('', b)
        titleList.append(itemTitle)
        fileTypeList.append(fileType[m])
        fileSizeList.append(fileSize[m])
        magnet = await get_magnet(magnetCode[m])
        magnetList.append(magnet)

        title = "".join(titleList[m])
        magnet = "".join(magnetList[m])
        type = "".join(fileTypeList[m])
        size = "".join(fileSizeList[m])

        result_text += "\r"
        result_text += ("资源名称："+title+"\r")
        result_text += ("资源类型：" + type+"\r")
        result_text += ("资源大小：" + size+"\r")
        result_text += ("磁力链接："+magnet+"\r")
        result_text += ("\r")

    return result_text

async def get_magnet(magnetCode):
    url = "https://ciligou.app/information/"+magnetCode
    res = requests.get(url)
    # res = requests.get(url,headers=headers)
    ret = res.text
    magnet = re.findall(r'<div class="Information_l_content"><a href=".*?" class="Information_magnet" id="down-url">(.*?)</a><div class="Information_download_tips">', ret, re.S)
    time.sleep(2)
    return magnet