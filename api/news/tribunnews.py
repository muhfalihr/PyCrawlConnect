import datetime
import json
import re
import io

from flask import Blueprint, request, send_file
from flask_restx import Resource, fields
from enum import Enum
from api import api
from helper import success_response, error_response, flask_response
from controller.news.tribunnews.indeks import NewsIndexArsip
from . import pk


tribunnews = Blueprint("tribunnews", __name__)
ns_api = api.namespace("tribunnews", description="News")


class SitesEnum(Enum):
    news = "news"
    nasional = "nasional"
    internasional = "internasional"
    regional = "regional"
    metropolitan = "metropolitan"
    sains = "sains"
    pendidikan = "pendidikan"


class DaerahEnum(Enum):
    wartakota = "Jakarta"
    jabar = "Jawa Barat"
    bogor = "Bogor"
    jogja = "Jogja"
    solo = "Solo"
    jateng = "Jawa Tengah"
    surabaya = "Surabaya"
    suryamalang = "Malang"
    bali = "Bali"
    aceh = "Aceh"
    medan = "Medan"
    pekanbaru = "Pekanbaru"
    batam = "Batam"
    jambi = "Jambi"
    palembang = "Palembang"
    bangka = "Bangka"
    lampung = "Lampung"
    pontianak = "Pontianak"
    banjarmasin = "Banjarmasin"
    kaltim = "Balikpapan"
    makassar = "Makassar"
    manado = "Manado"
    kupang = "Kupang"
    sumsel = "Sumatera Selatan"


class DatesEnum(Enum):
    TANGGAL_1 = 1
    TANGGAL_2 = 2
    TANGGAL_3 = 3
    TANGGAL_4 = 4
    TANGGAL_5 = 5
    TANGGAL_6 = 6
    TANGGAL_7 = 7
    TANGGAL_8 = 8
    TANGGAL_9 = 9
    TANGGAL_10 = 10
    TANGGAL_11 = 11
    TANGGAL_12 = 12
    TANGGAL_13 = 13
    TANGGAL_14 = 14
    TANGGAL_15 = 15
    TANGGAL_16 = 16
    TANGGAL_17 = 17
    TANGGAL_18 = 18
    TANGGAL_19 = 19
    TANGGAL_20 = 20
    TANGGAL_21 = 21
    TANGGAL_22 = 22
    TANGGAL_23 = 23
    TANGGAL_24 = 24
    TANGGAL_25 = 25
    TANGGAL_26 = 26
    TANGGAL_27 = 27
    TANGGAL_28 = 28
    TANGGAL_29 = 29
    TANGGAL_30 = 30
    TANGGAL_31 = 31


class MonthEnum(Enum):
    bulan_1 = 1
    bulan_2 = 2
    bulan_3 = 3
    bulan_4 = 4
    bulan_5 = 5
    bulan_6 = 6
    bulan_7 = 7
    bulan_8 = 8
    bulan_9 = 9
    bulan_10 = 10
    bulan_11 = 11
    bulan_12 = 12


class YearEnum(Enum):
    year2019 = 2019
    year2020 = 2020
    year2021 = 2021
    year2022 = 2022
    year2023 = 2023


def matching(classenum, formatdatetime):
    for enum in classenum:
        datenow = datetime.datetime.now()
        date = datenow.strftime(formatdatetime)
        date = int(date)
        if date == enum.value:
            return date


def setDaerahEnum(daerah):
    listde = [{e.name: e.value} for e in DaerahEnum]
    for lde in listde:
        for k, v in zip(lde.keys(), lde.values()):
            if daerah == v:
                return k


@ns_api.route("/index-news", methods=["GET"])
class NewsIndex(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "sites": {
                "description": "select size",
                "enum": [e.value for e in SitesEnum],
                "default": SitesEnum.news.value,
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
            sites = request.values.get("sites")
            date = request.values.get("date")
            month = request.values.get("month")
            year = request.values.get("year")
            page = request.values.get("page")
            search = NewsIndexArsip()
            data = search.newsIndex(
                site=sites,
                date=date,
                month=month,
                year=year,
                page=page
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


@ns_api.route("/archive-news", methods=["GET"])
class NewsArchive(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "year": {
                "description": "select year\nNOTE : Untuk ditahun 2019 hanya terdapat article di bulan Desember saja.",
                "enum": [e.value for e in YearEnum],
                "default": matching(YearEnum, "%Y"),
                "required": True
            },
            "month": {
                "description": "select month\nNOTE : Untuk ditahun 2019 hanya terdapat article di bulan Desember saja.",
                "enum": [e.value for e in MonthEnum]
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
            month = request.values.get("month")
            year = request.values.get("year")
            page = request.values.get("page")
            search = NewsIndexArsip()
            data = search.newsArchive(
                month=month,
                year=year,
                page=page
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
                "default": DaerahEnum.wartakota.value,
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
            daerah = request.values.get("region")
            date = request.values.get("date")
            month = request.values.get("month")
            year = request.values.get("year")
            page = request.values.get("page")
            search = NewsIndexArsip()
            daerah = setDaerahEnum(daerah=daerah)
            data = search.newsIndex(
                site="daerah",
                date=date,
                month=month,
                year=year,
                page=page,
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
