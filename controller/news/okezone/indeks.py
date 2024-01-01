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

        self.headers = dict()
        self.headers["Accept"] = "application/json, text/plain, */*"
        self.headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.headers["Sec-Fetch-Dest"] = "empty"
        self.headers["Sec-Fetch-Mode"] = "cors"
        self.headers["Sec-Fetch-Site"] = "same-site"

    def __set_cookies(self, cookies):
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

    def __rmBracket(self, teks: str):
        endpoint = teks.rfind(".")
        endbracket = teks.rfind(")", endpoint)
        if endbracket > endpoint:
            result = teks[:endpoint+1]
        else:
            result = teks
        return result

    def newsIndex(self, site, page, year, month, date, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.__set_cookies(cookies=cookies)
        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page
        if site != "index":
            page = (page - 1) * 10 if page > 1 else ""
            url = f"https://{site}.okezone.com/indeks/{year}/{month}/{date}/{page}"
            page = page//10+1 if page != "" else 1 if page == "" else 1
            multiple = 10
        elif site == "index":
            page = (page - 1) * 15 if page > 1 else 0
            url = f"https://index.okezone.com/bydate/index/{year}/{month}/{date}/{page}/"
            page = page//15+1 if page != 0 else 1 if page == 0 else 1
            multiple = 15

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
            for li in self.parser.pyq_parser(
                html,
                'ul[class="list-berita"] div[class="news-content"] li'
            ):
                article_link = (
                    self.parser.pyq_parser(
                        li,
                        'li h4[class="f17"] a'
                    )
                    .attr("href")
                )
                links.append(article_link)
            if site != "index":
                maxpage = (
                    self.parser.pyq_parser(
                        html,
                        'div[class="pagination-komentar"] a'
                    )
                    .eq(-1)
                    .attr("href")
                )
                pagematch = re.search(r'/(\d+)$', str(maxpage))
            elif site == "index":
                maxpage = (
                    self.parser.pyq_parser(
                        html,
                        'div[class="pagination-indexs"] div[class="time r1 fl bg1 b1"] a'
                    )
                    .eq(-1)
                    .attr("href")
                )
                pagematch = re.search(r'/(\d+)/?$', str(maxpage))
            if pagematch:
                maxpage = int(pagematch.group(1))
                maxpage = maxpage//multiple+1
            else:
                maxpage = 1
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
                            'div[class="title"] h1'
                        )
                        .text()
                    )
                    newsdate = (
                        re.search(r'/(\d{4}/\d{2}/\d{2})/', link)
                        .group(1)
                        .replace("/", "")
                    )
                    newstime = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="reporter"] div[class="namerep"] b'
                        )
                        .text()
                    )
                    newstime = re.search(r'(\d{2}):(\d{2})', newstime)
                    if newstime:
                        hour = newstime.group(1)
                        minute = newstime.group(2)
                    else:
                        hour = "00"
                        minute = "00"
                    pubhour = f"{newsdate}{hour}"
                    pubminute = f"{newsdate}{hour}{minute}"
                    pubyear = year
                    pubday = newsdate
                    created_at = (
                        datetime
                        .strptime(
                            pubminute,
                            "%Y%m%d%H%M"
                        )
                        .strftime("%Y-%m-%dT%H:%M:00")
                    )
                    timezone = Utility.timezone(
                        date_time=pubminute,
                        format="%Y%m%d%H%M"
                    )
                    crawling_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    id = Utility.hashmd5(url=link)
                    lang = (
                        self.parser.pyq_parser(
                            html,
                            'html'
                        )
                        .attr("lang")
                        [:2]
                    )
                    source = re.search(r'https?://([^/]+)', link)
                    if source:
                        source = source.group(1)
                        sitenews = source.split(".")[0]
                    else:
                        source = "okezone.com"
                    author = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="reporter"] div[class="namerep"] a'
                        )
                        .text()
                    )
                    author = author if author != "" else (
                        self.parser.pyq_parser(
                            html,
                            'div[class="reporter clearfix"] div[class="namerep"] a'
                        )
                        .text()
                    )
                    script = str(
                        self.parser.pyq_parser(
                            html,
                            'head script'
                        )
                    )
                    match = re.search(r"'editor'\s*:\s*'([^']+)'", script)
                    if match:
                        editor = match.group(1)
                    else:
                        editor = ""
                    image = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="detfoto"] img[id="imgCheck"]'
                        )
                        .attr('src')
                    )
                    image = image if image else (
                        self.parser.pyq_parser(
                            html,
                            'div[id="article"] figure img[class="img lazy"]'
                        )
                        .attr("src")
                    )
                    rmtext1 = (
                        self.parser.pyq_parser(
                            html,
                            'div[id="contentx"] p[class="box-gnews"]'
                        )
                        .text()
                    )
                    rmtext2 = (
                        self.parser.pyq_parser(
                            html,
                            'div[id="contentx"] p[style="font-weight:bold;text-align:center;"]'
                        )
                        .text()
                    )
                    body_article = (
                        self.parser.pyq_parser(
                            html,
                            'div[id="contentx"] p'
                        )
                        .text()
                        .lstrip()
                    )
                    body_article = body_article if body_article != "" else (
                        self.parser.pyq_parser(
                            html,
                            'div[id="article-box"] p'
                        )
                        .text()
                        .lstrip()
                    )
                    strong = (
                        self.parser.pyq_parser(
                            html,
                            'div[id="contentx"] p strong'
                        )
                        .eq(0)
                        .text()
                    )
                    body_article = (
                        self.__rmBracket(body_article)
                        .replace(rmtext1, "")
                        .replace(rmtext2, "")
                        .replace(" BACA JUGA:", "")
                        .lstrip()
                        .rstrip()
                    )
                    content_article = Utility.UniqClear(body_article)
                    desc = f"{body_article[:100]}..."
                    tags = []
                    for tag in self.parser.pyq_parser(
                        html,
                        'div[class="detail-tag newtag"] ul li'
                    ):
                        tag_article = (
                            self.parser.pyq_parser(
                                tag,
                                'li a[class="ga_Tag"]'
                            )
                            .remove("span")
                            .text()
                        )
                        tags.append(tag_article)
                    if not tags:
                        for tag in self.parser.pyq_parser(
                            html,
                            'div[class="detail-tag"] ul li'
                        ):
                            tag_article = (
                                self.parser.pyq_parser(
                                    tag,
                                    'li a[class="ga_Tag"]'
                                )
                                .remove("span")
                                .text()
                            )
                            tags.append(tag_article)

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
                        "content": content_article,
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
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")


if __name__ == "__main__":
    cookies = []
    sb = Index()
