import requests
import re
import json
import random
import string
import time

from pyquery import PyQuery
from urllib.parse import urljoin, urlencode
from faker import Faker
from datetime import datetime
from typing import Any, Optional
from helper.html_parser import HtmlParser
from helper.utility import Utility
from helper.exception import *


class NewsIndexArsip:
    def __init__(self):
        self.__session = requests.session()
        self.__fake = Faker()
        self.__parser = HtmlParser()

        self.__headers = dict()
        self.__headers["Accept"] = "application/json, text/plain, */*"
        self.__headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.__headers["Sec-Fetch-Dest"] = "empty"
        self.__headers["Sec-Fetch-Mode"] = "cors"
        self.__headers["Sec-Fetch-Site"] = "same-site"

    def newsIndex(
        self,
        page: int,
        site: str,
        year: int | str,
        month: int | str,
        date: int | str,
        daerah: Optional[str] = None,
        proxy: Optional[str] = None,
            **kwargs
    ) -> dict:

        user_agent = self.__fake.user_agent()

        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page

        if site != "daerah":
            url = f"https://www.tribunnews.com/index-news/{site}?date={year}-{month}-{date}&page={page}"
        else:
            url = f"https://{daerah}.tribunnews.com/index-news?date={year}-{month}-{date}&page={page}"
        self.__headers["User-Agent"] = user_agent

        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            datas = []
            html = content.decode("utf-8")
            links = []
            for li in self.__parser.pyq_parser(
                html,
                'div[class="content"] ul[class="lsi"] li[class="ptb15"]'
            ):
                article_link = (
                    self.__parser.pyq_parser(
                        li,
                        'li[class="ptb15"] h3[class="f16 fbo"] a'
                    )
                    .attr("href")
                )
                article_link = f"{article_link}?page=all"
                links.append(article_link)
            maxpage = (
                self.__parser.pyq_parser(
                    html,
                    'div[id="paginga"] div[class="paging"] a'
                )
                .eq(-1)
                .attr("href")
            )
            pagematch = re.search(r'page=(\d+)', maxpage)
            if pagematch:
                maxpage = int(pagematch.group(1))
            else:
                maxpage = 1
            nextpage = page+1 if page < maxpage else ""
            for link in links:
                resp = self.__session.request(
                    method="GET",
                    url=link,
                    timeout=60,
                    proxies=proxy,
                    headers=self.__headers,
                    **kwargs
                )
                status_code = resp.status_code
                content = resp.content
                if status_code == 200:
                    html = content.decode("utf-8")
                    div = self.__parser.pyq_parser(
                        html,
                        'div[class="content"] div[id="article"]'
                    )
                    title = (
                        self.__parser.pyq_parser(
                            div,
                            'h1[class="f50 black2 f400 crimson"]'
                        )
                        .text()
                    )
                    newstime = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="mt10"] time[class="grey"]'
                        )
                        .text()
                    )
                    newstime = re.search(r'(\d{2}):(\d{2})', newstime)
                    if newstime:
                        hour = newstime.group(1)
                        minute = newstime.group(2)
                    else:
                        hour = "00"
                        minute = "00"
                    pubhour = f"{year}{month}{date}{hour}"
                    pubminute = f"{year}{month}{date}{hour}{minute}"
                    pubyear = year
                    pubday = f"{year}{month}{date}"
                    created_at = (
                        datetime
                        .strptime(
                            pubminute,
                            "%Y%m%d%H%M"
                        )
                        .strftime("%Y-%m-%dT%H:%M:00")
                    )
                    timezone = Utility.timezone(
                        date_time=pubminute,
                        format="%Y%m%d%H%M"
                    )
                    crawling_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    id = Utility.hashmd5(url=link)
                    lang = (
                        self.__parser.pyq_parser(
                            html,
                            'html'
                        )
                        .attr("lang")
                        [:2]
                    )
                    source = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="side-article mb5"] div[class="sources mb20"] h6 div a'
                        )
                        .attr("title")
                    )
                    if source:
                        source = source
                    else:
                        source = (
                            re.match(
                                r'https?://(www\.)?([^/]+)', link
                            )
                            .group(2)
                        )
                    author = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="credit mt10"] div[id="penulis"] a'
                        )
                        .text()
                    )
                    editor = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="credit mt10"] div[id="editor"] a'
                        )
                        .text()
                    )
                    image = (
                        self.__parser.pyq_parser(
                            html,
                            'div[id="artimg"] div[class="ovh imgfull_div"] a[class="icon_zoom glightbox"]'
                        )
                        .attr("href")
                    )
                    body_article = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="side-article txt-article multi-fontsize"] '
                        )
                        .remove("script")
                        .remove("strong")
                        .remove("div")
                        .remove("figcaption")
                        .text()
                    )
                    body_article = (
                        body_article
                        .replace("\n", " ")
                        .lstrip("-")
                        .lstrip("\u2013")
                        .lstrip()
                    )
                    desc = f"{body_article[:100]}..."
                    tags = []
                    for tag in self.__parser.pyq_parser(
                        html,
                        'div[class="side-article mb5"] div[itemprop="keywords"] h5[class="tagcloud3"]'
                    ):
                        tag_article = (
                            self.__parser.pyq_parser(
                                tag,
                                'a[class="rd2"]'
                            )
                            .text()
                        )
                        tags.append(tag_article)
                    data = {
                        "id": id,
                        "title": title,
                        "link": link,
                        "thumbnail_link": image,
                        "created_at": created_at,
                        "source": source,
                        "pub_year": pubyear,
                        "pub_day": pubday,
                        "pub_hour": pubhour,
                        "pub_minute": pubminute,
                        "lang": lang,
                        "editor": editor,
                        "author": author,
                        "content": body_article,
                        "desc": desc,
                        "hashtags": tags,
                        "time_zone": timezone,
                        "crawling_date": crawling_date
                    }
                    datas.append(data)
                else:
                    raise HTTPErrorException(
                        f"Error! status code {resp.status_code} : {resp.reason}"
                    )
            result = {
                "result": datas,
                "nextpage": nextpage
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )

    def newsArchive(
            self,
            page: int,
            year: int | str,
            month: Optional[int | str] = None,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:

        user_agent = self.__fake.user_agent()

        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page

        month = f"/{month}" if month else ""

        url = f"https://www.tribunnews.com/{year}{month}?page={page}"
        self.__headers["User-Agent"] = user_agent
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            datas = []
            html = content.decode("utf-8")
            links = []
            for li in self.__parser.pyq_parser(
                html,
                'div[class="lsi pt10 pb10"] ul li[class="ptb15"]'
            ):
                article_link = (
                    self.__parser.pyq_parser(
                        li,
                        'h3[class="fbo f16"] a'
                    )
                    .attr("href")
                )
                article_link = f"{article_link}?page=all"
                links.append(article_link)
            maxpage = (
                self.__parser.pyq_parser(
                    html,
                    'div[id="paginga"] div[class="paging"] a'
                )
                .eq(-1)
                .attr("href")
            )
            pagematch = re.search(r'page=(\d+)', maxpage)
            if pagematch:
                maxpage = int(pagematch.group(1))
            else:
                maxpage = 1
            nextpage = page+1 if page < maxpage else ""
            for link in links:
                resp = self.__session.request(
                    method="GET",
                    url=link,
                    timeout=60,
                    proxies=proxy,
                    headers=self.__headers,
                    **kwargs
                )
                status_code = resp.status_code
                content = resp.content
                if status_code == 200:
                    html = content.decode("utf-8")
                    div = self.__parser.pyq_parser(
                        html,
                        'div[class="content"] div[id="article"]'
                    )
                    title = (
                        self.__parser.pyq_parser(
                            div,
                            'h1[class="f50 black2 f400 crimson"]'
                        )
                        .text()
                    )
                    newsdate = (
                        re.search(r'/(\d{4}/\d{2}/\d{2})/', link)
                        .group(1)
                        .replace("/", "")
                    )
                    newstime = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="mt10"] time[class="grey"]'
                        )
                        .text()
                    )
                    newstime = re.search(r'(\d{2}):(\d{2})', newstime)
                    if newstime:
                        hour = newstime.group(1)
                        minute = newstime.group(2)
                    else:
                        hour = "00"
                        minute = "00"
                    pubhour = f"{newsdate}{hour}"
                    pubminute = f"{newsdate}{hour}{minute}"
                    pubyear = year
                    pubday = newsdate
                    created_at = (
                        datetime
                        .strptime(
                            pubminute,
                            "%Y%m%d%H%M"
                        )
                        .strftime("%Y-%m-%dT%H:%M:00")
                    )
                    timezone = Utility.timezone(
                        date_time=pubminute,
                        format="%Y%m%d%H%M"
                    )
                    crawling_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    id = Utility.hashmd5(url=link)
                    lang = (
                        self.__parser.pyq_parser(
                            html,
                            'html'
                        )
                        .attr("lang")
                        [:2]
                    )
                    source = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="side-article mb5"] div[class="sources mb20"] h6 div a'
                        )
                        .attr("title")
                    )
                    if source:
                        source = source
                    else:
                        source = (
                            re.match(
                                r'https?://(www\.)?([^/]+)', link
                            )
                            .group(2)
                        )
                    author = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="credit mt10"] div[id="penulis"] a'
                        )
                        .text()
                    )
                    editor = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="credit mt10"] div[id="editor"] a'
                        )
                        .text()
                    )
                    image = (
                        self.__parser.pyq_parser(
                            html,
                            'div[id="artimg"] div[class="ovh imgfull_div"] a[class="icon_zoom glightbox"]'
                        )
                        .attr("href")
                    )
                    body_article = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="side-article txt-article multi-fontsize"] '
                        )
                        .remove("script")
                        .remove("strong")
                        .remove("div")
                        .remove("figcaption")
                        .text()
                    )
                    body_article = (
                        body_article
                        .replace("\n", " ")
                        .lstrip("-")
                        .lstrip("\u2013")
                        .lstrip()
                    )
                    desc = f"{body_article[:100]}..."
                    tags = []
                    for tag in self.__parser.pyq_parser(
                        html,
                        'div[class="side-article mb5"] div[itemprop="keywords"] h5[class="tagcloud3"]'
                    ):
                        tag_article = (
                            self.__parser.pyq_parser(
                                tag,
                                'a[class="rd2"]'
                            )
                            .text()
                        )
                        tags.append(tag_article)
                    data = {
                        "id": id,
                        "title": title,
                        "link": link,
                        "thumbnail_link": image,
                        "created_at": created_at,
                        "source": source,
                        "pub_year": pubyear,
                        "pub_day": pubday,
                        "pub_hour": pubhour,
                        "pub_minute": pubminute,
                        "lang": lang,
                        "editor": editor,
                        "author": author,
                        "content": body_article,
                        "desc": desc,
                        "hashtags": tags,
                        "time_zone": timezone,
                        "crawling_date": crawling_date
                    }
                    datas.append(data)
                else:
                    raise HTTPErrorException(
                        f"Error! status code {resp.status_code} : {resp.reason}"
                    )
            result = {
                "result": datas,
                "nextpage": nextpage
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


if __name__ == "__main__":
    sb = NewsIndexArsip()
