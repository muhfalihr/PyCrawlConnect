import requests
import re
import json
import random
import string

from pyquery import PyQuery
from urllib.parse import urljoin, urlencode
from faker import Faker
from typing import Any, Optional
from helper.exception import *


class Search:
    def __init__(self):
        self.__session = requests.session()
        self.__fake = Faker()

        self.__headers = dict()
        self.__headers["Accept"] = "application/json, text/plain, */*"
        self.__headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.__headers["Sec-Fetch-Dest"] = "empty"
        self.__headers["Sec-Fetch-Mode"] = "cors"
        self.__headers["Sec-Fetch-Site"] = "same-site"

    def search(self, kd1: str, kd2: str, limit: str, offset: str, proxy: Optional[str] = None, **kwargs):
        user_agent = self.__fake.user_agent()

        url = f"https://isbn.perpusnas.go.id/Account/GetBuku?kd1={kd1}&kd2={kd2}&limit={limit}&offset={offset}"
        self.__headers["user-agent"] = user_agent
        r = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs,
        )
        status_code = r.status_code
        data = r.content
        if status_code == 200:
            return json.loads(data.decode("utf-8"))
        else:
            raise HTTPErrorException(
                f"Error! status code {r.status_code} : {r.reason}"
            )


if __name__ == "__main__":
    search = Search()
