import requests
import re
import json
import random
import string
import time

from pyquery import PyQuery
from requests.cookies import RequestsCookieJar
from requests.exceptions import Timeout, ReadTimeout
from urllib.parse import urljoin, urlencode
from faker import Faker
from datetime import datetime
from helper.html_parser import HtmlParser
from helper.utility import Utility


class Index:
    def __init__(self):
        self.session = requests.session()
        self.jar = RequestsCookieJar()
        self.fake = Faker()
        self.parser = HtmlParser()
        self.utility = Utility()

        self.headers = dict()
        self.headers["Accept"] = "application/json, text/plain, */*"
        self.headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.headers["Sec-Fetch-Dest"] = "empty"
        self.headers["Sec-Fetch-Mode"] = "cors"
        self.headers["Sec-Fetch-Site"] = "same-site"

    def set_cookies(self, cookies):
        for cookie in cookies:
            if cookie["name"] == "msToken":
                msToken = cookie["value"]
            self.jar.set(
                cookie["name"],
                cookie["value"],
                domain=cookie["domain"],
                path=cookie["path"],
            )
        return self.jar

    def newsIndex(self, page, year, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.set_cookies(cookies=cookies)
        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page
        url = f"https://www.suara.com/indeks/terkini/news/{year}?page={page}"
        self.headers["User-Agent"] = user_agent
        resp = self.session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.headers,
            cookies=cookies,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            datas = []
            html = content.decode("utf-8")
            links = []
            for item in self.parser.pyq_parser(
                html,
                'div[class="base-content"] div[class="content mb-30 static"] div[class="list-item-y-img-retangle"] div[class="item"]'
            ):
                article_link = (
                    self.parser.pyq_parser(
                        item,
                        'div[class="item"] div[class="text-list-item-y"] a'
                    )
                    .attr('href')
                )
                links.append(article_link)
            maxpage = (
                self.parser.pyq_parser(
                    html,
                    'ul[class="pagination"] li a'
                )
                .eq(-2)
                .text()
            )
            maxpage = int(maxpage) if maxpage.isdigit() else 1
            nextpage = page+1 if page < maxpage else ""
            for link in links:
                resp = self.session.request(
                    method="GET",
                    url=link,
                    timeout=60,
                    proxies=proxy,
                    headers=self.headers,
                    cookies=cookies,
                    **kwargs
                )
                status_code = resp.status_code
                content = resp.content
                if status_code == 200:
                    html = content.decode("utf-8")
                    title = (
                        self.parser.pyq_parser(
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
                    timezone = self.utility.timezone(
                        date_time=newsdatetime,
                        format="%Y%m%d%H%M%S"
                    )
                    crawling_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    id = self.utility.hashmd5(url=link)
                    lang = (
                        self.parser.pyq_parser(
                            html,
                            'html'
                        )
                        .attr("lang")
                        [:2]
                    )
                    source = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="info"] div[class="head-writer-date"] div[class="writer"] span a[class="colored"]'
                        )
                        .eq(-1)
                        .text()
                    )
                    author = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="info"] div[class="head-writer-date"] div[class="writer"] span'
                        )
                        .eq(0)
                        .text()
                    )
                    editor = author
                    reporter = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="info"] div[class="head-writer-date"] div[class="writer"] span'
                        )
                        .remove_class("colored")
                        .eq(1)
                        .text()
                    )
                    image = (
                        self.parser.pyq_parser(
                            html,
                            'figure[class="img-cover"] picture img'
                        )
                        .attr("src")
                    )
                    remove = (
                        self.parser.pyq_parser(
                            html,
                            'article[class="detail-content detail-berita"] p strong'
                        )
                        .eq(0)
                        .text()
                    )
                    body_article = (
                        self.parser.pyq_parser(
                            html,
                            'article[class="detail-content detail-berita"] p'
                        )
                        .text()
                        .lstrip(remove)
                    )
                    body_article = self.utility.UniqClear(body_article)
                    desc = f"{body_article[:100]}..."
                    tags = []
                    for li in self.parser.pyq_parser(
                        html,
                        'div[class="tag-header"] ul[class="list-tag"] li'
                    ):
                        tag = (
                            self.parser.pyq_parser(
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
                    raise Exception(
                        f"Error! status code {resp.status_code} : {resp.reason}")
            result = {
                "result": datas,
                "nextpage": nextpage
            }
            return result
            # results = json.dumps(result, indent=4)
            # try:
            #     with open("controller/news/suara/result.json", "w") as file:
            #         file.write(results)
            # except Exception:
            #     with open("controller/news/suara/result.json", "r+") as file:
            #         file.write(results)
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")


if __name__ == "__main__":
    cookies = []
    sb = Index()
    # cek = sb.newsIndex(page=1, year=2023)
    # print(cek)
