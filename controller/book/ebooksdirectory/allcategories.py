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


class AllCategories:
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

    def allcategories(self, proxy: Optional[str] = None, **kwargs):

        user_agent = self.__fake.user_agent()

        url = 'http://www.e-booksdirectory.com'
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
            tag_a = self.__parser.pyq_parser(
                html,
                'article[class="main_categories"] table tr a'
            )
            for link in tag_a:
                a = (
                    self.__parser.pyq_parser(
                        link,
                        'a'
                    )
                    .attr('href')
                )
                links.append(f"http://www.e-booksdirectory.com/{a}")

            categories = []
            for name in tag_a:
                cn = (
                    self.__parser.pyq_parser(
                        name,
                        'a'
                    )
                    .text()
                )
                categories.append(cn)

            ids = [
                re.search(r'category=(\d+)', id).group(1)
                for id in links
            ]

            for link, category, id in zip(links, categories, ids):
                data = {
                    "id": id,
                    "category": category,
                    "url": link
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
    ac = AllCategories()
