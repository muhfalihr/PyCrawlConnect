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


class Search:
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

    def __set_search_by(self, search_by):
        search_by = search_by[0] + "." if search_by != "all" else ""
        return search_by

    def search(
        self,
        keyword: str,
        search_by: str,
        start_index: str | int,
        proxy: Optional[str] = None,
        **kwargs
    ) -> dict:

        user_agent = self.fake.user_agent()

        keyword = keyword.replace(" ", "+")
        search_by = self.__set_search_by(search_by)

        url = f"https://www.gutenberg.org/ebooks/search/?query={search_by}{keyword}&submit_search=Search&start_index={start_index}"

        self.headers["user-agent"] = user_agent
        r = self.session.request(
            "GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.headers,
            **kwargs,
        )
        status_code = r.status_code
        data = r.content
        if status_code == 200:
            datas = []
            html = data.decode("utf-8")
            try:
                next_start_index = self.parser.pyq_parser(
                    html,
                    'li[class="statusline"] [title="Go to the next page of results."]',
                ).attr("href")
                next_start_index = re.sub(
                    ".*start_index=", "", next_start_index)
            except:
                next_start_index = ""

            books = self.parser.pyq_parser(html, '[class="booklink"]')
            for book in books:
                book_link = "https://www.gutenberg.org{}".format(
                    self.parser.pyq_parser(book, "a").attr("href")
                )
                r = self.session.request(
                    "GET",
                    url=book_link,
                    timeout=60,
                    proxies=proxy,
                    headers=self.headers,
                    **kwargs,
                )
                status_code = r.status_code
                data = r.content
                if status_code == 200:
                    data_detail = self.parser.pyq_parser(
                        data, '[class="bibrec"]')
                    res = {}
                    list_same_header = []
                    for tr in self.parser.pyq_parser(data_detail, "tr"):
                        header = (
                            self.parser.pyq_parser(tr, f"th")
                            .text()
                            .lower()
                            .replace(" ", "_")
                        )
                        value = self.parser.pyq_parser(tr, f"td").text()
                        if header in res and header not in list_same_header:
                            temp = res[header]
                            res[header] = []
                            res[header].append(temp)
                            res[header].append(value)
                            list_same_header.append(header)
                        elif header in res:
                            res[header].append(value)
                        else:
                            res[header] = value

                        if header == "loc class":
                            value = value.split(",")
                            value = [x.strip(" ") for x in value]
                            res[header] = value

                    download_url = self.parser.pyq_parser(
                        data, '[class="files"] [content="application/pdf"] a'
                    ).attr("href")
                    if download_url == None:
                        download_url = self.parser.pyq_parser(
                            data, '[class="files"] [content="application/epub+zip"] a'
                        ).attr("href")

                    res["download_url"] = "https://www.gutenberg.org{}".format(
                        download_url
                    )
                    res["book_url"] = book_link
                    res.pop("")
                    datas.append(res)
                else:
                    raise HTTPErrorException(
                        f"Error! status code {r.status_code} : {r.reason}"
                    )

            result = {
                "result": datas,
                "next_start_index": next_start_index,
            }
            return result
        else:
            raise HTTPErrorException(f"Error! status code {r.status_code} : {r.reason}"
                                     )


if __name__ == "__main__":
    sb = Search()
