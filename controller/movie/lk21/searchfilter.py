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
from googletrans import Translator
from helper.html_parser import HtmlParser
from helper.utility import Utility


class SearchFilter:
    def __init__(self):
        self.session = requests.session()
        self.jar = RequestsCookieJar()
        self.fake = Faker()
        self.parser = HtmlParser()
        self.utility = Utility()
        self.translator = Translator()

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

    def regex(self, text, field):
        try:
            match field:
                case "title":
                    pattern = re.compile(
                        r'(?:LK21\sNONTON\s)?(.*)', re.IGNORECASE)
                    matches = pattern.findall(text)
                    if matches:
                        return matches[0]
                case "site":
                    pattern = re.compile(r'https?://\S+')
                    matches = pattern.search(text)
                    if matches:
                        return matches.group().rstrip("')")
                case "path":
                    pattern = re.compile(r"^https?://.*?/(.*)$")
                    matches = pattern.search(text)
                    if matches:
                        return matches.group(1)
                case "page":
                    pattern = re.compile(r'\b(\d+)\s+total\s+halaman\b')
                    matches = pattern.search(text)
                    if matches:
                        return int(matches.group(1))
        except Exception:
            return text

    def strtodate(self, text: str, field: str):
        try:
            if field == "published":
                date = datetime.strptime(text, "%B %d, %Y")
                result = date.strftime("%Y%m%d")
            elif field == "uploaded":
                date = datetime.strptime(text, "%B %d, %Y %I:%M %p")
                result = date.strftime("%Y-%m-%d %H:%M:%S")
            return result
        except Exception:
            return text

    def search(self, keyword: str, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.set_cookies(cookies=cookies)
        keyword = keyword.replace(" ", "+")
        url = f"https://tv2.lk21official.co/search.php?s={keyword}"
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
            for searchitem in self.parser.pyq_parser(
                html,
                'div[class="search-wrapper"] div[class="search-item"]'
            ):
                searchitem_link = (
                    self.parser.pyq_parser(
                        searchitem,
                        'div[class="col-xs-9 col-sm-10 search-content"] h3 a'
                    )
                    .attr("href")
                )
                title_link = (
                    self.parser.pyq_parser(
                        searchitem,
                        'div[class="col-xs-9 col-sm-10 search-content"] h3 a'
                    )
                    .text()
                )
                if "Series" in title_link:
                    continue
                else:
                    searchitem_link = f"https://tv2.lk21official.co{searchitem_link}"

                links.append(searchitem_link)
            links = self.utility.makeunique(links)
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
                    id = self.utility.hashmd5(url=link)
                    title = self.regex(
                        self.parser.pyq_parser(
                            html,
                            'div[class="container"] h1'
                        )
                        .text(),
                        "title"
                    )

                    synopsis = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="col-xs-9 content"] blockquote'
                        )
                        .remove("strong")
                        .remove("a")
                        .remove("span")
                        .text()
                        .replace("\n", " ")
                    )

                    site = self.regex(
                        self.parser.pyq_parser(
                            html,
                            'div[class="download-movie"] a'
                        )
                        .attr("onclick"),
                        "site"
                    )
                    if site:
                        site = site.split("/")
                        site.insert(3, "get")
                        site_downloader = "/".join(site)
                    else:
                        site_downloader = ""

                    image = self.parser.pyq_parser(
                        html,
                        'div[class="col-xs-3 content-poster"] img[class="img-thumbnail"]'
                    ).attr("src")
                    image = f"https:{image}" if image else ""

                    source = re.search(
                        r"https?://(.[^/]+)/",
                        link
                    )
                    source = source.group(1) if source else ""

                    crawling_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    emptystring = ""
                    emptylist = []

                    data = {
                        "id": id,
                        "title": title,
                        "link": link,
                        "source": source,
                        "thumbnail_link": image,
                        "quality": emptystring,
                        "countries": emptylist,
                        "movie_stars": emptylist,
                        "director": emptystring,
                        "genres": emptylist,
                        "imdb": emptystring,
                        "published": emptystring,
                        "translator": emptystring,
                        "by": emptystring,
                        "synopsis": synopsis,
                        "uploaded": emptystring,
                        "duration": emptystring,
                        "site_downloader": site_downloader,
                        "crawling_date": crawling_date
                    }

                    h2_list = []
                    for h2 in self.parser.pyq_parser(
                        html,
                        'div[class="col-xs-9 content"] div'
                    ):
                        h2_text = self.translator.translate(
                            self.parser.pyq_parser(
                                h2,
                                'div h2'
                            )
                            .text(),
                            src='id',
                            dest='en'
                        ).text.lower()
                        h2_list.append(h2_text)

                    for index, value in enumerate(h2_list):
                        match value:
                            case "movie star":
                                parser_list = []
                                for h3 in self.parser.pyq_parser(
                                    html,
                                    'div[class="col-xs-9 content"] div'
                                ).eq(index).find("h3"):
                                    parser = (
                                        self.parser.pyq_parser(
                                            h3,
                                            'h3 a'
                                        )
                                        .text()
                                    )
                                    parser_list.append(parser)
                                data.update(movie_stars=parser_list)

                            case "genre" | "country":
                                parser_list = []
                                for h3 in self.parser.pyq_parser(
                                    html,
                                    'div[class="col-xs-9 content"] div'
                                ).eq(index).find("a"):
                                    parser = (
                                        self.parser.pyq_parser(
                                            h3,
                                            'a'
                                        )
                                        .text()
                                    )
                                    parser_list.append(parser)
                                if value == "country":
                                    data.update(countries=parser_list)
                                data.update(genres=parser_list)

                            case "imdb":
                                parser = (
                                    self.parser.pyq_parser(
                                        html,
                                        'div[class="col-xs-9 content"] div'
                                    )
                                    .eq(index)
                                    .text()
                                    .replace("\n", " ")
                                )
                                data.update({value: parser})

                            case _:
                                parser = (
                                    self.parser.pyq_parser(
                                        html,
                                        'div[class="col-xs-9 content"] div'
                                    )
                                    .eq(index)
                                    .find("h3")
                                    .text()
                                )
                                if value == "published" or "uploaded":
                                    parser = self.strtodate(
                                        text=parser,
                                        field=value
                                    )
                                if value == "duration":
                                    parser = (
                                        parser
                                        .replace("jam", "hours")
                                        .replace("menit", "minutes")
                                    )
                                data.update({value: parser})

                    datas.append(data)
                else:
                    raise Exception(
                        f"Error! status code {resp.status_code} : {resp.reason}")
            result = {
                "result": datas
            }
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def filter(self, orderby, order, page, type=None, genre1=None, genre2=None, country=None, year=None, hdonly=0, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.set_cookies(cookies=cookies)
        type = type if type else 0
        genre1 = genre1 if genre1 else 0
        genre2 = genre2 if genre2 else 0
        country = country if country else 0
        year = year if year else 0
        page = int(page)
        page = page+1 if page == 0 else -page\
            if '-' in str(page) else page

        url = f"https://tv6.lk21official.wiki/{orderby}/page/{page}/?order={order}&type={type}&genre1={genre1}&genre2={genre2}&country={country}&tahun={year}&hdonly={hdonly}"
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
            for filteritem in self.parser.pyq_parser(
                html,
                'div[class="grid-archive"] div[id="grid-wrapper"] div'
            ):
                filteritem_link = (
                    self.parser.pyq_parser(
                        filteritem,
                        'div article header[class="grid-header"] h1[class="grid-title"] a'
                    )
                    .attr("href")
                )
                title_link = (
                    self.parser.pyq_parser(
                        filteritem,
                        'div article footer[class="grid-action"] p'
                    )
                    .eq(1)
                    .find("a")
                    .text()
                )
                if filteritem_link:
                    if type == "2":
                        filteritem_link = "https://tv8.nontondrama.click/" + self.regex(
                            text=filteritem_link,
                            field='path'
                        )
                        links.append(filteritem_link)
                    elif title_link != "NONTON SERIES":
                        links.append(filteritem_link)

                links = self.utility.makeunique(links)
            maxpage = self.regex(
                self.parser.pyq_parser(
                    html,
                    'div[class="col-lg-9 col-sm-8"] header[class="archive-header"] h3'
                )
                .text(),
                "page"
            )
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
                if status_code == 404:
                    continue
                if status_code == 200:
                    html = content.decode("utf-8")
                    id = self.utility.hashmd5(url=link)
                    if type == "2":
                        title = (
                            self.parser.pyq_parser(
                                html,
                                'section[class="breadcrumb"] div[class="container"] li[class="last"] span[itemprop="name"]'
                            )
                            .text()
                        )
                    else:
                        title = self.regex(
                            self.parser.pyq_parser(
                                html,
                                'div[class="container"] h1'
                            )
                            .text(),
                            "title"
                        )
                    synopsis = (
                        self.parser.pyq_parser(
                            html,
                            'div[class="col-xs-9 content"] blockquote'
                        )
                        .remove("strong")
                        .remove("a")
                        .remove("span")
                        .text()
                        .replace("\n", " ")
                    )

                    image = self.parser.pyq_parser(
                        html,
                        'div[class="col-xs-3 content-poster"] img[class="img-thumbnail"]'
                    ).attr("src")
                    image = f"https:{image}" if image else ""

                    source = re.search(
                        r"https?://(.[^/]+)/",
                        link
                    )
                    source = source.group(1) if source else ""

                    crawling_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    emptystring = ""
                    emptylist = []

                    data = {
                        "id": id,
                        "title": title,
                        "link": link,
                        "source": source,
                        "thumbnail_link": image,
                        "status": emptystring,
                        "quality": emptystring,
                        "countries": emptylist,
                        "movie_stars": emptylist,
                        "director": emptystring,
                        "genres": emptylist,
                        "imdb": emptystring,
                        "published": emptystring,
                        "translator": emptystring,
                        "by": emptystring,
                        "synopsis": synopsis,
                        "uploaded": emptystring,
                        "duration": emptystring,
                        "crawling_date": crawling_date
                    }
                    if type == "1":
                        del data["status"]
                    if type == "2":
                        del data["quality"]
                        del data["translator"]

                    h2_list = []
                    for h2 in self.parser.pyq_parser(
                        html,
                        'div[class="col-xs-9 content"] div'
                    ):
                        h2_text = self.translator.translate(
                            self.parser.pyq_parser(
                                h2,
                                'div h2'
                            )
                            .text(),
                            src='id',
                            dest='en'
                        ).text.lower()
                        h2_list.append(h2_text)

                    for index, value in enumerate(h2_list):
                        match value:
                            case "movie star":
                                parser_list = []
                                for h3 in self.parser.pyq_parser(
                                    html,
                                    'div[class="col-xs-9 content"] div'
                                ).eq(index).find("h3"):
                                    parser = (
                                        self.parser.pyq_parser(
                                            h3,
                                            'h3 a'
                                        )
                                        .text()
                                    )
                                    parser_list.append(parser)
                                data.update(movie_stars=parser_list)

                            case "genre" | "country":
                                parser_list = []
                                for h3 in self.parser.pyq_parser(
                                    html,
                                    'div[class="col-xs-9 content"] div'
                                ).eq(index).find("a"):
                                    parser = (
                                        self.parser.pyq_parser(
                                            h3,
                                            'a'
                                        )
                                        .text()
                                    )
                                    parser_list.append(parser)
                                if value == "country":
                                    data.update(countries=parser_list)
                                data.update(genres=parser_list)

                            case "imdb":
                                parser = (
                                    self.parser.pyq_parser(
                                        html,
                                        'div[class="col-xs-9 content"] div'
                                    )
                                    .eq(index)
                                    .text()
                                    .replace("\n", " ")
                                )
                                data.update({value: parser})

                            case _:
                                parser = (
                                    self.parser.pyq_parser(
                                        html,
                                        'div[class="col-xs-9 content"] div'
                                    )
                                    .eq(index)
                                    .find("h3")
                                    .text()
                                )
                                if value == "published" or "uploaded":
                                    parser = self.strtodate(
                                        text=parser,
                                        field=value
                                    )
                                if value == "duration":
                                    parser = (
                                        parser
                                        .replace("jam", "hours")
                                        .replace("menit", "minutes")
                                    )
                                data.update({value: parser})
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
    sb = SearchFilter()
