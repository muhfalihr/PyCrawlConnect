import requests
import re
import json
import random
import string
import time

from pyquery import PyQuery
from urllib.parse import urljoin, urlencode
from faker import Faker
from datetime import datetime
from typing import Any, Optional
from googletrans import Translator
from helper.html_parser import HtmlParser
from helper.utility import Utility
from helper.exception import *


class SearchFilter:
    def __init__(self):
        self.__session = requests.session()
        self.__fake = Faker()
        self.__parser = HtmlParser()
        self.__translator = Translator()

        self.__headers = dict()
        self.__headers["Accept"] = "application/json, text/plain, */*"
        self.__headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.__headers["Sec-Fetch-Dest"] = "empty"
        self.__headers["Sec-Fetch-Mode"] = "cors"
        self.__headers["Sec-Fetch-Site"] = "same-site"

    def __regex(self, text: str, field: str) -> str:
        try:
            match field:
                case "title":
                    pattern = re.compile(
                        r'(?:LK21\sNONTON\s)?(.*)', re.IGNORECASE)
                    matches = pattern.findall(text)
                    if matches:
                        return matches[0]
                    return None
                case "site":
                    pattern = re.compile(r'https?://\S+')
                    matches = pattern.search(text)
                    if matches:
                        return matches.group().rstrip("')")
                    return None
                case "path":
                    pattern = re.compile(r"^https?://.*?/(.*)$")
                    matches = pattern.search(text)
                    if matches:
                        return matches.group(1)
                    return None
                case "page":
                    pattern = re.compile(r'\b(\d+)\s+total\s+halaman\b')
                    matches = pattern.search(text)
                    if matches:
                        return int(matches.group(1))
                    return None
        except Exception:
            return text

    def strtodate(self, text: str, field: str) -> str:
        try:
            if field == "published":
                date = datetime.strptime(text, "%B %d, %Y")
                result = date.strftime("%Y%m%d")
            elif field == "uploaded":
                date = datetime.strptime(text, "%B %d, %Y %I:%M %p")
                result = date.strftime("%Y-%m-%dT%H:%M:%S")
            return result
        except Exception:
            return text

    def search(self, keyword: str, proxy: str = None, **kwargs) -> dict:

        user_agent = self.__fake.user_agent()

        keyword = keyword.replace(" ", "+")

        url = f"https://tv2.lk21official.co/search.php?s={keyword}"

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
            links = []
            for searchitem in self.__parser.pyq_parser(
                html,
                'div[class="search-wrapper"] div[class="search-item"]'
            ):
                searchitem_link = (
                    self.__parser.pyq_parser(
                        searchitem,
                        'div[class="col-xs-9 col-sm-10 search-content"] h3 a'
                    )
                    .attr("href")
                )
                title_link = (
                    self.__parser.pyq_parser(
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
            links = Utility.makeunique(links)
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
                    id = Utility.hashmd5(url=link)
                    title = self.__regex(
                        self.__parser.pyq_parser(
                            html,
                            'div[class="container"] h1'
                        )
                        .text(),
                        "title"
                    )
                    title = title if title else ""
                    synopsis = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="col-xs-9 content"] blockquote'
                        )
                        .remove("strong")
                        .remove("a")
                        .remove("span")
                        .text()
                        .replace("\n", " ")
                    )
                    site = self.__regex(
                        self.__parser.pyq_parser(
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

                    image = self.__parser.pyq_parser(
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
                    for h2 in self.__parser.pyq_parser(
                        html,
                        'div[class="col-xs-9 content"] div'
                    ):
                        h2_text = (
                            self.__parser.pyq_parser(
                                h2,
                                'div h2'
                            )
                            .text()
                        )
                        h2_text = self.__translator.translate(
                            h2_text, dest='en', src='id'
                        ).text.lower()
                        h2_list.append(h2_text)
                    for index, value in enumerate(h2_list):
                        match value:
                            case "movie star":
                                parser_list = []
                                for h3 in self.__parser.pyq_parser(
                                    html,
                                    'div[class="col-xs-9 content"] div'
                                ).eq(index).find("h3"):
                                    parser = (
                                        self.__parser.pyq_parser(
                                            h3,
                                            'h3 a'
                                        )
                                        .text()
                                    )
                                    parser_list.append(parser)
                                data.update(movie_stars=parser_list)

                            case "genre" | "country":
                                parser_list = []
                                for h3 in self.__parser.pyq_parser(
                                    html,
                                    'div[class="col-xs-9 content"] div'
                                ).eq(index).find("a"):
                                    parser = (
                                        self.__parser.pyq_parser(
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
                                    self.__parser.pyq_parser(
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
                                    self.__parser.pyq_parser(
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

    def filter(
            self,
            orderby: str,
            order: str,
            page: int,
            type: Optional[str] = None,
            genre1: Optional[str] = None,
            genre2: Optional[str] = None,
            country: Optional[str] = None,
            year: Optional[str | int] = None,
            hdonly: Optional[int] = 0,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:

        user_agent = self.__fake.user_agent()

        type = type if type else 0
        genre1 = genre1 if genre1 else 0
        genre2 = genre2 if genre2 else 0
        country = country if country else 0
        year = year if year else 0
        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page

        url = f"https://tv6.lk21official.wiki/{orderby}/page/{page}/?order={order}&type={type}&genre1={genre1}&genre2={genre2}&country={country}&tahun={year}&hdonly={hdonly}"

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
            links = []
            for filteritem in self.__parser.pyq_parser(
                html,
                'div[class="grid-archive"] div[id="grid-wrapper"] div'
            ):
                filteritem_link = (
                    self.__parser.pyq_parser(
                        filteritem,
                        'div article header[class="grid-header"] h1[class="grid-title"] a'
                    )
                    .attr("href")
                )
                title_link = (
                    self.__parser.pyq_parser(
                        filteritem,
                        'div article footer[class="grid-action"] p'
                    )
                    .eq(1)
                    .find("a")
                    .text()
                )
                if filteritem_link:
                    if type == "2":
                        filteritem_link = "https://tv8.nontondrama.click/" + self.__regex(
                            text=filteritem_link,
                            field='path'
                        )
                        links.append(filteritem_link)
                    elif title_link != "NONTON SERIES":
                        links.append(filteritem_link)

                links = Utility.makeunique(links)
            maxpage = self.__regex(
                self.__parser.pyq_parser(
                    html,
                    'div[class="col-lg-9 col-sm-8"] header[class="archive-header"] h3'
                )
                .text(),
                "page"
            )
            nextpage = page+1 if page < maxpage else ""
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
                if status_code == 404:
                    continue
                if status_code == 200:
                    html = content.decode("utf-8")
                    id = Utility.hashmd5(url=link)
                    if type == "2":
                        title = (
                            self.__parser.pyq_parser(
                                html,
                                'section[class="breadcrumb"] div[class="container"] li[class="last"] span[itemprop="name"]'
                            )
                            .text()
                        )
                    else:
                        title = self.__regex(
                            self.__parser.pyq_parser(
                                html,
                                'div[class="container"] h1'
                            )
                            .text(),
                            "title"
                        )
                    synopsis = (
                        self.__parser.pyq_parser(
                            html,
                            'div[class="col-xs-9 content"] blockquote'
                        )
                        .remove("strong")
                        .remove("a")
                        .remove("span")
                        .text()
                        .replace("\n", " ")
                    )

                    image = self.__parser.pyq_parser(
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
                    for h2 in self.__parser.pyq_parser(
                        html,
                        'div[class="col-xs-9 content"] div'
                    ):
                        h2_text = self.__translator.translate(
                            self.__parser.pyq_parser(
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
                                for h3 in self.__parser.pyq_parser(
                                    html,
                                    'div[class="col-xs-9 content"] div'
                                ).eq(index).find("h3"):
                                    parser = (
                                        self.__parser.pyq_parser(
                                            h3,
                                            'h3 a'
                                        )
                                        .text()
                                    )
                                    parser_list.append(parser)
                                data.update(movie_stars=parser_list)

                            case "genre" | "country":
                                parser_list = []
                                for h3 in self.__parser.pyq_parser(
                                    html,
                                    'div[class="col-xs-9 content"] div'
                                ).eq(index).find("a"):
                                    parser = (
                                        self.__parser.pyq_parser(
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
                                    self.__parser.pyq_parser(
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
                                    self.__parser.pyq_parser(
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


if __name__ == "__main__":
    sb = SearchFilter()
