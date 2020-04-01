import re
import base64
from urllib import parse
# from urllib import request
import requests
from nonebot import on_command,on_natural_language, CommandSession, NLPSession, IntentCommand
from nonebot.helpers import render_expression


headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
               'Accept - Encoding':'gzip, deflate',
               'Accept-Language':'zh-Hans-CN, zh-Hans; q=0.5',
               'Connection':'Keep-Alive',
               'Host':'zhannei.baidu.com',
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}


@on_command('搜磁力', aliases=('磁力搜索', '搜资源'))
async def search(session: CommandSession):
    keyword = session.get('keyword', prompt='你想喷谁呢？')
    result = await to_search(keyword)
    await session.send(result)

@search.args_parser
async def _(session: CommandSession):
    print('session',session)

    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            session.state['keyword'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('你想搜啥?')

    session.state[session.current_key] = stripped_arg



async def to_search(keyword):
    url = "https://ciligou.app/search?word="+keyword+'&sort=rele&p=1'

    print(url)

    res = requests.get(url,headers=headers)
    ret = res.text

    itemTitleCode = re.findall(r'<a style="border-bottom:none;" href="/information/.*?" class="SearchListTitle_result_title">(.*?)</a>', ret, re.S)
    magnetCode = re.findall(r'<a style="border-bottom:none;" href="/information/(.*?)" class="SearchListTitle_result_title">', ret, re.S)
    fileType = re.findall(r'<em>文件格式：</em>(.*?)</div>', ret, re.S)
    fileSize = re.findall(r'<em>文件大小：</em>(.*?)<em>', ret, re.S)

    titleList = []
    fileTypeList = []
    fileSizeList = []
    magnetList = []

    for m in range(5):
        result_text += '\r'
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
    print(url)
    res = requests.get(url,headers=headers)
    ret = res.text
    magnet = re.findall(r'<div class="Information_l_content"><a href=".*?" class="Information_magnet" id="down-url">(.*?)</a><div class="Information_download_tips">', ret, re.S)
    return magnet