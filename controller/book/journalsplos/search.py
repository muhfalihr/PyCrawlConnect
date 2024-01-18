import requests

from faker import Faker
from datetime import datetime
from typing import Any, Optional
from json import loads
from helper.html_parser import HtmlParser
from helper.exception import *


class Search:
    def __init__(self):
        self.session = requests.session()
        self.fake = Faker()
        self.parser = HtmlParser()

        self.headers = dict()
        self.headers["Accept"] = "application/json, text/plain, */*"
        self.headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.headers["Sec-Fetch-Dest"] = "empty"
        self.headers["Sec-Fetch-Mode"] = "cors"
        self.headers["Sec-Fetch-Site"] = "same-site"

    def __set_pubdate(self, start: str, end: str) -> str:
        if start != None:
            start = start if "-" in start\
                else datetime.strptime(start, "%Y/%m/%d").strftime("%Y-%m-%d")\
                if "/" in start\
                else datetime.strptime(start, "%Y%m%d").strftime("%Y-%m-%d")
            current_date = datetime.now().strftime("%Y-%m-%d")
            return start, current_date

        elif start and end != None:
            start = start if "-" in start\
                else datetime.strptime(start, "%Y/%m/%d").strftime("%Y-%m-%d")\
                if "/" in start\
                else datetime.strptime(start, "%Y%m%d").strftime("%Y-%m-%d")
            end = end if "-" in end\
                else datetime.strptime(end, "%Y/%m/%d").strftime("%Y-%m-%d")\
                if "/" in end\
                else datetime.strptime(end, "%Y%m%d").strftime("%Y-%m-%d")
            return start, end

        else:
            return "", ""

    def search(
            self,
            keyword: Optional[str] = None,
            category: Optional[str] = "everything",
            filterstartdate: Optional[str] = None,
            filterenddate: Optional[str] = None,
            sizepage: Optional[int] = 15,
            sortby: Optional[str] = "RELEVANCE",
            page: Optional[int] = 1,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:

        user_agent = self.fake.user_agent()

        keyword = keyword.replace(" ", "%20")
        sortby = f"&sortOrder={sortby}"
        start, end = self.__set_pubdate(filterstartdate, filterenddate)
        pub_date_filter = f"filterStartDate={start}&filterEndDate={end}&" if filterstartdate or filterenddate != None or filterstartdate != None else ""

        match category:
            case "publication_date":
                url = f"https://journals.plos.org/plosone/dynamicSearch?unformattedQuery=publication_date%3A%5B{start}T00%3A00%3A00Z%20TO%20{end}T23%3A59%3A59Z%5D&q=publication_date%3A%5B{start}T00%3A00%3A00Z%20TO%20{end}T23%3A59%3A59Z%5D&utm_content=b&utm_campaign=ENG-2397"
            case _:
                url = f"https://journals.plos.org/plosone/dynamicSearch?{pub_date_filter}resultsPerPage={sizepage}&unformattedQuery={category}%3A{keyword}&q={category}%3A{keyword}{sortby}&page={page}&utm_content=a&utm_campaign=ENG-2397"

        self.headers["User-Agent"] = user_agent
        resp = self.session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.headers,
            **kwargs
        )

        content = resp.content
        status_code = resp.status_code
        if status_code == 200:
            raw = content.decode("utf-8")
            search_results = loads(raw)["searchResults"]
            maxpage = search_results["numFound"] / int(sizepage)
            next_page = int(page)+1 if int(page) <= maxpage else ""

            datas = []
            for doc in search_results["docs"]:
                id = doc.get("id", "")
                doc.update({
                    "id": id,
                    "eissn": doc.get("eissn", ""),
                    "publication_date": doc.get("publication_date", ""),
                    "article_type": doc.get("article_type", ""),
                    "author_display": doc.get("author_display", []),
                    "title_display": doc.get("title_display", ""),
                    "title": doc.get("title", ""),
                    "figure_table_caption": [caption.rstrip().lstrip()
                                             for caption in doc.get("figure_table_caption", [])],
                    "journal_name": doc.get("journal_name", ""),
                    "journal_key": doc.get("journal_key", ""),
                    "striking_image": doc.get("striking_image", ""),
                    "alm_mendeleyCount": doc.get("alm_mendeleyCount", 0),
                    "alm_twitterCount": doc.get("alm_twitterCount", 0),
                    "alm_scopusCiteCount": doc.get("alm_scopusCiteCount", 0),
                    "counter_total_all": doc.get("counter_total_all", 0),
                    "alm_facebookCount": doc.get("alm_facebookCount", 0),
                    "link": "https://journals.plos.org"+doc.get("link", ""),
                    "journalKey": doc.get("journalKey", "")
                })
                doc["link_download"] = f"https://journals.plos.org/plosone/article/file?id={id}&type=printable"
                datas.append(doc)

            results = {
                "results": datas,
                "next_page": next_page
            }
            return results
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


if __name__ == "__main__":
    sb = Search()
