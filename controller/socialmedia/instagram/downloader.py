import re

from requests import Session
from faker import Faker
from helper.utility import Utility
from helper.exception import *
from typing import Any, Optional


class Downloader:
    def __init__(self, cookie: str = None) -> Any:
        if not isinstance(cookie, str):
            raise TypeError("Invalid parameter for 'Downloader'. Expected str, got {}".format(
                type(cookie).__name__)
            )

        self.session = Session()
        self.fake = Faker()

        self.headers = dict()
        self.headers["Accept"] = "application/json, text/plain, */*"
        self.headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.headers["Sec-Fetch-Dest"] = "empty"
        self.headers["Sec-Fetch-Mode"] = "cors"
        self.headers["Sec-Fetch-Site"] = "same-site"
        if cookie is not None:
            self.__headers["Cookie"] = cookie

    def download(self, url: str, proxy: Optional[str] = None, **kwargs) -> Any:
        if not isinstance(url, str):
            raise TypeError("Invalid parameter for 'download'. Expected str, got {}".format(
                type(url).__name__)
            )
        if proxy is not None:
            if not isinstance(proxy, str):
                raise TypeError("Invalid parameter for 'download'. Expected str, got {}".format(
                    type(proxy).__name__)
                )

        user_agent = self.fake.user_agent()
        self.headers["User-Agent"] = user_agent
        resp = self.session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.headers,
            cookies=cookies,
            **kwargs,
        )
        status_code = resp.status_code
        data = resp.content
        if status_code == 200:
            pattern = re.compile(r'\/([^\/?]+\.jpg)')
            matches = pattern.search(url)
            if matches:
                filename = matches.group(1)
            else:
                pattern = re.compile(r'\/([^\/?]+\.mp4)')
                matches = pattern.search(url)
                if matches:
                    filename = matches.group(1)
                else:
                    raise URLValidationError(
                        f"Error! Invalid URL \"{url}\". Make sure the URL is correctly formatted and complete."
                    )
            content_type = resp.headers.get("content-type")
            return data, filename, content_type
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


if __name__ == "__main__":
    cookies = ''
    search = Downloader(cookie=cookies)
