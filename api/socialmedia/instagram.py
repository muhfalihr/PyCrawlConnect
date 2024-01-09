import datetime
import json
import re
import io

from flask import Blueprint, request, send_file
from flask_restx import Resource
from enum import Enum
from api import api
from helper import success_response, error_response, flask_response
from controller.socialmedia.instagram.igcrawl import InstagramCrawl
from controller.socialmedia.instagram.downloader import Downloader
from . import pk

instagram = Blueprint("instagram", __name__)
ns_api = api.namespace("instagram", description="Social Media")
# Required
cookies = ""


@ns_api.route("/user-profile", methods=["GET"])
class UsersIG(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "username": {
                "description": "username\nExample: gibran_rakabuming",
                "required": True
            },
        },
    )
    def get(self):
        try:
            username = request.values.get("username")
            profile = InstagramCrawl(cookie=cookies)
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
            "username": {
                "description": "username\nExample: gibran_rakabuming",
                "required": True
            },
            "count": {
                "description": "amount of data",
                "default": 33,
                "type": int
            },
            "max_id": {
                "description": "Taken from the next_max_id key value.\nExample: 3038059354248345987_51296391646"
            }
        },
    )
    def get(self):
        try:
            username = request.values.get("username")
            count = request.values.get("count")
            max_id = request.values.get("max_id")
            profile = InstagramCrawl(cookie=cookies)
            data = profile.media(username=username, count=count, max_id=max_id)
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
                "description": "Taken from the next_min_id key value.",
                "type": str
            }
        },
    )
    def get(self):
        try:
            pk = request.values.get("pk")
            min_id = request.values.get("min_id")
            profile = InstagramCrawl(cookie=cookies)
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


@ns_api.route("/user-be_marked", methods=["GET"])
class BeMarked(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "userid": {
                "description": "id from profile onpoint result",
                "required": True
            },
            "count": {
                "description": "amount of data",
                "default": 12,
                "type": int
            },
            "cursor": {
                "description": "Taken from the end_cursor key value."
            }
        },
    )
    def get(self):
        try:
            userid = request.values.get("userid")
            count = request.values.get("count")
            cursor = request.values.get("cursor")
            profile = InstagramCrawl(cookie=cookies)
            data = profile.be_marked(userid=userid, count=count, cursor=cursor)
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


@ns_api.route("/user-followed", methods=["GET"])
class Following(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "userid": {
                "description": "id from profile onpoint result",
                "required": True
            },
            "count": {
                "description": "amount of data",
                "default": 12,
                "type": int
            },
            "max_id": {
                "description": "Taken from the next_max_id key value."
            }
        },
    )
    def get(self):
        try:
            userid = request.values.get("userid")
            count = request.values.get("count")
            max_id = request.values.get("max_id")
            profile = InstagramCrawl(cookie=cookies)
            data = profile.following(userid=userid, count=count, max_id=max_id)
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


@ns_api.route("/user-followers", methods=["GET"])
class Followers(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "userid": {
                "description": "id from profile onpoint result",
                "required": True
            },
            "count": {
                "description": "amount of data",
                "default": 12,
                "type": int
            },
            "max_id": {
                "description": "Taken from the next_max_id key value."
            }
        },
    )
    def get(self):
        try:
            userid = request.values.get("userid")
            count = request.values.get("count")
            max_id = request.values.get("max_id")
            profile = InstagramCrawl(cookie=cookies)
            data = profile.followers(userid=userid, count=count, max_id=max_id)
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
