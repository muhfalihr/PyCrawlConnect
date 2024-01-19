import requests
import re
import json
import random
import string

from pyquery import PyQuery
from urllib.parse import urljoin, urlencode, unquote
from datetime import datetime
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
                if "preview" in url:
                    match = re.search(r'[^/]+$', url).group(0)
                    filename = f'{match}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                elif "content" in url:
                    filename = re.search(r"/([^/]+)\.pdf", url)
                    if filename:
                        filename = f'{filename.group(1)}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                    else:
                        match = re.search(r"m\:(.*?)\/", url).group(1)
                        filename = f'{match}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                else:
                    filename = datetime.now().strftime("%Y%m%dT%H%M%S")
                filename = unquote(filename)
            content_type = resp.headers.get("content-type")
            return data, filename, content_type
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


if __name__ == "__main__":
    search = Downloader()
