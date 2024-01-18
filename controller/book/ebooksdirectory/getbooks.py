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


class GetBooks:
    def __init__(self):
        self.session = requests.session()
        self.fake = Faker()
        self.parser = HtmlParser()

        self.headers = dict()
        self.headers["Accept"] = "application/json, text/plain, */*"
        self.headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.headers["Sec-Fetch-Dest"] = "empty"
        self.headers["Sec-Fetch-Mode"] = "cors"
        self.headers["Sec-Fetch-Site"] = "same-site"

    def getbooks(
            self,
            option: str,
            id: Optional[str] = None,
            page: Optional[int] = 1,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:

        user_agent = self.fake.user_agent()

        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page

        self.headers["User-Agent"] = user_agent
        match option:
            case 'categories':
                url = f'http://www.e-booksdirectory.com/listing.php?category={id}'
                resp = self.session.request(
                    method="GET",
                    url=url,
                    timeout=60,
                    proxies=proxy,
                    headers=self.headers,
                    **kwargs
                )
                status_code = resp.status_code
                content = resp.content
                if status_code == 200:
                    datas = []
                    html = content.decode('utf-8')
                    links = []
                    tag_a = self.parser.pyq_parser(
                        html,
                        '[class="dir_books"] [class="img_list"] a'
                    )
                    for link in tag_a:
                        a = (
                            self.parser.pyq_parser(
                                link,
                                'a'
                            )
                            .attr('href')
                        )
                        links.append(f"http://www.e-booksdirectory.com/{a}")

                    for link in links:
                        resp = self.session.request(
                            method="GET",
                            url=link,
                            timeout=60,
                            proxies=proxy,
                            headers=self.headers,
                            **kwargs
                        )
                        status_code = resp.status_code
                        content = resp.content
                        if status_code == 200:
                            html = content.decode('utf-8')
                            data_id = Utility.hashmd5(url=link)
                            detail_book = self.parser.pyq_parser(
                                html,
                                'article[itemtype="http://schema.org/Book"] p'
                            )
                            title = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'strong[itemprop="name"]'
                                )
                                .text()
                            )
                            img = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'img[itemprop="image"]'
                                )
                                .attr('src')
                            )
                            img = f"http://www.e-booksdirectory.com/{img}"
                            author = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="author"]'
                                )
                                .text()
                            )
                            publisher = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="publisher"] span[itemprop="name"]'
                                )
                                .text()
                            )
                            datePublished = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="datePublished"]'
                                )
                                .text()
                            )
                            isbnasin = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="isbn"]'
                                )
                                .eq(0)
                                .text()
                            )
                            isbn13 = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="isbn"]'
                                )
                                .eq(1)
                                .text()
                            )
                            numpage = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="numberOfPages"]'
                                )
                                .text()
                            )
                            desc = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="description"]'
                                )
                                .text()
                            )
                            originsite = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'a[target="_blank"]'
                                )
                                .eq(1)
                                .attr('href')
                            )
                            originsite_h = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'a[target="_blank"]'
                                )
                                .eq(0)
                                .attr('href')
                            )
                            originsite = originsite if originsite != None else originsite_h if originsite_h != None else ""

                            data = {
                                "id": data_id,
                                "url": link,
                                "title": title,
                                "thumbnail_url": img,
                                "author": author,
                                "publisher": publisher,
                                "date_published": datePublished,
                                "number_of_page": numpage,
                                "isbn/asin": isbnasin,
                                "isbn-13": isbn13,
                                "description": desc,
                                "original_site": originsite
                            }
                            datas.append(data)
                        else:
                            raise HTTPErrorException(
                                f"Error! status code {resp.status_code} : {resp.reason}"
                            )
                    result = {
                        "result": datas
                    }
                    return result
                else:
                    raise HTTPErrorException(
                        f"Error! status code {resp.status_code} : {resp.reason}"
                    )

            case 'new' | 'top20' | 'popular':
                url = f'http://www.e-booksdirectory.com/{option}.php'
                resp = self.session.request(
                    method="GET",
                    url=url,
                    timeout=60,
                    proxies=proxy,
                    headers=self.headers,
                    **kwargs
                )
                status_code1 = resp.status_code
                content1 = resp.content
                if status_code1 == 200:
                    datas = []
                    html1 = content1.decode('utf-8')
                    maxpage = (
                        self.parser.pyq_parser(
                            html1,
                            'input[value="Next"]'
                        )
                        .attr('value')
                    )
                    nextpage = page+1 if maxpage != None else ""

                    links = []
                    if page == 1:
                        tag_a1 = self.parser.pyq_parser(
                            html1,
                            '[class="img_list"] a'
                        )
                        for link in tag_a1:
                            a = (
                                self.parser.pyq_parser(
                                    link,
                                    'a'
                                )
                                .attr('href')
                            )
                            links.append(
                                f"http://www.e-booksdirectory.com/{a}")
                    elif page > 1:
                        num = 0
                        for i in range(page-1):
                            data = {
                                "submit": "Next",
                                "startid": f"{0+num}"
                            }
                            resp = self.session.post(
                                url=url,
                                timeout=60,
                                proxies=proxy,
                                headers=self.headers,
                                data=data,
                                **kwargs
                            )
                            status_code2 = resp.status_code
                            content2 = resp.content
                            num += 20
                        if status_code2 == 200:
                            html2 = content2.decode('utf-8')
                            tag_a2 = self.parser.pyq_parser(
                                html2,
                                '[class="img_list"] a'
                            )
                            for link in tag_a2:
                                a = (
                                    self.parser.pyq_parser(
                                        link,
                                        'a'
                                    )
                                    .attr('href')
                                )
                                links.append(
                                    f"http://www.e-booksdirectory.com/{a}")
                        else:
                            raise HTTPErrorException(
                                f"Error! status code {resp.status_code} : {resp.reason}"
                            )

                    for link in links:
                        resp = self.session.request(
                            method="GET",
                            url=link,
                            timeout=60,
                            proxies=proxy,
                            headers=self.headers,
                            **kwargs
                        )
                        status_code = resp.status_code
                        content = resp.content
                        if status_code == 200:
                            html = content.decode('utf-8')
                            data_id = Utility.hashmd5(url=link)
                            detail_book = self.parser.pyq_parser(
                                html,
                                'article[itemtype="http://schema.org/Book"] p'
                            )
                            title = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'strong[itemprop="name"]'
                                )
                                .text()
                            )
                            img = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'img[itemprop="image"]'
                                )
                                .attr('src')
                            )
                            img = f"http://www.e-booksdirectory.com/{img}"
                            author = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="author"]'
                                )
                                .text()
                            )
                            publisher = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="publisher"] span[itemprop="name"]'
                                )
                                .text()
                            )
                            datePublished = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="datePublished"]'
                                )
                                .text()
                            )
                            isbnasin = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="isbn"]'
                                )
                                .eq(0)
                                .text()
                            )
                            isbn13 = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="isbn"]'
                                )
                                .eq(1)
                                .text()
                            )
                            numpage = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="numberOfPages"]'
                                )
                                .text()
                            )
                            desc = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'span[itemprop="description"]'
                                )
                                .text()
                            )
                            originsite = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'a[target="_blank"]'
                                )
                                .eq(1)
                                .attr('href')
                            )
                            originsite_h = (
                                self.parser.pyq_parser(
                                    detail_book,
                                    'a[target="_blank"]'
                                )
                                .eq(0)
                                .attr('href')
                            )
                            originsite = originsite if originsite != None\
                                else originsite_h if originsite_h != None else ""

                            data = {
                                "id": data_id,
                                "url": link,
                                "title": title,
                                "thumbnail_url": img,
                                "author": author,
                                "publisher": publisher,
                                "date_published": datePublished,
                                "number_of_page": numpage,
                                "isbn/asin": isbnasin,
                                "isbn-13": isbn13,
                                "description": desc,
                                "original_site": originsite
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
            case _:
                url = ""
                raise HTTPErrorException(
                    f"Error! status code {resp.status_code} : {resp.reason}"
                )


if __name__ == "__main__":
    gb = GetBooks()
