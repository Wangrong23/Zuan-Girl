"""
由于大陆自2020年2月1日11时起对海外网络连接的封锁，
部署在海外的bot已无法访问丁香园及其他api，
若您的bot部署在大陆境内，仍可作参考
该功能不再维护。
"""

#copy from https://github.com/Ice-Cirno/HoshinoBot/blob/master/hoshino/modules/subscribe/nCoV2019.py

import re
try:
    import ujson as json
except:
    import json
import random
import asyncio
from urllib.parse import urljoin
from datetime import datetime
import nonebot
from nonebot import CommandSession, MessageSegment, on_command,on_natural_language, NLPSession, IntentCommand
import requests

_api = "https://lab.isaaclin.cn/nCoV/api/"
_timeout = 10

class nCoV2019:
    
    cache = { 'overall': {}, 'news': [], 'news_url': set() }

    @staticmethod
    async def get_overall():
        try:
            url = urljoin(_api, 'overall')
            rsp = await requests.get(url, timeout=_timeout)
            j = await rsp.json()
            data = j['results'][0]
            nCoV2019.cache['overall'] = data
            return data
        except Exception as e:
            print(e)
        return {}


    @staticmethod
    async def _get_news():
        try:
            url = urljoin(_api, 'news')
            rsp = await requests.get(url, timeout=_timeout)
            j = await rsp.json()
            data = j['results']
            return data
        except Exception as e:
            print(e)
        return []


    @staticmethod
    async def update_news():
        news = await nCoV2019._get_news()
        new_ones = []
        for item in news:
            if item['sourceUrl'] not in nCoV2019.cache['news_url']:
                nCoV2019.cache['news_url'].add(item['sourceUrl'])
                new_ones.append(item)
        if news:
            nCoV2019.cache['news'] = news
        return new_ones


    # @staticmethod
    # def get_distribution():
    #     resp = nCoV2019._get_content()
    #     reg = r'<script id="getAreaStat">.+?window.getAreaStat\s=\s(\[.+?\])\}catch\(e\)\{\}</script>'
    #     result = re.search(reg, resp).group(1)
    #     data = json.loads(result)
    #     return data


    # @staticmethod
    # def get_status(name):
    #     data = nCoV2019.get_distribution()
    #     for each in data:
    #         if name in each["provinceName"]:
    #             return each
    #         for city in each["cities"]:
    #             if name in city["cityName"]:
    #                 return each
    #     return None

@on_command('咳', only_to_me=False)
async def cough_redirect(session):
    await session.send('请见丁香园： https://ncov.dxy.cn/ncovh5/view/pneumonia')


@on_command('咳咳', only_to_me=False)
async def cough(session:CommandSession):
    session.finish('请见丁香园： https://ncov.dxy.cn/ncovh5/view/pneumonia')
    name = session.current_arg_text
    if name:    # look up province or city
        # data = nCoV2019.get_status(name)
        # if not data:
        #     return "未知省市"
        # info = '\n'.join([f"{city['cityName']} 确诊{city['confirmedCount']}例" for city in data['cities'] ])
        # text = f"新型冠状病毒肺炎疫情\n{info}\n💊 全国疫情 → t.cn/A6v1xgC0"
        # await session.send(text)
        await session.finish('省市查询维护中...')
    else:   # show overall
        if not nCoV2019.cache['overall']:
            await nCoV2019.get_overall()
        data = nCoV2019.cache['overall']
        if data:
            data['updateTimeStr'] = datetime.fromtimestamp(data['updateTime'] / 1000).strftime(r'%Y-%m-%d %H:%M')
            data['pic1'] = MessageSegment.image(data['dailyPics'][0]) # 新增图
            data['pic2'] = MessageSegment.image(data['dailyPics'][2]) # 累积图
            data['pic3'] = MessageSegment.image(data['dailyPics'][3]) # 治愈死亡图
            text = "新型冠状病毒肺炎疫情\n更新时间：{updateTimeStr}\n确诊{confirmedCount}例(+{confirmedIncr})\n疑似{suspectedCount}例(+{suspectedIncr})\n重症{seriousCount}例(+{seriousIncr})\n死亡{deadCount}例(+{deadIncr})\n治愈{curedCount}例(+{curedIncr})\n{pic1!s}{pic2!s}{pic3!s}\n更多请见丁香园：ncov.dxy.cn/ncovh5/view/pneumonia".format(**data)
            await session.send(text)
        else:
            await session.send('查询出错')


def _make_msg(news_item):
    news_item['pubDateStr'] = datetime.fromtimestamp(news_item['pubDate'] / 1000).strftime(r'%Y-%m-%d %H:%M')
    return "{infoSource}：【{title}】{pubDateStr}\n{summary}\n▲{sourceUrl}".format(**news_item)


@on_command('咳咳咳', only_to_me=False)
async def cough_news(session:CommandSession):
    session.finish('请见丁香园： https://ncov.dxy.cn/ncovh5/view/pneumonia')
    # await nCoV2019.update_news()
    if not nCoV2019.cache['news']:
        await nCoV2019.update_news()
    news = nCoV2019.cache['news']
    if news:
        msg = [ _make_msg(i) for i in news[:min(5, len(news))] ]
        msg = '\n'.join(msg)
        await session.send(f'新冠活动报告：\n{msg}')
    else:
        await session.send('查询出错')
