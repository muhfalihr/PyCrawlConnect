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
from controller.news.kompas.search import Search


kompas = Blueprint("kompas", __name__)
ns_api = api.namespace("kompas", description="News")


class SitesEnum(Enum):
    all = "all"
    news = "news"
    nasional = "nasional"
    regional = "regional"
    megapolitan = "megapolitan"
    Global = "global"
    tren = "tren"
    health = "health"
    food = "food"
    edukasi = "edukasi"
    money = "money"
    umkm = "umkm"
    tekno = "tekno"
    lifestyle = "lifestyle"
    homey = "homey"
    properti = "properti"
    bola = "bola"
    travel = "travel"
    otomotif = "otomotif"
    sains = "sains"
    hype = "hype"
    jeo = "jeo"
    healtH = "health"
    skola = "skola"
    stori = "stori"
    wiken = "wiken"


@ns_api.route("/search", methods=["GET"])
class NewsSearch(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "sites": {
                "description": "select size",
                "enum": [e.value for e in SitesEnum],
                "default": SitesEnum.all.value,
                "required": True
            },
            "date": {
                "description": "writing format = YYYYmmdd"
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
            page = request.values.get("page")
            search = Search()
            # Uncomment ini jika menggunakan Kafka
            # pk = ProduserKafka(topic="")
            data = search.search(site=sites, date=date, page=page)
            reponse = (
                success_response(data, message="success"), 200
            )
            # Uncomment ini jika menggunakan Kafka
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
