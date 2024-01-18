import requests
import re
import json
import random
import string

from pyquery import PyQuery
from urllib.parse import urljoin, urlencode, unquote
from faker import Faker
from helper.exception import *
from typing import Any, Optional


class Downloader:
    def __init__(self):
        self.__session = requests.session()
        self.__fake = Faker()

        self.__headers = dict()
        self.__headers["Accept"] = "application/json, text/plain, */*"
        self.__headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.__headers["Sec-Fetch-Dest"] = "empty"
        self.__headers["Sec-Fetch-Mode"] = "cors"
        self.__headers["Sec-Fetch-Site"] = "same-site"

    def download(self, bookID: str, proxy: Optional[str] = None, **kwargs) -> Any:

        user_agent = self.__fake.user_agent()

        self.__headers["user-agent"] = user_agent

        url = f"https://www.bookrix.com/Books/Download.html?bookID={bookID}&format=epub"

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
            # Mendapatkan nama file dari header "content-disposition" jika ada
            content_disposition = r.headers.get("content-disposition")
            if content_disposition:
                filename_match = re.search(
                    r'filename="([^"]+)"', content_disposition)
                if filename_match:
                    filename = unquote(filename_match.group(1))
                else:
                    print("Filename not found in content-disposition header")
            else:
                # Jika header "content-disposition" tidak ada, menggunakan bagian terakhir dari URL sebagai nama file
                filename = url.split("/")[-1]
                filename = unquote(filename)
            content_type = r.headers.get("content-type")
            return data, filename, content_type
        else:
            raise HTTPErrorException(
                f"Error! status code {r.status_code} : {r.reason}"
            )


if __name__ == "__main__":
    search = Downloader()
