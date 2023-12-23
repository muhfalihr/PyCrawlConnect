import datetime
import json
import re
import io

from flask import Blueprint, request, send_file
from flask_restx import Resource, fields
from enum import Enum
from api import api
from helper import success_response, error_response, flask_response
from helper.kafka_produser import ProduserKafka
from controller.film.lk21.searchfilter import SearchFilter


from bs4 import BeautifulSoup
from pyquery import PyQuery as pq

import requests
from requests.cookies import RequestsCookieJar
from faker import Faker


class HtmlParser:
    def __init__(self):
        pass

    def bs4_parser(self, html, selector):
        result = None
        try:
            html = BeautifulSoup(html, "lxml")
            result = html.select(selector)
        except Exception as e:
            print(e)
        finally:
            return result

    def pyq_parser(self, html, selector):
        result = None
        try:
            html = pq(html)
            result = html(selector)
        except Exception as e:
            print(e)
        finally:
            return result


class OrderBy(Enum):
    populer = "Populer"
    release = "Tahun Pembuatan"
    rating = "IMDB Rating"
    title = "Judul File"
    latest = "Tanggal Uploud"


class Order(Enum):
    desc = "Besar ke kecil"
    asc = "Kecil ke besar"


class FilterEnum:
    def __init__(self) -> None:
        self.enums = {}
        self.session = requests.session()
        self.jar = RequestsCookieJar()
        self.fake = Faker()
        self.parser = HtmlParser()

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

    def filterenum(self, filter, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.set_cookies(cookies=cookies)
        url = "https://tv6.lk21official.wiki/"
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
            enums = {}
            html = content.decode("utf-8")
            match filter:
                case "genres":
                    for option in self.parser.pyq_parser(
                        html,
                        'div[class="form-group"] select[name="genre1"] option'
                    ):
                        key = self.parser.pyq_parser(
                            option,
                            'option'
                        ).attr("value")
                        value = self.parser.pyq_parser(
                            option,
                            'option'
                        ).text()
                        if key != "0":
                            enums[key] = value
                            self.enums[key] = value
                case "countries":
                    for option in self.parser.pyq_parser(
                        html,
                        'div[class="form-group"] select[name="country"] option'
                    ):
                        key = self.parser.pyq_parser(
                            option,
                            'option'
                        ).attr("value")
                        value = self.parser.pyq_parser(
                            option,
                            'option'
                        ).text()
                        if key != "0":
                            enums[key] = value
                            self.enums[key] = value
                case "year":
                    for option in self.parser.pyq_parser(
                        html,
                        'div[class="form-group"] select[name="tahun"] option'
                    ):
                        key = self.parser.pyq_parser(
                            option,
                            'option'
                        ).attr("value")
                        value = self.parser.pyq_parser(
                            option,
                            'option'
                        ).text()
                        if key != "0":
                            enums[key] = value
                            self.enums[key] = value
            value_list = []
            for k, v in enums.items():
                value_list.append(v)
            return value_list
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def key(self, value):
        for k in self.enums.keys():
            if self.enums[k] == value:
                return k

    def orderbyenum(self, value):
        for key, enum_value in OrderBy.__members__.items():
            if value == enum_value.value:
                return key
        return None

    def orderenum(self, value):
        for key, enum_value in Order.__members__.items():
            if value == enum_value.value:
                return key
        return None


lk21 = Blueprint("lk21", __name__)
ns_api = api.namespace("lk21", description="Film")

FE = FilterEnum()


@ns_api.route("/search", methods=["GET"])
class SearchMovie(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "keyword": {
                "description": "Define keyword!",
                "required": True
            }
        }
    )
    def get(self):
        try:
            keyword = request.values.get("keyword")
            search = SearchFilter()
            # pk = ProduserKafka()
            data = search.search(keyword=keyword)
            reponse = (
                success_response(data, message="success"), 200
            )
            # pk.produser(datas=reponse)
            return reponse
        except Exception as e:
            if re.search("status code", str(e)):
                pattern = r"status code (\d+) : (.+)"
                match = re.search(pattern, str(e))
                if match:
                    status_code = match.group(1)
                    message = match.group(2)
                    return error_response(
                        message=json.dumps(
                            dict(
                                message=message,
                                status=int(status_code),
                            )
                        ),
                        status=int(status_code),
                    )
                else:
                    return error_response(
                        message=json.dumps(dict(message=str(e), status=500))
                    )
            else:
                return error_response(
                    message=json.dumps(dict(message=str(e), status=500))
                )


