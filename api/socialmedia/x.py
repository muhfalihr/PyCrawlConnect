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
# Required
cookie = ''


@ns_api.route("/search", methods=["GET"])
class SearchTimeline(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "rawquery": {
                "description": "raw query",
                "required": True
            },
            "product": {
                "description": "product",
                "default": "People",
                "required": True
            },
            "count": {
                "description": "count",
                "default": 20,
                "type": int
            },
            "cursor": {
                "description": "cursor\nTaken from the cursor_value key contained in the bottom data.\n*NOTE:To retrieve further data."
            }
        },
    )
    def get(self):
        try:
            rawquery = request.values.get("rawquery")
            product = request.values.get("product")
            count = request.values.get("count")
            cursor = request.values.get("cursor")
            profile = Users(cookie=cookie)
            data = profile.search(
                rawquery=rawquery, product=product, count=count, cursor=cursor
            )
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


@ns_api.route("/user-profile", methods=["GET"])
class UserByScreenName(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "screen_name": {"description": "screen name\nExample: gibran_tweet", "required": True},
        },
    )
    def get(self):
        try:
            screen_name = request.values.get("screen_name")
            profile = Users(cookie=cookie)
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


@ns_api.route("/user-posts", methods=["GET"])
class UserTweets(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "userId": {
                "description": "userId\n*NOTE:Taken from key rest_id from onpoint \"user-profile\" or \"search\".",
                "required": True
            },
        },
    )
    def get(self):
        try:
            userId = request.values.get("userId")
            profile = Users(cookie=cookie)
            data = profile.posts(userId=userId)
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
class UserMedia(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "userId": {
                "description": "userId\n*NOTE:Taken from key rest_id from onpoint \"user-profile\" or \"search\".",
                "required": True
            },
            "count": {
                "description": "count",
                "default": 20,
                "type": int
            },
            "cursor": {
                "description": "cursor\nTaken from the cursor_value key contained in the bottom data.\n*NOTE:To retrieve further data."
            }
        },
    )
    def get(self):
        try:
            userId = request.values.get("userId")
            count = request.values.get("count")
            cursor = request.values.get("cursor")
            profile = Users(cookie=cookie)
            data = profile.media(userId=userId, count=count, cursor=cursor)
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


@ns_api.route("/users-recomendation", methods=["GET"])
class UserRecomendation(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "userId": {
                "description": "ID of the Twitter user.\nTaken from the rest_id key value contained in the user-profile onpoint results",
                "required": True
            },
            "limit": {
                "description": "number of recommended users.\nNOTE : Max 40.",
                "required": True
            }
        },
    )
    def get(self):
        try:
            userId = request.values.get("userId")
            limit = request.values.get("limit")
            profile = Users(cookie=cookie)
            data = profile.recomendation(userId=userId, limit=limit)
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
