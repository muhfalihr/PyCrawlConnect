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


class All:
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

    def __datarow(self, parent: bytes, eq: int) -> str:
        field = (
            self.__parser.pyq_parser(
                parent,
                'div[class="col-lg-6 col-md-6 col-md-6"] p'
            )
            .eq(eq)
            .clone()
        )
        field.find("strong").remove()
        return field.text().lstrip(': ').replace('n/a', '').replace('N/A', '')

    def __allbooks(self, url: str, page: int, proxy: Optional[str] = None, **kwargs) -> dict:

        user_agent = self.__fake.user_agent()

        self.__headers["User-Agent"] = user_agent
        resp = self.__session.request(
            method="GET",
            url=url,
            headers=self.__headers,
            timeout=60,
            proxies=proxy,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            datas = []
            html = content.decode('utf-8')
            links = []
            tag_a = self.__parser.pyq_parser(
                html,
                'span[class="visible-xs"] p[class="media-heading lead"] a'
            )
            for link in tag_a:
                a = (
                    self.__parser.pyq_parser(
                        link,
                        'a'
                    )
                    .attr('href')
                )
                links.append(a)
            pagelist = []
            tag_li = self.__parser.pyq_parser(
                html,
                'ul[class="pagination"] li'
            )
            for num in tag_li:
                pn = (
                    self.__parser.pyq_parser(
                        num,
                        'li'
                    )
                    .text()
                )
                pagelist.append(pn)
            maxpage = int(pagelist[-2].replace(',', ''))\
                if pagelist != [] else 1
            nextpage = page+1 if page < maxpage else ""
            for link in links:
                resp = self.__session.request(
                    method="GET",
                    url=link,
                    headers=self.__headers,
                    timeout=60,
                    proxies=proxy,
                    **kwargs
                )
                status_code = resp.status_code
                content = resp.content
                if status_code == 200:
                    html = content.decode('utf-8')
                    id = Utility.hashmd5(url=link)
                    details_book = self.__parser.pyq_parser(
                        html,
                        'div[class="col-lg-8 col-md-8"]'
                    )
                    title = (
                        self.__parser.pyq_parser(
                            details_book,
                            'p[class="media-heading h3"]'
                        )
                        .text()
                    )
                    img = (
                        self.__parser.pyq_parser(
                            details_book,
                            'div[class="col-xs-12"] img[class="thumbnail"]'
                        )
                        .attr('src')
                    )
                    desc = (
                        self.__parser.pyq_parser(
                            details_book,
                            'div[class="col-xs-12"]'
                        )
                        .eq(0)
                        .text()
                    )
                    authors = []
                    about_authors = self.__parser.pyq_parser(
                        details_book,
                        'div[class="row"] span[class="visible-xs"] ul[class="list-inline"]'
                    )
                    for auth in about_authors:
                        author = (
                            self.__parser.pyq_parser(
                                auth,
                                'li'
                            )
                            .eq(0)
                            .text()
                        )
                        authors.append(author)
                    tags = []
                    about_tags = self.__parser.pyq_parser(
                        details_book,
                        'div[class="col-lg-12 col-md-12 col-md-12"] p a'
                    )
                    for t in about_tags:
                        tag = (
                            self.__parser.pyq_parser(
                                t,
                                'a'
                            )
                            .text()
                        )
                        tags.append(tag)
                    pubdate = self.__datarow(details_book, 0)
                    isbn10 = self.__datarow(details_book, 1)
                    isbn13 = self.__datarow(details_book, 2)
                    paperback = self.__datarow(details_book, 3)
                    views = self.__datarow(details_book, 4)
                    type = self.__datarow(details_book, 5)
                    publisher = self.__datarow(details_book, 6)
                    license = self.__datarow(details_book, 7)
                    post_time = self.__datarow(details_book, 8)
                    excerpts = (
                        self.__parser.pyq_parser(
                            details_book,
                            'div blockquote span'
                        )
                        .text()
                    )
                    downloadsite = (
                        self.__parser.pyq_parser(
                            details_book,
                            'div[id="srvata-content"] li a[class="btn btn-primary"]'
                        )
                        .attr('href')
                    )
                    data = {
                        "id": id,
                        "url": link,
                        "title": title,
                        "thumbnail_link": img,
                        "authors": authors,
                        "description": desc,
                        "tags": tags,
                        "publication_date": pubdate,
                        "isbn-10": isbn10,
                        "isbn-13": isbn13,
                        "paperback": paperback,
                        "views": views,
                        "document_type": type,
                        "publisher": publisher,
                        "license": license,
                        "post_time": post_time,
                        "excerpts": excerpts,
                        "download_link": downloadsite
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

    def all(
            self,
            option: Optional[str] = None,
            page: Optional[int] = 1,
            allbook: Optional[bool] = False,
            idlink: Optional[str] = None,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:

        user_agent = self.__fake.user_agent()
        if cookies:
            cookies = self.__set_cookies(cookies=cookies)
        page = int(page)
        page = page+1 if page == 0 else -page if '-' in str(page) else page
        self.__headers["User-Agent"] = user_agent
        match option:
            case "topics":
                url = f"http://www.freetechbooks.com/topics?page={page}"
                result = self.__allbooks(
                    url=url,
                    page=page,
                    proxy=proxy,
                    cookies=cookies
                )
                return result

            case "categories":
                url = "http://www.freetechbooks.com/categories"
                resp = self.__session.request(
                    method="GET",
                    url=url,
                    headers=self.__headers,
                    cookies=cookies,
                    proxies=proxy,
                    **kwargs
                )
                status_code = resp.status_code
                content = resp.content
                if status_code == 200:
                    datas = []
                    html = content.decode('utf-8')
                    links = []
                    div = self.__parser.pyq_parser(
                        html,
                        'div[class="col-lg-8 col-md-8"] tbody tr'
                    )
                    for a in div:
                        link = (
                            self.__parser.pyq_parser(
                                a,
                                'a'
                            )
                            .attr('href')
                        )
                        links.append(link)
                    categories = []
                    for a in div:
                        cat = (
                            self.__parser.pyq_parser(
                                a,
                                'a'
                            )
                            .text()
                        )
                        categories.append(cat)
                    ids = [
                        re.search(r'/([^/]+)\.html$', id).group(1)
                        for id in links
                    ]
                    for link, category, id in zip(links, categories, ids):
                        data = {
                            "id": id,
                            "category": category,
                            "link": link
                        }
                        datas.append(data)
                    result = {
                        "result": datas
                    }
                    return result
                else:
                    raise HTTPErrorException(
                        f"Error! status code {resp.status_code} : {resp.reason}"
                    )

            case "authors":
                url = f"http://www.freetechbooks.com/authors?page={page}"
                resp = self.__session.request(
                    method="GET",
                    url=url,
                    headers=self.__headers,
                    cookies=cookies,
                    proxies=proxy,
                    **kwargs
                )
                status_code = resp.status_code
                content = resp.content
                if status_code == 200:
                    datas = []
                    html = content.decode('utf-8')
                    div = self.__parser.pyq_parser(
                        html,
                        'div[class="col-lg-8 col-md-8"]'
                    )
                    pagelist = []
                    tag_li = self.__parser.pyq_parser(
                        div,
                        'ul[class="pagination"] li'
                    )
                    for num in tag_li:
                        pn = (
                            self.__parser.pyq_parser(
                                num,
                                'li'
                            )
                            .text()
                        )
                        pagelist.append(pn)
                    maxpage = int(pagelist[-2])
                    nextpage = page+1 if page < maxpage else ""
                    links = []
                    table = self.__parser.pyq_parser(
                        div,
                        'table[class="table table-hover table-responsive"] tbody tr td[class="col-md-3"]'
                    )
                    for a in table:
                        link = (
                            self.__parser.pyq_parser(
                                a,
                                'a'
                            )
                            .attr('href')
                        )
                        links.append(link)
                    links = self.unique(links)
                    table = self.__parser.pyq_parser(
                        div,
                        'table[class="table table-hover table-responsive"] tbody tr'
                    )
                    fullnames = []
                    for td in table:
                        name = self.__parser.pyq_parser(
                            td,
                            '[class="col-md-3"]'
                        )
                        fix = []
                        for fn in name:
                            fullname = (
                                self.__parser.pyq_parser(
                                    fn,
                                    '[class="col-md-3"]'
                                )
                                .text()
                                .replace('"', "'")
                            )
                            fix.append(fullname)
                        fix.reverse()
                        fullnames.append(' '.join(fix))
                    ids = [
                        re.search(r'/([^/]+)\.html$', id).group(1)
                        for id in links
                    ]
                    posts = []
                    for p in table:
                        post = (
                            self.__parser.pyq_parser(
                                p,
                                'td[class="col-md-1 text-center"]'
                            )
                            .text()
                        )
                        posts.append(post)

                    for link, fullname, id, post in zip(links, fullnames, ids, posts):
                        data = {
                            "fullname": fullname,
                            "id": id,
                            "post": post,
                            "link": link
                        }
                        datas.append(data)
                    result = {
                        "result": datas,
                        "nextpage": nextpage
                    }
                    return result
                else:
                    raise HTTPErrorException(
                        f"Error! status code {resp.status_code} : {resp.reason}"
                    )

            case "publishers":
                url = f"http://www.freetechbooks.com/publishers?page={page}"
                resp = self.__session.request(
                    method="GET",
                    url=url,
                    headers=self.__headers,
                    cookies=cookies,
                    proxies=proxy,
                    **kwargs
                )
                status_code = resp.status_code
                content = resp.content
                if status_code == 200:
                    datas = []
                    html = content.decode('utf-8')
                    div = self.__parser.pyq_parser(
                        html,
                        'div[class="col-lg-8 col-md-8"]'
                    )
                    pagelist = []
                    tag_li = self.__parser.pyq_parser(
                        div,
                        'ul[class="pagination"] li'
                    )
                    for num in tag_li:
                        pn = (
                            self.__parser.pyq_parser(
                                num,
                                'li'
                            )
                            .text()
                        )
                        pagelist.append(pn)
                    maxpage = int(pagelist[-2])
                    nextpage = page+1 if page < maxpage else ""
                    links = []
                    table = self.__parser.pyq_parser(
                        div,
                        'table[class="table table-hover table-responsive"] tbody tr td[class="col-md-6"]'
                    )
                    for a in table:
                        link = (
                            self.__parser.pyq_parser(
                                a,
                                'a'
                            )
                            .attr('href')
                        )
                        links.append(link)
                    publisher_names = []
                    for a in table:
                        name = (
                            self.__parser.pyq_parser(
                                a,
                                'a'
                            )
                            .text()
                        )
                        publisher_names.append(name)
                    table = self.__parser.pyq_parser(
                        div,
                        'table[class="table table-hover table-responsive"] tbody tr'
                    )
                    posts = []
                    for p in table:
                        post = (
                            self.__parser.pyq_parser(
                                p,
                                'td[class="col-md-1 text-center"]'
                            )
                            .text()
                        )
                        posts.append(post)
                    ids = [
                        re.search(r'/([^/]+)\.html$', id).group(1)
                        for id in links
                    ]
                    for link, pubname, id, post in zip(links, publisher_names, ids, posts):
                        data = {
                            "publisher_name": pubname,
                            "id": id,
                            "post": post,
                            "link": link
                        }
                        datas.append(data)
                    result = {
                        "result": datas,
                        "nextpage": nextpage
                    }
                    return result
                else:
                    raise HTTPErrorException(
                        f"Error! status code {resp.status_code} : {resp.reason}"
                    )
            case "licenses":
                url = f"http://www.freetechbooks.com/licenses?page={page}"
                resp = self.__session.request(
                    method="GET",
                    url=url,
                    headers=self.__headers,
                    cookies=cookies,
                    proxies=proxy,
                    **kwargs
                )
                status_code = resp.status_code
                content = resp.content
                if status_code == 200:
                    datas = []
                    html = content.decode('utf-8')
                    div = self.__parser.pyq_parser(
                        html,
                        'div[class="col-lg-8 col-md-8"]'
                    )
                    pagelist = []
                    tag_li = self.__parser.pyq_parser(
                        div,
                        'ul[class="pagination"] li'
                    )
                    for num in tag_li:
                        pn = (
                            self.__parser.pyq_parser(
                                num,
                                'li'
                            )
                            .text()
                        )
                        pagelist.append(pn)
                    maxpage = int(pagelist[-2])
                    nextpage = page+1 if page < maxpage else ""
                    links = []
                    table = self.__parser.pyq_parser(
                        div,
                        'table[class="table table-hover table-responsive"] tbody tr td[class="col-md-6"]'
                    )
                    for a in table:
                        link = (
                            self.__parser.pyq_parser(
                                a,
                                'a'
                            )
                            .attr('href')
                        )
                        links.append(link)
                    license_names = []
                    for a in table:
                        name = (
                            self.__parser.pyq_parser(
                                a,
                                'a'
                            )
                            .text()
                        )
                        license_names.append(name)
                    table = self.__parser.pyq_parser(
                        div,
                        'table[class="table table-hover table-responsive"] tbody tr'
                    )
                    posts = []
                    for p in table:
                        post = (
                            self.__parser.pyq_parser(
                                p,
                                'td[class="col-md-1 text-center"]'
                            )
                            .text()
                        )
                        posts.append(post)
                    ids = [
                        re.search(r'/([^/]+)\.html$', id).group(1)
                        for id in links
                    ]
                    for link, licname, id, post in zip(links, license_names, ids, posts):
                        data = {
                            "license_name": licname,
                            "id": id,
                            "post": post,
                            "link": link
                        }
                        datas.append(data)
                    result = {
                        "result": datas,
                        "nextpage": nextpage
                    }
                    return result
                else:
                    raise HTTPErrorException(
                        f"Error! status code {resp.status_code} : {resp.reason}"
                    )

        match allbook:
            case True:
                url = f"http://www.freetechbooks.com/{idlink}.html?page={page}"
                result = self.__allbooks(
                    url=url,
                    page=page,
                    proxy=proxy,
                    cookies=cookies
                )
                return result


if __name__ == "__main__":
    sb = All()
