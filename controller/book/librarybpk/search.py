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

    def __handle(self, field: str, s: str) -> list:
        try:
            var = [i for i in field.rstrip(';').split(s) if i != ""]
        except Exception:
            var = []
        finally:
            return var

    def __detailbook(self, parent, numdb, indexdb):
        detail = self.__parser.pyq_parser(
            parent.eq(numdb),
            'td'
        ).eq(indexdb).text()
        return detail

    def search(self, keyword: str, page: int, proxy: Optional[str] = None, **kwargs):

        user_agent = self.__fake.user_agent()

        keyword = keyword.replace(' ', '%20')
        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page

        url = f"https://library.bpk.go.id/search/keyword/{keyword}/{page}"
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
            data = self.__parser.pyq_parser(
                html,
                '[class="col-lg-9"] [class="row"] [class="col-lg-10"]'
            )
            pages = []
            for li in self.__parser.pyq_parser(
                html,
                'ul[class="pagination"] li'
            ):
                tag_a = self.__parser.pyq_parser(
                    li,
                    'a'
                ).text()
                pages.append(tag_a)
            maxpage = int(pages[-2])
            nextpage = page+1 if page < maxpage else ""

            links = []
            for div in data:
                link = self.__parser.pyq_parser(
                    div,
                    'div[class="col-lg-10"] a'
                ).attr('href')
                links.append(f"https://library.bpk.go.id{link}")
            for link in links:
                resp = self.__session.request(
                    method="GET",
                    url=link,
                    timeout=60,
                    proxies=proxy,
                    headers=self.__headers,
                    **kwargs
                )
                content = resp.content
                status_code = resp.status_code
                if status_code == 200:
                    html_detail = content.decode("utf-8")
                    id = Utility.hashmd5(url=link)
                    data_detail = self.__parser.pyq_parser(
                        html_detail,
                        'div[class="row"]'
                    )

                    img = self.__parser.pyq_parser(
                        data_detail,
                        'div[class="threecol"] img[class="centerimg"]'
                    ).attr('data-url')
                    title = self.__parser.pyq_parser(
                        data_detail,
                        '[class="first"] h2'
                    ).text()
                    details = self.__parser.pyq_parser(
                        data_detail,
                        'ul[class="price_features"] li'
                    )

                    value = self.__parser.pyq_parser(
                        data_detail,
                        'tbody tr'
                    )
                    values = []
                    for v in value:
                        x = self.__parser.pyq_parser(
                            v,
                            'td'
                        ).text()
                        values.append(x)
                    details = []
                    for i in range(len(values)):
                        detail = {
                            "number": self.__detailbook(value, i, 0),
                            "registration_number": self.__detailbook(value, i, 1),
                            "location": self.__detailbook(value, i, 2),
                            "status": self.__detailbook(value, i, 3)
                        }
                        details.append(detail)

                    li = self.__parser.pyq_parser(
                        data_detail,
                        'ul[class="price_features"] li span[class="right bold"]'
                    )
                    span = self.__parser.pyq_parser(
                        li,
                        'span[class="right bold"]'
                    )
                    authors = (self.__handle(span.eq(0).text(), ', '))
                    issue = (span.eq(1).text())
                    isbn = (span.eq(2).text())
                    callnumber = (span.eq(3).text())
                    language = (span.eq(4).text())
                    subjects = (self.__handle(span.eq(5).text(), '; '))

                    data = {
                        "id": id,
                        "url": link,
                        "title": title,
                        "thumbnail_link": str(img).replace('perpustakaan', 'library'),
                        "authors": authors,
                        "issue": issue,
                        "isbn": isbn,
                        "callnumber": callnumber,
                        "language": language,
                        "subjects": subjects,
                        "details": details
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
