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


class Index:
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
            year: int | str,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:

        user_agent = self.__fake.user_agent()

        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page

        url = f"https://www.suara.com/indeks/terkini/news/{year}?page={page}"
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
            for item in self.__parser.pyq_parser(
                html,
                'div[class="base-content"] div[class="content mb-30 static"] div[class="list-item-y-img-retangle"] div[class="item"]'
            ):
                article_link = (
                    self.__parser.pyq_parser(
                        item,
                        'div[class="item"] div[class="text-list-item-y"] a'
                    )
                    .attr('href')
                )
                links.append(article_link)
            maxpage = (
                self.__parser.pyq_parser(
                    html,
                    'ul[class="pagination"] li a'
                )
                .eq(-2)
                .text()
            )
            maxpage = int(maxpage) if maxpage.isdigit() else 1
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
                    title = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="info"] h1'
                        )
                        .text()
                    )
                    newsdatetime = (
                        re.search(r'/(\d{4}/\d{2}/\d{2}/\d+)/', link)
                        .group(1)
                        .replace("/", "")
                    )
                    pubhour = newsdatetime[:-6]
                    pubminute = newsdatetime[:-4]
                    pubyear = newsdatetime[:4]
                    pubday = newsdatetime[:-8]
                    created_at = (
                        datetime
                        .strptime(newsdatetime, "%Y%m%d%H%M%S")
                        .strftime("%Y-%m-%dT%H:%M:%S")
                    )
                    timezone = Utility.timezone(
                        date_time=newsdatetime,
                        format="%Y%m%d%H%M%S"
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
                            'div[class="info"] div[class="head-writer-date"] div[class="writer"] span a[class="colored"]'
                        )
                        .eq(-1)
                        .text()
                    )
                    author = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="info"] div[class="head-writer-date"] div[class="writer"] span'
                        )
                        .eq(0)
                        .text()
                    )
                    editor = author
                    reporter = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="info"] div[class="head-writer-date"] div[class="writer"] span'
                        )
                        .remove_class("colored")
                        .eq(1)
                        .text()
                    )
                    image = (
                        self.__parser.pyq_parser(
                            html,
                            'figure[class="img-cover"] picture img'
                        )
                        .attr("src")
                    )
                    remove = (
                        self.__parser.pyq_parser(
                            html,
                            'article[class="detail-content detail-berita"] p strong'
                        )
                        .eq(0)
                        .text()
                    )
                    body_article = (
                        self.__parser.pyq_parser(
                            html,
                            'article[class="detail-content detail-berita"] p'
                        )
                        .text()
                        .lstrip(remove)
                    )
                    body_article = Utility.UniqClear(body_article)
                    desc = f"{body_article[:100]}..."
                    tags = []
                    for li in self.__parser.pyq_parser(
                        html,
                        'div[class="tag-header"] ul[class="list-tag"] li'
                    ):
                        tag = (
                            self.__parser.pyq_parser(
                                li,
                                'li a'
                            )
                            .attr("title")
                        )
                        tag = tag if tag else ""
                        tags.append(tag)
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
                        "reporter": reporter,
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
    sb = Index()
