import datetime
import json
import re
import io

from flask import Blueprint, request, send_file
from flask_restx import Resource
from enum import Enum
from api import api
from helper import success_response, error_response, flask_response
from controller.socialmedia.instagram.api_ig import API
from controller.socialmedia.instagram.downloader import Downloader
from . import pk

instagram = Blueprint("instagram", __name__)
ns_api = api.namespace("instagram", description="Social Media")
cookies = "ig_did=3ABCC936-AF74-4336-A4EB-7DA5FFEDA4A3; datr=gSJ5ZVzOZePX4p1BJ0SxrjNN; mid=ZXkihwAEAAFoAqJ6keaV4txQaUuz; ig_nrcb=1; shbid=\"5680\05433964907779\0541735354007:01f78d55aadf11b317d96761a907671b471332d788b998a0a27bef6a3877871f3a26f7ee\"; shbts=\"1703818007\05433964907779\0541735354007:01f7443ecb3f3d9851fcac85e8c737956542507f73840303bff7d5422651291f701fb261\"; csrftoken=UUsIB4w3gqGzHFDPYpJZn49i5vo6Dno1; ds_user_id=63948446931; rur=\"NHA\05463948446931\0541735722517:01f755f224ff5c3c15e07c9836afe974ee5f28e93f742bb5289338368f2501d3291e4412\"; sessionid=63948446931%3AMOcQTY6Lz8PHgd%3A18%3AAYeJpLEp5-QeC0dZ8n-3MA2RGzfk7bInblKDSvV9Vw"


@ns_api.route("/user-profile", methods=["GET"])
class UsersIG(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "username": {"description": "username\nExample: gibran_rakabuming", "required": True},
        },
    )
    def get(self):
        try:
            username = request.values.get("username")
            profile = API(cookie=cookies)
            data = profile.profile(username=username)
            return (
                success_response(data=data, message=f"success"),
                200,
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


@ns_api.route("/user-media", methods=["GET"])
class MediaUsersIG(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "username": {"description": "username\nExample: gibran_rakabuming", "required": True},
            "max_id": {"description": "max_id\nTaken from the results of this onpoint, the bottom part.\nExample: {\"cached_comments_cursor\": \"18055356079507540\", \"bifilter_token\": \"KEUBFABYACAAGAAQABAACAAIAAgACAAIAP_9OH_-_X37mo7_C3dH4P06jbY3H5slylf1___v86-H____YvyxGfBBCgGCBgAA\"}"}
        },
    )
    def get(self):
        try:
            username = request.values.get("username")
            max_id = request.values.get("max_id")
            profile = API(cookie=cookies)
            data = profile.media(username=username, max_id=max_id)
            return (
                success_response(data=data, message=f"success"),
                200,
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


@ns_api.route("/users-comments", methods=["GET"])
class UserComments(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "pk": {
                "description": "The pk key value from the user-media onpoint result.",
                "required": True
            },
            "min_id": {
                "description": "min_id.\nTaken from the results of this onpoint, the bottom part."
            }
        },
    )
    def get(self):
        try:
            pk = request.values.get("pk")
            min_id = request.values.get("min_id")
            profile = API(cookie=cookies)
            data = profile.comments(pk=pk, min_id=min_id)
            return (
                success_response(data=data, message=f"success"),
                200,
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


@ns_api.route("/download", methods=["GET"])
class Download(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "media_url_https": {
                "description": "media_url_https from data search return",
                "required": True,
                "example": "https://pbs.twimg.com/media/FyUTYm4aUAAYY1h.jpg",
            }
        },
    )
    def get(self):
        try:
            media_url_https = request.values.get("media_url_https")
            downloader = Downloader()
            data, filename, content_type = downloader.download(
                url=media_url_https)
            file_stream = io.BytesIO(data)
            return send_file(
                file_stream,
                as_attachment=True,
                mimetype=content_type,
                download_name=filename,
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
