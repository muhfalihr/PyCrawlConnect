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
        self.__session = requests.session()
        self.__fake = Faker()
        self.__parser = HtmlParser()

        self.__headers = dict()
        self.__headers["Accept"] = "application/json, text/plain, */*"
        self.__headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.__headers["Sec-Fetch-Dest"] = "empty"
        self.__headers["Sec-Fetch-Mode"] = "cors"
        self.__headers["Sec-Fetch-Site"] = "same-site"

    def __set_sort_by(self, sort_by: str) -> str:
        match sort_by:
            case "title":
                sort_by = "field_title"
            case "author":
                sort_by = "mnybks_author_last_name"
            case "popularity":
                sort_by = "field_downloads"
            case "rating":
                sort_by = "mnybks_comment_rate"
            case _:
                return sort_by
        return sort_by

    def search(self, keyword: str, sort_by: str, page: int, proxy: Optional[str] = None, **kwargs) -> dict:
        user_agent = self.__fake.user_agent()

        keyword = keyword.replace(" ", "%20")
        sort_by = self.__set_sort_by(sort_by)

        url = f"https://manybooks.net/search-book?search={keyword}&sort_by={sort_by}&page={page}"

        self.__headers["user-agent"] = user_agent
        r = self.__session.request(
            "GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs,
        )
        status_code = r.status_code
        data = r.content
        if status_code == 200:
            datas = []
            html = data.decode("utf-8")
            try:
                next_page = self.__parser.pyq_parser(
                    html, 'li[class="pager__item pager__item--next"] a'
                ).attr("href")
                next_page = re.sub(".*page=", "", next_page)
            except:
                next_page = ""

            data = self.__parser.pyq_parser(
                html, '[class="view-content"] [class="content"]'
            )
            for div in data:
                book_links = self.__parser.pyq_parser(div, "a").attr("href")
                book_links = f"https://manybooks.net{book_links}"
                r = self.__session.request(
                    "GET",
                    url=book_links,
                    timeout=60,
                    proxies=proxy,
                    headers=self.__headers,
                    **kwargs,
                )
                status_code = r.status_code
                data = r.content
                if status_code == 200:
                    title = self.__parser.pyq_parser(
                        data, 'div[itemprop="name"]').text()
                    description = self.__parser.pyq_parser(
                        data,
                        '[class="field field--name-field-description field--type-string-long field--label-hidden field--item"]',
                    ).text()
                    authors = []
                    for a in self.__parser.pyq_parser(
                        data,
                        '[class="field field--name-field-author-er field--type-entity-reference field--label-hidden field--items"] [class="field--item"]',
                    ):
                        author = self.__parser.pyq_parser(
                            a, '[itemprop="author"]').text()
                        authors.append(author)
                    authors = list(filter(None, authors))
                    downloads = (
                        self.__parser.pyq_parser(
                            data,
                            '[class="field field--name-field-downloads field--type-integer field--label-hidden field--item"]',
                        )
                        .text()
                        .replace(",", "")
                    )
                    published = self.__parser.pyq_parser(
                        data,
                        '[class="field field--name-field-published-year field--type-integer field--label-hidden field--item"]',
                    ).text()
                    pages = self.__parser.pyq_parser(
                        data,
                        '[class="field field--name-field-pages field--type-integer field--label-hidden field--item"]',
                    ).text()
                    isbn = self.__parser.pyq_parser(
                        data,
                        '[class="field field--name-field-isbn field--type-string field--label-hidden field--item"]',
                    ).text()
                    count_review = (
                        self.__parser.pyq_parser(
                            data, '[class="mb-rate-description"]')
                        .eq(0)
                        .text()
                    )
                    count_review = int(re.findall("[0-9]+", count_review)[0])
                    book_excerpt = self.__parser.pyq_parser(
                        data,
                        '[class="block block-ctools-block block-entity-fieldnodefield-excerpt clearfix"] [class="block-content"]',
                    ).text()
                    genres = []
                    for genre in self.__parser.pyq_parser(
                        data,
                        '[class="field field--name-field-genre field--type-entity-reference field--label-hidden field--items"] [class="field--item"] a',
                    ):
                        genres.append(genre.text)

                    reviews = []
                    for review in self.__parser.pyq_parser(
                        data, '[id="reviews"] [class="views-row"]'
                    ):
                        user_full_name = self.__parser.pyq_parser(
                            review, '[class="full-name"]'
                        ).text()
                        rating = self.__parser.pyq_parser(
                            review, '[class="field-rating"]'
                        ).text()
                        text = self.__parser.pyq_parser(
                            review,
                            '[class="field field--name-field-review field--type-string-long field--label-hidden field--item"]',
                        ).text()
                        upvote = (
                            self.__parser.pyq_parser(
                                review, '[class="mb-comment-bottom-items"] li'
                            )
                            .eq(0)
                            .text()
                        )
                        upvote = int(re.findall("[0-9]+", upvote)[0])
                        downvote = (
                            self.__parser.pyq_parser(
                                review, '[class="mb-comment-bottom-items"] li'
                            )
                            .eq(1)
                            .text()
                        )
                        downvote = int(re.findall("[0-9]+", downvote)[0])
                        created_at = self.__parser.pyq_parser(
                            review,
                            '[class="mb-comment-bottom-items"] [class="mb-comment-created-date"]',
                        ).text()

                        review = {
                            "user_full_name": user_full_name,
                            "rating": int(rating) if rating else None,
                            "text": text,
                            "upvote": upvote,
                            "downvote": downvote,
                            "created_at": created_at,
                        }
                        reviews.append(review)

                    data = {
                        "title": title,
                        "description": description,
                        "authors": authors,
                        "published": int(published) if published else None,
                        "pages": int(pages) if pages else None,
                        "isbn": isbn,
                        "downloads": int(downloads),
                        "count_review": count_review,
                        "book_excerpt": book_excerpt,
                        "genre": genres,
                        "book_links": book_links,
                        "reviews": reviews,
                    }
                    datas.append(data)
                else:
                    raise HTTPErrorException(
                        f"Error! status code {r.status_code} : {r.reason}"
                    )

            result = {
                "result": datas,
                "next_page": next_page,
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {r.status_code} : {r.reason}"
            )


if __name__ == "__main__":
    sb = Search()
    sb.search()
