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

    def newsIndex(self, site, page, year, month, date, daerah=None, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.set_cookies(cookies=cookies)
        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page
        if site != "daerah":
            url = f"https://{site}.detik.com/berita/indeks/{page}?date={month}/{date}/{year}"
        else:
            url = f"https://www.detik.com/{daerah}/berita/indeks/{page}?date={month}/{date}/{year}"
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
            for article in self.parser.pyq_parser(
                html,
                'div[class="column-9"] div[class="nhl indeks mgb-24"] div[id="indeks-container"] article[class="list-content__item"]'
            ):
                article_link = (
                    self.parser.pyq_parser(
                        article,
                        'div[class="media media--left media--image-radius block-link"] div[class="media__text"] h3[class="media__title"] a[class="media__link"]'
                    )
                    .attr("href")
                )
                links.append(article_link)
            maxpage = (
                self.parser.pyq_parser(
                    html,
                    'div[class="pagination text-center mgt-16 mgb-16"] a'
                )
                .eq(-2)
                .text()
            )
            maxpage = int(maxpage) if maxpage != "" else 1
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
                            'article[class="detail"] div[class="detail__header"] h1[class="detail__title"]'
                        )
                        .text()
                    )
                    newstime = (
                        self.parser.pyq_parser(
                            html,
                            'article[class="detail"] div[class="detail__header"] div[class="detail__date"]'
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
                    pubday = f"{year}{month}{date}"
                    pubhour = f"{pubday}{hour}"
                    pubminute = f"{pubday}{hour}{minute}"
                    pubyear = year
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
                    source = re.search(r'https?://([^/]+)', link)
                    if source:
                        source = source.group(1)
                    else:
                        source = "detik.com"
                    author = (
                        self.parser.pyq_parser(
                            html,
                            'article[class="detail"] div[class="detail__header"] div[class="detail__author"]'
                        )
                        .remove("span")
                        .text()
                        .rstrip()
                        .rstrip(" -")
                    )
                    editor = ""
                    image = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="detail__media"] figure[class="detail__media-image"] img[class="p_img_zoomin img-zoomin"]'
                        )
                        .attr("src")
                    )
                    body_article = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="detail__body-text itp_bodycontent"] p'
                        )
                        .text()
                    )
                    body_article = self.utility.UniqClear(body_article)
                    desc = f"{body_article[:100]}..."
                    tags = []
                    for tag in self.parser.pyq_parser(
                        html,
                        'div[class="detail__body-tag mgt-16"] div[class="nav"] a'
                    ):
                        article_tag = (
                            self.parser.pyq_parser(
                                tag,
                                'a'
                            )
                            .text()
                        )
                        tags.append(article_tag)
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
            #     with open("controller/news/detik/result.json", "w") as file:
            #         file.write(results)
            # except Exception:
            #     with open("controller/news/detik/result.json", "r+") as file:
            #         file.write(results)
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")


if __name__ == "__main__":
    cookies = []
    sb = Index()
    # cek = sb.newsIndex(site="news", page=1, year=2023, month=12, date="07")
    # print(cek)
