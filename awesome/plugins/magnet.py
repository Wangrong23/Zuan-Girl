import re
import base64
from urllib import parse
from urllib import request
from nonebot import on_command,on_natural_language, CommandSession, NLPSession, IntentCommand
from nonebot.helpers import render_expression


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
        # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('')

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg



async def to_search(keyword):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    }
    bytesKeyWord = keyword.encode(encoding="utf-8")
    decodeWord = base64.b64encode(bytesKeyWord)
    keyCode = decodeWord.decode()
    urlPart1 = "https://ciligou.app/search?word="+keyCode+'&sort=rele&p='

    result_text = ''
    for pageNum in range(1,2):
        result_text += '\r'
        url = urlPart1+str(pageNum)
        print(url)
        req = request.Request(url=url,headers=headers)
        res = request.urlopen(req)
        ret = res.read().decode("utf-8")

        itemTitleCode = re.findall(r'<a style="border-bottom:none;" href="/information/.*?" class="SearchListTitle_result_title">(.*?)</a>', ret, re.S)
        magnetCode = re.findall(r'<a style="border-bottom:none;" href="/information/(.*?)" class="SearchListTitle_result_title">', ret, re.S)
        fileType = re.findall(r'<em>文件格式：</em>(.*?)</div>', ret, re.S)
        fileSize = re.findall(r'<em>文件大小：</em>(.*?)<em>', ret, re.S)

        titleList = []
        fileTypeList = []
        fileSizeList = []
        magnetList = []

        itemAmount = len(itemTitleCode)

        for m in range(itemAmount):
            result_text += '\r'
            a = re.sub('[+"]', '', itemTitleCode[m])
            b = parse.unquote(a)
            c = re.compile(r'<[^>]+>',re.S)
            itemTitle = c.sub('', b)
            titleList.append(itemTitle)
            fileTypeList.append(fileType[m])
            fileSizeList.append(fileSize[m])
            magnetPart1 = "magnet:?xt=urn:btih:"
            magnetPart2 = magnetCode[m]
            magnet = magnetPart1+magnetPart2
            magnetList.append(magnet)

            title = "".join(titleList[m])
            magnet = "".join(magnetList[m])
            type = "".join(fileTypeList[m])
            size = "".join(fileSizeList[m])

            result_text += "\r"
            result_text += ("资源名称："+title)
            result_text += ("资源类型：" + type)
            result_text += ("资源大小：" + size)
            result_text += ("磁力链接："+magnet)
            result_text += ("\r")

        return result_text;