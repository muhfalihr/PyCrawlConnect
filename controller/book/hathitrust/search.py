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
from helper.utility import Utility
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

    def __emptyarray(self, data: dict, grid: str):
        field = data.get(grid, [])
        field = [field] if isinstance(field, str) else field
        return field

    def search(
            self,
            keyword: str,
            category: str,
            page: int,
            pagesize: int,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:

        user_agent = self.__fake.user_agent()

        keyword = keyword.replace(" ", "+")

        page = int(page)
        page = page+1 if page == 0\
            else -page if '-' in str(page) else page

        match category:
            case 'all' | 'title' | 'author' | 'subject' | 'isn' | 'publisher' | 'seriestitle':
                url = f'https://catalog.hathitrust.org/Search/Home?type%5B%5D={category}&lookfor%5B%5D={keyword}&page={page}&pagesize={pagesize}'
            case 'full_text_and_all_fields':
                url = f'https://babel.hathitrust.org/cgi/ls?q1={keyword}&field1=ocr&a=srchls&ft=ft&lmt=ft&pn={page}'

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
            maxpage = (
                self.__parser.pyq_parser(
                    html,
                    'hathi-results-pagination'
                )
                .attr('data-prop-max-pages')
            )
            maxpage = int(maxpage)
            nextpage = page+1 if page < maxpage else ""

            data = self.__parser.pyq_parser(
                html=html,
                selector='[class="results-container"] [class="record d-flex gap-3 p-3 mb-3 mt-3 shadow-sm"]'
            )
            links = []
            for raw in data:
                link = (
                    self.__parser.pyq_parser(
                        raw,
                        '[class="list-group-item list-group-item-action w-sm-50"]'
                    )
                    .attr("href")
                )
                link = f"https://catalog.hathitrust.org/{link}"
                links.append(link)

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
                    data = self.__parser.pyq_parser(
                        html,
                        'article[class="record d-flex flex-column gap-3 p-3 mb-3 mt-3"]'
                    )
                    id = Utility.hashmd5(url=link)
                    for raw in data:
                        title = (
                            self.__parser.pyq_parser(
                                raw,
                                '[class="article-heading d-flex gap-3"]'
                            )
                            .text()
                            .replace("\n", "")
                        )
                        metadata = self.__parser.pyq_parser(
                            raw,
                            '[class="metadata"] [class="grid"]'
                        )
                        atag = self.__parser.pyq_parser(
                            raw,
                            '[class="grid"] [class="g-col-lg-8 g-col-12"] a[data-toggle="tracking"]'
                        )

                        alist = []
                        for a in atag:
                            origin_site = (
                                self.__parser.pyq_parser(
                                    a,
                                    'a'
                                )
                                .attr('href')
                            )
                            alist.append(origin_site)

                        data_grid = dict()

                        for grid in metadata:
                            key = (
                                self.__parser.pyq_parser(
                                    grid,
                                    '[class="g-col-lg-4 g-col-12"]'
                                )
                                .text()
                                .rstrip()
                                .lstrip()
                            )
                            key = re.sub(r'\(s\)', '', key)
                            value = self.__parser.pyq_parser(
                                grid,
                                '[class="g-col-lg-8 g-col-12"]'
                            )
                            value = re.sub(
                                r'>[^/]+/', '>',
                                value.text().rstrip().lstrip().replace('"', '')
                            )
                            data_grid[key] = value.split('\n')\
                                if '\n' in value else value
                        isbn = [
                            re.sub(r'\D', '', i)
                            for i in self.__emptyarray(
                                data_grid,
                                "ISBN"
                            )
                        ]
                        data = {
                            "id": id,
                            "url": link,
                            "title": title,
                            "description": {
                                "main_author": data_grid.get('Main Author', ""),
                                "related_names": self.__emptyarray(data_grid, "Related Names"),
                                "languages": data_grid.get('Language', ""),
                                "published": data_grid.get('Published', ""),
                                "edition": data_grid.get('Edition', ""),
                                "subjects": self.__emptyarray(data_grid, "Subjects"),
                                "summary": data_grid.get('Summary', ""),
                                "note": data_grid.get('Note', ""),
                                "isbn": isbn,
                                "physical_description": data_grid.get('Physical Description', ""),
                                "original_site": alist
                            }
                        }
                        datas.append(data)
                else:
                    raise HTTPErrorException(
                        f"Error! status code {resp.status_code} : {resp.reason}"
                    )
            result = {
                "result": datas,
                "next_page": nextpage
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


if __name__ == "__main__":
    sb = Search()
