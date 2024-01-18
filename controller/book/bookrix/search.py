import requests
import re
import json
import random
import string

from pyquery import PyQuery
from requests.cookies import RequestsCookieJar
from requests.exceptions import Timeout, ReadTimeout
from urllib.parse import urljoin, urlencode
from faker import Faker
from typing import Any, Optional
from helper.html_parser import HtmlParser
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
            keyword: Optional[str] = "",
            page: Optional[int] = 1,
            proxy: Optional[str] = None,
            cookies: Optional[str] = None,
            **kwargs
    ) -> dict:

        user_agent = self.__fake.user_agent()

        keyword = keyword.replace(" ", "%20")
        url = f"https://www.bookrix.com/search;keywords:{keyword},searchoption:books,page:{page}.html"

        self.__headers["user-agent"] = user_agent
        r = self.__session.request(
            "GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            cookies=cookies,
            **kwargs,
        )
        status_code = r.status_code
        data = r.content
        if status_code == 200:
            datas = []
            html = data.decode("utf-8")
            try:
                next_page = self.__parser.pyq_parser(html, 'li[class="next"] a').attr(
                    "href"
                )
                next_page = re.sub(".*page:", "", next_page)
                next_page = re.sub(".html", "", next_page)
            except:
                next_page = ""

            data = self.__parser.pyq_parser(
                html, '[class="listView books"] [class="item"]'
            )
            for div in data:
                bookID = self.__parser.pyq_parser(div, "img").attr("src")
                bookID = re.sub(".*p=", "", bookID)
                title = self.__parser.pyq_parser(
                    div, '[class="item-title"]').text()
                links = self.__parser.pyq_parser(div, "a").attr("href")
                links = f"https://www.bookrix.com{links}"
                author = self.__parser.pyq_parser(
                    div, '[class="item-author"]').text()
                genre = self.__parser.pyq_parser(
                    div, '[class="item-details"] li:nth-child(1)'
                ).text()
                language = self.__parser.pyq_parser(
                    div, '[class="item-details"] li:nth-child(2)'
                ).text()
                count_words = self.__parser.pyq_parser(
                    div, '[class="item-details"] li:nth-child(3)'
                ).text()
                rating = self.__parser.pyq_parser(
                    div, '[class="item-details"] li:nth-child(4)'
                ).text()
                views = self.__parser.pyq_parser(
                    div, '[class="item-details"] li:nth-child(5)'
                ).text()
                favorites = self.__parser.pyq_parser(
                    div, '[class="item-details"] li:nth-child(6)'
                ).text()
                description = self.__parser.pyq_parser(
                    div, '[class="item-description hyphenate"]'
                ).text()
                keywords = []
                for k in self.__parser.pyq_parser(div, '[class="item-keywords"] a'):
                    key = self.__parser.pyq_parser(k, "a").text()
                    keywords.append(key)
                price = self.__parser.pyq_parser(
                    div, '[class="item-price"]').text()
                data = {
                    "bookID": bookID,
                    "title": title,
                    "url": links,
                    "author": author,
                    "genre": genre,
                    "language": language,
                    "count_words": count_words,
                    "rating": rating,
                    "views": int(views),
                    "favorites": int(favorites),
                    "description": description,
                    "keywords": keywords,
                    "price": price,
                }
                datas.append(data)
            result = {
                "result": datas,
                "next_page": next_page,
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {r.status_code} : {r.reason}"
            )


if __name__ == "__main__":
    sb = Search()
