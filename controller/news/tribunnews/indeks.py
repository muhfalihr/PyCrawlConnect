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


class NewsIndexArsip:
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

    def newsIndex(self, page, site, year, month, date, daerah=None, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.set_cookies(cookies=cookies)
        page = int(page)
        page = page+1 if page == 0 else -page\
            if '-' in str(page) else page
        if site != "daerah":
            url = f"https://www.tribunnews.com/index-news/{site}?date={year}-{month}-{date}&page={page}"
        else:
            url = f"https://{daerah}.tribunnews.com/index-news?date={year}-{month}-{date}&page={page}"
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
                'div[class="content"] ul[class="lsi"] li[class="ptb15"]'
            ):
                article_link = (
                    self.parser.pyq_parser(
                        li,
                        'li[class="ptb15"] h3[class="f16 fbo"] a'
                    )
                    .attr("href")
                )
                article_link = f"{article_link}?page=all"
                links.append(article_link)
            maxpage = (
                self.parser.pyq_parser(
                    html,
                    'div[id="paginga"] div[class="paging"] a'
                )
                .eq(-1)
                .attr("href")
            )
            pagematch = re.search(r'page=(\d+)', maxpage)
            if pagematch:
                maxpage = int(pagematch.group(1))
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
                    div = self.parser.pyq_parser(
                        html,
                        'div[class="content"] div[id="article"]'
                    )
                    title = (
                        self.parser.pyq_parser(
                            div,
                            'h1[class="f50 black2 f400 crimson"]'
                        )
                        .text()
                    )
                    newstime = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="mt10"] time[class="grey"]'
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
                    pubhour = f"{year}{month}{date}{hour}"
                    pubminute = f"{year}{month}{date}{hour}{minute}"
                    pubyear = year
                    pubday = f"{year}{month}{date}"
                    created_at = (
                        datetime
                        .strptime(
                            pubminute,
                            "%Y%m%d%H%M"
                        )
                        .strftime("%Y-%m-%dT%H:%M:00")
                    )
                    timezone = self.utility.timezone(
                        date_time=pubminute,
                        format="%Y%m%d%H%M"
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
                            'div[class="side-article mb5"] div[class="sources mb20"] h6 div a'
                        )
                        .attr("title")
                    )
                    if source:
                        source = source
                    else:
                        source = (
                            re.match(
                                r'https?://(www\.)?([^/]+)', link
                            )
                            .group(2)
                        )
                    author = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="credit mt10"] div[id="penulis"] a'
                        )
                        .text()
                    )
                    editor = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="credit mt10"] div[id="editor"] a'
                        )
                        .text()
                    )
                    image = (
                        self.parser.pyq_parser(
                            html,
                            'div[id="artimg"] div[class="ovh imgfull_div"] a[class="icon_zoom glightbox"]'
                        )
                        .attr("href")
                    )
                    body_article = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="side-article txt-article multi-fontsize"] '
                        )
                        .remove("script")
                        .remove("strong")
                        .remove("div")
                        .remove("figcaption")
                        .text()
                    )
                    body_article = (
                        body_article
                        .replace("\n", " ")
                        .lstrip("-")
                        .lstrip("\u2013")
                        .lstrip()
                    )
                    desc = f"{body_article[:100]}..."
                    tags = []
                    for tag in self.parser.pyq_parser(
                        html,
                        'div[class="side-article mb5"] div[itemprop="keywords"] h5[class="tagcloud3"]'
                    ):
                        tag_article = (
                            self.parser.pyq_parser(
                                tag,
                                'a[class="rd2"]'
                            )
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
            #     with open("controller/news/tribunnews/result.json", "w") as file:
            #         file.write(results)
            # except Exception:
            #     with open("controller/news/tribunnews/result.json", "r+") as file:
            #         file.write(results)
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def newsArchive(self, page, year, month=None, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.set_cookies(cookies=cookies)
        page = int(page)
        page = page+1 if page == 0 else -page\
            if '-' in str(page) else page
        if month:
            month = f"/{month}"
        else:
            month = ""
        url = f"https://www.tribunnews.com/{year}{month}?page={page}"
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
                'div[class="lsi pt10 pb10"] ul li[class="ptb15"]'
            ):
                article_link = (
                    self.parser.pyq_parser(
                        li,
                        'h3[class="fbo f16"] a'
                    )
                    .attr("href")
                )
                article_link = f"{article_link}?page=all"
                links.append(article_link)
            maxpage = (
                self.parser.pyq_parser(
                    html,
                    'div[id="paginga"] div[class="paging"] a'
                )
                .eq(-1)
                .attr("href")
            )
            pagematch = re.search(r'page=(\d+)', maxpage)
            if pagematch:
                maxpage = int(pagematch.group(1))
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
                    div = self.parser.pyq_parser(
                        html,
                        'div[class="content"] div[id="article"]'
                    )
                    title = (
                        self.parser.pyq_parser(
                            div,
                            'h1[class="f50 black2 f400 crimson"]'
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
                            'div[class="mt10"] time[class="grey"]'
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
                    timezone = self.utility.timezone(
                        date_time=pubminute,
                        format="%Y%m%d%H%M"
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
                            'div[class="side-article mb5"] div[class="sources mb20"] h6 div a'
                        )
                        .attr("title")
                    )
                    if source:
                        source = source
                    else:
                        source = (
                            re.match(
                                r'https?://(www\.)?([^/]+)', link
                            )
                            .group(2)
                        )
                    author = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="credit mt10"] div[id="penulis"] a'
                        )
                        .text()
                    )
                    editor = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="credit mt10"] div[id="editor"] a'
                        )
                        .text()
                    )
                    image = (
                        self.parser.pyq_parser(
                            html,
                            'div[id="artimg"] div[class="ovh imgfull_div"] a[class="icon_zoom glightbox"]'
                        )
                        .attr("href")
                    )
                    body_article = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="side-article txt-article multi-fontsize"] '
                        )
                        .remove("script")
                        .remove("strong")
                        .remove("div")
                        .remove("figcaption")
                        .text()
                    )
                    body_article = (
                        body_article
                        .replace("\n", " ")
                        .lstrip("-")
                        .lstrip("\u2013")
                        .lstrip()
                    )
                    desc = f"{body_article[:100]}..."
                    tags = []
                    for tag in self.parser.pyq_parser(
                        html,
                        'div[class="side-article mb5"] div[itemprop="keywords"] h5[class="tagcloud3"]'
                    ):
                        tag_article = (
                            self.parser.pyq_parser(
                                tag,
                                'a[class="rd2"]'
                            )
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
            #     with open("controller/news/tribunnews/result.json", "w") as file:
            #         file.write(results)
            # except Exception:
            #     with open("controller/news/tribunnews/result.json", "r+") as file:
            #         file.write(results)
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")


if __name__ == "__main__":
    cookies = []
    sb = NewsIndexArsip()
    # cek = sb.newsArchive(page=1, year="2023")
    # cek = sb.newsIndex(page=1, site="news", year="2023", month="12", date="05")
    # print(cek)
