import requests
import re
import json
import random
import string

from pyquery import PyQuery
from urllib.parse import urljoin, urlencode
from faker import Faker
from typing import Any, Optional
from helper.html_parser import HtmlParser
from helper.exception import *


class Categories:
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

    def categories(self, proxy: Optional[str] = None, **kwargs):
        user_agent = self.__fake.user_agent()

        url = "https://www.pdfdrive.com/"
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
            div = self.__parser.pyq_parser(
                html,
                'div[class="categories-list"] ul li a'
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
                links.append(f"https://www.pdfdrive.com{link}")
            categories = []
            for p in div:
                cat = (
                    self.__parser.pyq_parser(
                        p,
                        'a p'
                    )
                    .text()
                )
                categories.append(cat)
            links2 = []
            categories2 = []
            for url in links:
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
                    html2 = content.decode('utf-8')
                    div2 = self.__parser.pyq_parser(
                        html2,
                        'div[class="categories-list subcategories-list mt-4"] ul li a'
                    )
                    if div2:
                        for a2 in div2:
                            link2 = (
                                self.__parser.pyq_parser(
                                    a2,
                                    'a'
                                )
                                .attr('href')
                            )
                            links2.append(f"https://www.pdfdrive.com{link2}")
                        for p2 in div2:
                            cat2 = (
                                self.__parser.pyq_parser(
                                    p2,
                                    'a p'
                                )
                                .text()
                            )
                            categories2.append(cat2)
                    else:
                        pass
                else:
                    raise Exception(
                        f"Error! status code {resp.status_code} : {resp.reason}")
            links.extend(links2)
            categories.extend(categories2)
            ids = [
                re.search(r'/category/(\d+)', id).group(1)
                for id in links
            ]
            for link, cat, id in zip(links, categories, ids):
                data = {
                    "category": cat,
                    "id": id,
                    "link": link
                }
                datas.append(data)
            return datas
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


if __name__ == "__main__":
    cat = Categories()
