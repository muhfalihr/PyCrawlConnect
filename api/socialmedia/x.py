import datetime
import json
import re
import io

from flask import Blueprint, request, send_file
from flask_restx import Resource
from enum import Enum
from api import api
from helper import success_response, error_response, flask_response
from controller.socialmedia.X.xcrawl import XCrawl
from controller.socialmedia.X.downloader import Downloader
from . import pk

x = Blueprint("x", __name__)
ns_api = api.namespace("x", description="Social Media")
# Required
cookie = ''


class SearchProduct(Enum):
    top = "Top"
    latest = "Latest"
    people = "People"
    media = "Media"


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
                "enum": [e.value for e in SearchProduct],
                "default": SearchProduct.people.value,
                "required": True
            },
            "count": {
                "description": "count",
                "default": 20,
                "type": int
            },
            "cursor": {
                "description": "The value of the key \"cursor_value\" of this onpoint result. To return the results of the next API response."
            }
        },
    )
    def get(self):
        try:
            rawquery = request.values.get("rawquery")
            product = request.values.get("product")
            count = request.values.get("count")
            cursor = request.values.get("cursor")
            profile = XCrawl(cookie=cookie)
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
            profile = XCrawl(cookie=cookie)
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
            "count": {
                "description": "count",
                "default": 20,
                "type": int
            },
            "cursor": {
                "description": "The value of the key \"cursor_value\" of this onpoint result. To return the results of the next API response."
            }
        },
    )
    def get(self):
        try:
            userId = request.values.get("userId")
            profile = XCrawl(cookie=cookie)
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
                "description": "The value of the key \"cursor_value\" of this onpoint result. To return the results of the next API response."
            }
        },
    )
    def get(self):
        try:
            userId = request.values.get("userId")
            count = request.values.get("count")
            cursor = request.values.get("cursor")
            profile = XCrawl(cookie=cookie)
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


@ns_api.route("/user-replies", methods=["GET"])
class UserTweetsAndReplies(Resource):
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
                "description": "The value of the key \"cursor_value\" of this onpoint result. To return the results of the next API response."
            }
        },
    )
    def get(self):
        try:
            userId = request.values.get("userId")
            count = request.values.get("count")
            cursor = request.values.get("cursor")
            profile = XCrawl(cookie=cookie)
            data = profile.replies(userId=userId, count=count, cursor=cursor)
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


@ns_api.route("/user-likes", methods=["GET"])
class UserLikes(Resource):
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
                "description": "The value of the key \"cursor_value\" of this onpoint result. To return the results of the next API response."
            }
        },
    )
    def get(self):
        try:
            userId = request.values.get("userId")
            count = request.values.get("count")
            cursor = request.values.get("cursor")
            profile = XCrawl(cookie=cookie)
            data = profile.likes(userId=userId, count=count, cursor=cursor)
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


@ns_api.route("/user-tweetdetail", methods=["GET"])
class UserTweetsDetail(Resource):
    @api.doc(
        responses=flask_response("get"),
        params={
            "focalTweetId": {
                "description": "focalTweetId\n*NOTE:Taken from key rest_id from onpoint \"user-profile\" or \"search\".",
                "required": True
            },
            "controller_data": {
                "description": "controller_data",
                "default": "DAACDAABDAABCgABAAAAAAAAAAAKAAkXK+YwNdoAAAAAAAA=",
            },
            "cursor": {
                "description": "The value of the key \"cursor_value\" of this onpoint result. To return the results of the next API response."
            }
        },
    )
    def get(self):
        try:
            tweetdetail = request.values.get("tweetdetail")
            controller_data = request.values.get("controller_data")
            cursor = request.values.get("cursor")
            profile = XCrawl(cookie=cookie)
            data = profile.tweetdetail(
                tweetdetail=tweetdetail, controller_data=controller_data, cursor=cursor
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


@ns_api.route("/user-following", methods=["GET"])
class UserFollowing(Resource):
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
                "description": "The value of the key \"cursor_value\" of this onpoint result. To return the results of the next API response."
            }
        },
    )
    def get(self):
        try:
            userId = request.values.get("userId")
            count = request.values.get("count")
            cursor = request.values.get("cursor")
            profile = XCrawl(cookie=cookie)
            data = profile.following(userId=userId, count=count, cursor=cursor)
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
class UserFollowers(Resource):
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
                "description": "The value of the key \"cursor_value\" of this onpoint result. To return the results of the next API response."
            }
        },
    )
    def get(self):
        try:
            userId = request.values.get("userId")
            count = request.values.get("count")
            cursor = request.values.get("cursor")
            profile = XCrawl(cookie=cookie)
            data = profile.followers(userId=userId, count=count, cursor=cursor)
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


@ns_api.route("/user-blue_verified_followers", methods=["GET"])
class BlueVerifiedFollowers(Resource):
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
                "description": "The value of the key \"cursor_value\" of this onpoint result. To return the results of the next API response."
            }
        },
    )
    def get(self):
        try:
            userId = request.values.get("userId")
            count = request.values.get("count")
            cursor = request.values.get("cursor")
            profile = XCrawl(cookie=cookie)
            data = profile.blue_verified_followers(
                userId=userId, count=count, cursor=cursor)
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


@ns_api.route("/user-followers_you_know", methods=["GET"])
class FollowersYouKnow(Resource):
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
                "description": "The value of the key \"cursor_value\" of this onpoint result. To return the results of the next API response."
            }
        },
    )
    def get(self):
        try:
            userId = request.values.get("userId")
            count = request.values.get("count")
            cursor = request.values.get("cursor")
            profile = XCrawl(cookie=cookie)
            data = profile.followers_you_know(
                userId=userId, count=count, cursor=cursor)
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
            profile = XCrawl(cookie=cookie)
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
