import datetime
import json
import re
import io

from flask import Blueprint, request, send_file
from flask_restx import Resource, fields
from enum import Enum
from api import api
from helper import success_response, error_response, flask_response
from controller.news.suara.indeks import Index
from . import pk


suara = Blueprint("suara", __name__)
ns_api = api.namespace("suara", description="News")


class YearEnum(Enum):
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
            year = request.values.get("year")
            page = request.values.get("page")
            search = Index()
            data = search.newsIndex(
                page=page,
                year=year
            )
            reponse = (
                success_response(data, message="success"), 200
            )
            pk.produser(datas=reponse)
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
