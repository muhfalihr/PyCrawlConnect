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
from langdetect import detect
from helper.html_parser import HtmlParser
from helper.utility import Utility


class Search:
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

    def search(self, page, site, date=None, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.__set_cookies(cookies=cookies)
        page = int(page)
        page = page+1 if page == 0 else -page\
            if '-' in str(page) else page
        if date:
            date = datetime.strptime(date, "%Y%m%d")
            batas = datetime.strptime("20130501", "%Y%m%d")
            if date >= batas:
                date = date.strftime("%Y-%m-%d")
            else:
                date = "2013-05-01"
        else:
            date = datetime.now().strftime("%Y-%m-%d")
        url = f"https://indeks.kompas.com/?site={site}&date={date}&page={page}"
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
            div = self.parser.pyq_parser(
                html,
                'div[class="row mt2 col-offset-fluid clearfix"]'
            )
            maxpage = (
                self.parser.pyq_parser(
                    div,
                    'div[class="paging__wrap clearfix"] div[class="paging__item"] a[class="paging__link paging__link--prev"]'
                )
                .attr("data-ci-pagination-page")
            )
            if maxpage:
                maxpage = int(maxpage) if maxpage.isdigit() else 1
            else:
                maxpage = 1
            nextpage = page+1 if page < maxpage else ""
            links = []
            for a in self.parser.pyq_parser(
                div,
                'div[class="latest--indeks mt2 clearfix"] div[class="article__list clearfix"]'
            ):
                artcile_link = (
                    self.parser.pyq_parser(
                        a,
                        'a[class="article__link"]'
                    )
                    .attr("href")
                )
                artcile_link = f"{artcile_link}?page=all"
                links.append(artcile_link)
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
                            'div[class="col-bs10-10"] h1[class="read__title"]'
                        )
                        .text()
                    )
                    try:
                        newsdatetime = (
                            re.search(r'/(\d{4}/\d{2}/\d{2}/\d+)/', link)
                            .group(1)
                            .replace("/", "")
                        )
                    except:
                        newsdatetime = self.parser.pyq_parser(
                            html,
                            'div[class="col-bs10-10"] div[class="read__time"]'
                        ).remove("a").text()
                        ndts = []
                        for ndt in newsdatetime:
                            if ndt.isdigit():
                                ndts.append(ndt)
                        dt = "".join(ndts)
                        newsdatetime = f"{dt[4:8]}{dt[2:4]}{dt[0:2]}{dt[8:]}0000"
                    pubhour = newsdatetime[:-6]
                    pubminute = newsdatetime[:-4]
                    pubyear = newsdatetime[:4]
                    pubday = newsdatetime[:-8]
                    created_at = (
                        datetime
                        .strptime(newsdatetime, "%Y%m%d%H%M%S%f")
                        .strftime("%Y-%m-%dT%H:%M:%S")
                    )
                    timezone = Utility.timezone(
                        date_time=newsdatetime,
                        format="%Y%m%d%H%M%S%f"
                    )
                    crawling_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    id = Utility.hashmd5(url=link)
                    source = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="read__credit top clearfix"] div[class="read__credit__item"] a'
                        )
                        .text()
                    )
                    if source == "":
                        source = (
                            self.parser.pyq_parser(
                                html,
                                'div[class="read__header col-offset-fluid clearfix"] div[class="read__time"] a'
                            )
                            .text()
                        )
                    author = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="col-bs10-10"] div[class="credit"] div[class="credit-title-name"] h6'
                        )
                        .eq(0)
                        .text()
                        .rstrip(",")
                    )
                    editor = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="col-bs10-10"] div[class="credit"] div[class="credit-title-name"] h6'
                        )
                        .eq(1)
                        .text()
                    )
                    image = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="cover-photo -gallery"] div[class="photo__wrap"] img'
                        )
                        .attr("src")
                    )
                    image = image if image else (
                        self.parser.pyq_parser(
                            html,
                            'div[class="cover-photo -gallery"] div[class="photo__wrap"] img'
                        )
                        .attr("data-src")
                    )
                    image = image if image else ""
                    body_article = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="read__content"] div[class="clearfix"]'
                        )
                        .remove_class("read__bacajuga")
                        .remove_class("ads-on-body")
                        .remove_class("video")
                        .remove("strong")
                        .remove("i")
                        .text()
                    )
                    if body_article == "":
                        body_article = (
                            self.parser.pyq_parser(
                                html,
                                'div[class="read__content clearfix"] div[class="clearfix"]'
                            )
                            .remove_class("read__bacajuga")
                            .remove_class("ads-on-body")
                            .remove_class("video")
                            .remove("strong")
                            .remove("i")
                            .text()
                        )
                    body_article = (
                        Utility.UniqClear(body_article)
                        .replace("\n", " ")
                        .lstrip("-")
                        .lstrip("\u2013")
                        .lstrip()
                    )
                    lang = (
                        self.parser.pyq_parser(
                            html,
                            'html'
                        )
                        .attr("lang")
                    )
                    lang = lang if lang else detect(body_article)
                    desc = f"{body_article[:100]}..."
                    tags = []
                    for tag in self.parser.pyq_parser(
                        html,
                        'h3[class="tag tag--article clearfix"] ul[class="tag__article__wrap"] li[class="tag__article__item"]'
                    ):
                        tag_article = (
                            self.parser.pyq_parser(
                                tag,
                                'a[class="tag__article__link"]'
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
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")


if __name__ == "__main__":
    cookies = []
    sb = Search()