@ns_api.route("/filter-movie", methods=["GET"])
class FilterMovie(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "orderby": {
                "description": "Select Order by",
                "enum": [e.value for e in OrderBy],
                "default": OrderBy.populer.value,
                "required": True
            },
            "order": {
                "description": "Select Order",
                "enum": [e.value for e in Order],
                "default": Order.desc.value,
                "required": True
            },
            "page": {
                "description": "Page number",
                "type": int,
                "default": 1,
            },
            "genre1": {
                "description": "Select Genre1",
                "enum": [e for e in FE.filterenum(filter="genres")]
            },
            "genre2": {
                "description": "Select Genre2",
                "enum": [e for e in FE.filterenum(filter="genres")]
            },
            "country": {
                "description": "Select Country",
                "enum": [e for e in FE.filterenum(filter="countries")]
            },
            "year": {
                "description": "Select Year",
                "enum": [e for e in FE.filterenum(filter="year")]
            },
            "hdonly": {
                "description": "Only HD and SD\nNOTE : If 1 = True, 0 = False",
                "enum": [e for e in range(2)],
                "type": int,
                "default": 0
            }
        }
    )
    def get(self):
        try:
            orderby = FE.orderbyenum(request.values.get("orderby"))
            order = FE.orderenum(request.values.get("order"))
            page = request.values.get("page")
            genre1 = FE.key(request.values.get("genre1"))
            genre2 = FE.key(request.values.get("genre2"))
            country = FE.key(request.values.get("country"))
            hdonly = request.values.get("hdonly")
            search = SearchFilter()
            # pk = ProduserKafka()
            data = search.filter(
                orderby=orderby,
                order=order,
                page=page,
                type="1",
                genre1=genre1,
                genre2=genre2,
                country=country,
                hdonly=hdonly
            )
            reponse = (
                success_response(data, message="success"), 200
            )
            # pk.produser(datas=reponse)
            return reponse
        except Exception as e:
            if re.search("status code", str(e)):
                pattern = r"status code (\d+) : (.+)"
                match = re.search(pattern, str(e))
                if match:
                    status_code = match.group(1)
                    message = match.group(2)
                    return error_response(
                        message=json.dumps(
                            dict(
                                message=message,
                                status=int(status_code),
                            )
                        ),
                        status=int(status_code),
                    )
                else:
                    return error_response(
                        message=json.dumps(dict(message=str(e), status=500))
                    )
            else:
                return error_response(
                    message=json.dumps(dict(message=str(e), status=500))
                )


@ns_api.route("/filter-series", methods=["GET"])
class FilterSeries(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "orderby": {
                "description": "Select Order by",
                "enum": [e.value for e in OrderBy],
                "default": OrderBy.populer.value,
                "required": True
            },
            "order": {
                "description": "Select Order",
                "enum": [e.value for e in Order],
                "default": Order.desc.value,
                "required": True
            },
            "page": {
                "description": "Page number",
                "type": int,
                "default": 1,
            },
            "genre1": {
                "description": "Select Genre1",
                "enum": [e for e in FE.filterenum(filter="genres")]
            },
            "genre2": {
                "description": "Select Genre2",
                "enum": [e for e in FE.filterenum(filter="genres")]
            },
            "country": {
                "description": "Select Country",
                "enum": [e for e in FE.filterenum(filter="countries")]
            },
            "year": {
                "description": "Select Year",
                "enum": [e for e in FE.filterenum(filter="year")]
            },
            "hdonly": {
                "description": "Only HD and SD\nNOTE : If 1 = True, 0 = False",
                "enum": [e for e in range(2)],
                "type": int,
                "default": 0
            }
        }
    )
    def get(self):
        try:
            orderby = FE.orderbyenum(request.values.get("orderby"))
            order = FE.orderenum(request.values.get("order"))
            page = request.values.get("page")
            genre1 = FE.key(request.values.get("genre1"))
            genre2 = FE.key(request.values.get("genre2"))
            country = FE.key(request.values.get("country"))
            hdonly = request.values.get("hdonly")
            search = SearchFilter()
            # pk = ProduserKafka()
            data = search.filter(
                orderby=orderby,
                order=order,
                page=page,
                type="2",
                genre1=genre1,
                genre2=genre2,
                country=country,
                hdonly=hdonly
            )
            reponse = (
                success_response(data, message="success"), 200
            )
            # pk.produser(datas=reponse)
            return reponse
        except Exception as e:
            if re.search("status code", str(e)):
                pattern = r"status code (\d+) : (.+)"
                match = re.search(pattern, str(e))
                if match:
                    status_code = match.group(1)
                    message = match.group(2)
                    return error_response(
                        message=json.dumps(
                            dict(
                                message=message,
                                status=int(status_code),
                            )
                        ),
                        status=int(status_code),
                    )
                else:
                    return error_response(
                        message=json.dumps(dict(message=str(e), status=500))
                    )
            else:
                return error_response(
                    message=json.dumps(dict(message=str(e), status=500))
                )
