import requests
import re
import json
import random
import string

from pyquery import PyQuery
from urllib.parse import urljoin, urlencode
from faker import Faker
from helper.html_parser import HtmlParser
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

    def search(self, keyword: str, limit: int, page: int, proxy: Optional[str] = None, **kwargs) -> dict:
        user_agent = self.__fake.user_agent()

        keyword = keyword.replace(" ", "+")
        limit = int(limit)

        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page

        offset = limit * (page-1) if page > 1 else 0

        url = f"https://en.wikibooks.org/w/index.php?limit={limit}&offset={offset}&profile=default&search={keyword}&title=Special:Search&ns0=1&ns4=1&ns102=1&ns110=1&ns112=1"

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
            maxpage = (
                self.__parser.pyq_parser(
                    html,
                    '[id="mw-search-top-table"] [class="results-info"]'
                )
                .attr('data-mw-num-results-total')
            )
            maxpage = int(maxpage) // limit
            nextpage = page+1 if page < maxpage else ""
            div = self.__parser.pyq_parser(
                html,
                '[class="mw-search-results-container"] [class="mw-search-results"] [class="mw-search-result mw-search-result-ns-0"]'
            )

            links = []
            for a in div:
                link = (
                    self.__parser.pyq_parser(
                        a,
                        'a'
                    )
                    .attr('href')
                )
                links.append(f"https://en.wikibooks.org{link}")

            ids = [
                re.search(r'\/wiki\/(.+)', id).group(1)
                for id in links
            ]

            titles = []
            for a in div:
                title = (
                    self.__parser.pyq_parser(
                        a,
                        'a'
                    )
                    .text()
                )
                titles.append(title)
            for title, id, link in zip(titles, ids, links):
                data = {
                    "title": title,
                    "id": id,
                    "link": link
                }
                datas.append(data)
            result = {
                "result": datas,
                "nextpage": nextpage
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


class DepartementEnum(Search):
    def __init__(self):
        super().__init__()

    def departementenum(self, proxy: Optional[str] = None, **kwargs) -> dict:
        user_agent = self.__fake.user_agent()

        url = "https://en.wikibooks.org/wiki/Main_Page"
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
            html = content.decode('utf-8')
            departements = []
            div = self.__parser.pyq_parser(
                html,
                'div[style="flex: 1 0 50%; width:50%; min-width:10em; float: right; box-sizing: border-box; font-size:95%; display: flex; flex-wrap: wrap;"] div[style="float:left; width:25%; flex: 1 0 25%; min-width: 12em;"] li'
            )
            for a in div:
                dep = (
                    self.__parser.pyq_parser(
                        a,
                        'a'
                    )
                    .attr('href')
                )
                departements.append(dep)
            departements = [
                re.search(r'\:(.+)', d).group(1)
                for d in departements[:-2]
            ]
            return departements
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


class FeaturedBooks(Search):
    def __init__(self):
        super().__init__()

    def featuredbooks(self, departement: str, proxy: Optional[str] = None, **kwargs):
        user_agent = self.__fake.user_agent()

        url = f"https://en.wikibooks.org/wiki/Department:{departement}"
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
            links = []
            div = self.__parser.pyq_parser(
                html,
                'td[style="vertical-align:top; height:1%; padding:0em 0.5em 0.2em 0.5em; width:50%;"] ul li'
            )
            for a in div:
                link = (
                    self.__parser.pyq_parser(
                        a,
                        'a'
                    )
                    .attr('href')
                )
                links.append(f"https://en.wikibooks.org{link}")
            titles = []
            for a in div:
                title = (
                    self.__parser.pyq_parser(
                        a,
                        'a'
                    )
                    .text()
                )
                titles.append(title)
            ids = [
                re.search(r'\/wiki\/(.+)', id).group(1)
                for id in links
            ]
            for title, id, link in zip(titles, ids, links):
                data = {
                    "title": title,
                    "id": id,
                    "link": link
                }
                datas.append(data)
            result = {
                "result": datas
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


if __name__ == "__main__":
    sb = Search()
    fb = FeaturedBooks()
    dp = DepartementEnum()
