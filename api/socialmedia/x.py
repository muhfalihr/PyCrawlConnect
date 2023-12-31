import datetime
import json
import re
import io

from flask import Blueprint, request, send_file
from flask_restx import Resource
from enum import Enum
from api import api
from helper import success_response, error_response, flask_response
from controller.socialmedia.X.userpost import Users
from controller.socialmedia.X.downloader import Downloader
from . import pk

x = Blueprint("x", __name__)
ns_api = api.namespace("x", description="Social Media")


@ns_api.route("/profile-user", methods=["GET"])
class UsersX(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "screen_name": {"description": "screen name\nExample: gibran_tweet", "required": True},
        },
    )
    def get(self):
        try:
            screen_name = request.values.get("screen_name")
            profile = Users()
            data = profile.profile(screen_name=screen_name)
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


@ns_api.route("/media-user", methods=["GET"])
class MediaUsersX(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "screen_name": {"description": "screen name\nExample: gibran_tweet", "required": True},
        },
    )
    def get(self):
        try:
            screen_name = request.values.get("screen_name")
            profile = Users()
            data = profile.media(screen_name=screen_name)
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
