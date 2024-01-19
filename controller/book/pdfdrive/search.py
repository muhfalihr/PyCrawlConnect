import requests
import re
import json
import random
import string

from pyquery import PyQuery
from urllib.parse import urljoin, urlencode
from faker import Faker
from helper.html_parser import HtmlParser
from helper.utility import Utility
from typing import Any, Optional
from helper.exception import *


class Search:
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

    def search(
            self,
            keyword: Optional[str] = None,
            page: Optional[int] = 1,
            pub_year: Optional[str] = "Pub. Year",
            pagecount: Optional[str] = "Any Pages",
            lang: Optional[str] = None,
            em: Optional[bool] = False,
            iscategory: Optional[bool] = False,
            idcat: Optional[str] = None,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:

        user_agent = self.__fake.user_agent()

        pub_year = "" if pub_year == "Pub. Year" else re.search(
            r'\d+', pub_year
        ).group()

        keyword = keyword.replace(" ", "+") if keyword != None else ""

        pagecount = "" if pagecount == "Any Pages" else pagecount.replace(
            "+", "-*"
        )

        lang = ""
        em = 0 if em == "false" or False else 1

        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page

        match iscategory:
            case False:
                url = f"https://www.pdfdrive.com/search?q={keyword}&pagecount={pagecount}&pubyear={pub_year}&searchin={lang}&em={em}&page={page}"
            case True:
                url = f"https://www.pdfdrive.com/category/{idcat}/p{page}/"

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
            html = content.decode('utf-8')
            page_list = []
            tag_li = self.__parser.pyq_parser(
                html,
                '[class="pagination"] [class="Zebra_Pagination"] ul li'
            )
            for li in tag_li:
                p = (
                    self.__parser.pyq_parser(
                        li,
                        'li'
                    )
                    .text()
                )
                page_list.append(p)
            maxpage = int(page_list[-2]) if page_list != [] else 1
            nextpage = page+1 if page < maxpage else ""
            div = self.__parser.pyq_parser(
                html,
                '[class="files-new"] ul li'
            )
            links = []
            for a in div:
                link = (
                    self.__parser.pyq_parser(
                        a,
                        'div[class="file-right"] a'
                    )
                    .attr('href')
                )
                links.append(f"https://www.pdfdrive.com{link}")
            links = list(
                filter(lambda x: x != "https://www.pdfdrive.comNone", links))
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
                    html = content.decode('utf-8')
                    id = Utility.hashmd5(url=link)
                    div = self.__parser.pyq_parser(
                        html,
                        'div[class="ebook-main"]'
                    )
                    img = (
                        self.__parser.pyq_parser(
                            div,
                            'img[class="ebook-img"]'
                        )
                        .attr('src')
                    )
                    title = (
                        self.__parser.pyq_parser(
                            div,
                            'h1[itemprop="name"]'
                        )
                        .text()
                    )
                    author = (
                        self.__parser.pyq_parser(
                            div,
                            'div[class="ebook-author"] span[itemprop="creator"]'
                        )
                        .text()
                    )
                    info = self.__parser.pyq_parser(
                        div,
                        'div[class="ebook-file-info"] span[class="info-green"]'
                    )
                    countpage = info.eq(0).text()
                    pubyear = info.eq(1).text()
                    filesize = info.eq(2).text()
                    language = info.eq(3).text()
                    tags = []
                    tag_div = self.__parser.pyq_parser(
                        div,
                        'div[class="ebook-tags"] a'
                    )
                    for a in tag_div:
                        tag = (
                            self.__parser.pyq_parser(
                                a,
                                'a'
                            )
                            .text()
                        )
                        tags.append(tag)
                    downloadsite = (
                        self.__parser.pyq_parser(
                            div,
                            'span[id="download-button"] a[id="download-button-link"]'
                        )
                        .attr('href')
                    )
                    downloadsite = f"https://www.pdfdrive.com{downloadsite}#top"
                    data = {
                        "id": id,
                        "url": link,
                        "title": title,
                        "thumbnail_link": img,
                        "author": author,
                        "count_page": countpage,
                        "pub_year": pubyear,
                        "tags": tags,
                        "file_size": filesize,
                        "language": language,
                        "download_link": downloadsite
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
    sb = Search()
