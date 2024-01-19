import requests
import re
import json
import random
import string

from pyquery import PyQuery
from urllib.parse import urljoin, urlencode, unquote
from faker import Faker
from typing import Any, Optional
from helper.exception import *


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

    def download(self, url: str, proxy: Optional[str] = None, **kwargs) -> Any:
        user_agent = self.__fake.user_agent()

        self.__headers["User-Agent"] = user_agent
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs,
        )
        status_code = resp.status_code
        data = resp.content
        if status_code == 200:
            content_disposition = resp.headers.get("content-disposition")
            if content_disposition:
                filename = re.search(
                    r'filename=([^;]+)', content_disposition).group(1)
            else:
                if "link.springer.com" in url:
                    filename = re.search(
                        r'content/pdf/10.1186/(.*$)', url).group(1)
                else:
                    filename = re.search(
                        r'counter/pdf/10.1186/(.*$)', url).group(1)
                filename = unquote(filename)
            content_type = resp.headers.get("content-type")
            return data, filename, content_type
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


if __name__ == "__main__":
    search = Downloader()
