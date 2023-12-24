import datetime
import json
import re
import io

from flask import Blueprint, request, send_file
from flask_restx import Resource, fields
from enum import Enum
from api import api
from helper import success_response, error_response, flask_response
from controller.news.detik.indeks import Index
from . import pk


detik = Blueprint("detik", __name__)
ns_api = api.namespace("detik", description="News")


class DaerahEnum(Enum):
    jateng = "jateng"
    jatim = "jatim"
    jabar = "jabar"
    sulsel = "sulsel"
    sumut = "sumut"
    bali = "bali"
    sumbagsel = "sumbagsel"
    jogja = "jogja"


class DatesEnum(Enum):
    TANGGAL_1 = "01"
    TANGGAL_2 = "02"
    TANGGAL_3 = "03"
    TANGGAL_4 = "04"
    TANGGAL_5 = "05"
    TANGGAL_6 = "06"
    TANGGAL_7 = "07"
    TANGGAL_8 = "08"
    TANGGAL_9 = "09"
    TANGGAL_10 = "10"
    TANGGAL_11 = "11"
    TANGGAL_12 = "12"
    TANGGAL_13 = "13"
    TANGGAL_14 = "14"
    TANGGAL_15 = "15"
    TANGGAL_16 = "16"
    TANGGAL_17 = "17"
    TANGGAL_18 = "18"
    TANGGAL_19 = "19"
    TANGGAL_20 = "20"
    TANGGAL_21 = "21"
    TANGGAL_22 = "22"
    TANGGAL_23 = "23"
    TANGGAL_24 = "24"
    TANGGAL_25 = "25"
    TANGGAL_26 = "26"
    TANGGAL_27 = "27"
    TANGGAL_28 = "28"
    TANGGAL_29 = "29"
    TANGGAL_30 = "30"
    TANGGAL_31 = "31"


class MonthEnum(Enum):
    bulan_1 = "01"
    bulan_2 = "02"
    bulan_3 = "03"
    bulan_4 = "04"
    bulan_5 = "05"
    bulan_6 = "06"
    bulan_7 = "07"
    bulan_8 = "08"
    bulan_9 = "09"
    bulan_10 = "10"
    bulan_11 = "11"
    bulan_12 = "12"


class YearEnum(Enum):
    year2007 = "2007"
    year2008 = "2008"
    year2009 = "2009"
    year2010 = "2010"
    year2011 = "2011"
    year2012 = "2012"
    year2013 = "2013"
    year2014 = "2014"
    year2015 = "2015"
    year2016 = "2016"
    year2017 = "2017"
    year2018 = "2018"
    year2019 = "2019"
    year2020 = "2020"
    year2021 = "2021"
    year2022 = "2022"
    year2023 = "2023"


def matching(classenum, formatdatetime):
    for enum in classenum:
        datenow = datetime.datetime.now()
        date = datenow.strftime(formatdatetime)
        if date == enum.value:
            return date


@ns_api.route("/index-news", methods=["GET"])
class NewsIndex(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "date": {
                "description": "select date",
                "enum": [e.value for e in DatesEnum],
                "default": matching(DatesEnum, "%d")
            },
            "month": {
                "description": "select month",
                "enum": [e.value for e in MonthEnum],
                "default": matching(MonthEnum, "%m")
            },
            "year": {
                "description": "select year",
                "enum": [e.value for e in YearEnum],
                "default": matching(YearEnum, "%Y")
            },
            "page": {
                "description": "Page number",
                "type": int,
                "default": 1,
            }
        }
    )
    def get(self):
        try:
            date = request.values.get("date")
            month = request.values.get("month")
            year = request.values.get("year")
            page = request.values.get("page")
            daerah = request.values.get("region")
            search = Index()
            data = search.newsIndex(
                site="news",
                page=page,
                year=year,
                month=month,
                date=date,
                daerah=daerah
            )
            pk.produser(datas=data)
            return (
                success_response(data, message="success"), 200
            )
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


@ns_api.route("/index-news-daerah", methods=["GET"])
class NewsIndexDaerah(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "region": {
                "description": "select region",
                "enum": [e.value for e in DaerahEnum],
                "default": DaerahEnum.jatim.value,
                "required": True
            },
            "date": {
                "description": "select date",
                "enum": [e.value for e in DatesEnum],
                "default": matching(DatesEnum, "%d")
            },
            "month": {
                "description": "select month",
                "enum": [e.value for e in MonthEnum],
                "default": matching(MonthEnum, "%m")
            },
            "year": {
                "description": "select year",
                "enum": [e.value for e in YearEnum],
                "default": matching(YearEnum, "%Y")
            },
            "page": {
                "description": "Page number",
                "type": int,
                "default": 1,
            }
        }
    )
    def get(self):
        try:
            date = request.values.get("date")
            month = request.values.get("month")
            year = request.values.get("year")
            page = request.values.get("page")
            daerah = request.values.get("region")
            search = Index()
            data = search.newsIndex(
                site="daerah",
                page=page,
                year=year,
                month=month,
                date=date,
                daerah=daerah
            )
            pk.produser(datas=data)
            return (
                success_response(data, message="success"), 200
            )
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
