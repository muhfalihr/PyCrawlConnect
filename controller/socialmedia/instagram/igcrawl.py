import unicodedata
import re
import json
import string
import time

from requests.sessions import Session
from requests.exceptions import Timeout, ReadTimeout
from urllib.parse import quote, unquote
from faker import Faker
from datetime import datetime
from typing import Any, Optional
from helper.utility import Utility
from helper.exception import *


class InstagramCrawl:
    def __init__(self, cookie: str = None) -> Any:
        if not isinstance(cookie, str):
            raise TypeError("Invalid parameter for 'InstagramCrawl'. Expected str, got {}".format(
                type(cookie).__name__)
            )

        self.__cookie = cookie
        self.__session = Session()
        self.__fake = Faker()

        self.__headers = dict()
        self.__headers["Accept"] = "application/json, text/plain, */*"
        self.__headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.__headers["Sec-Fetch-Dest"] = "empty"
        self.__headers["Sec-Fetch-Mode"] = "cors"
        self.__headers["Sec-Fetch-Site"] = "same-site"
        if cookie is not None:
            self.__headers["Cookie"] = cookie

    def __Csrftoken(self) -> str:
        pattern = re.compile(r'csrftoken=([a-zA-Z0-9_-]+)')
        matches = pattern.search(self.__cookie)
        if matches:
            csrftoken = matches.group(1)
            return csrftoken
        else:
            raise CSRFTokenMissingError(
                "Error! CSRF token is missing. Please ensure that a valid CSRF token is included in the cookie."
            )

    def __processmedia(self, item: dict) -> dict:
        """
        Process media entry data and return a cleaned dictionary.
        """
        if not isinstance(item, dict):
            raise TypeError("Invalid parameter for '__processmedia'. Expected dict, got {}".format(
                type(item).__name__)
            )

        pk = item["pk"]
        id = item["id"]

        KEYS_USER_REMOVE = [
            "fbid_v2",
            "feed_post_reshare_disabled",
            "is_private",
            "is_unpublished",
            "pk",
            "pk_id",
            "show_account_transparency_details",
            "strong_id__",
            "third_party_downloads_enabled",
            "account_badges",
            "fan_club_info",
            "friendship_status",
            "has_anonymous_profile_picture",
            "hd_profile_pic_versions",
            "is_favorite",
            "latest_reel_media",
            "profile_pic_id",
            'profile_pic_url',
            "transparency_product_enabled"
        ]
        for key in KEYS_USER_REMOVE:
            if key in item["user"]:
                del item["user"][key]

        for key in ["width", "height"]:
            if key in item["user"]["hd_profile_pic_url_info"]:
                del item["user"]["hd_profile_pic_url_info"][key]

        user = item["user"]

        KEYS_CAPTION_REMOVE = [
            "pk",
            "user",
            "did_report_as_spam",
            "bit_flags",
            "share_enabled",
            "is_ranked_comment",
            "is_covered",
            "private_reply_status",
            "media_id",
            "type"
        ]

        for key in KEYS_CAPTION_REMOVE:
            try:
                if key in item["caption"]:
                    del item["caption"][key]
            except TypeError:
                item["caption"] = {}

        caption = item["caption"]

        KEYS_MUSIC_REMOVE = [
            "music_canonical_id",
            "audio_type",
            "original_sound_info",
            "pinned_media_ids"
        ]

        for key in KEYS_MUSIC_REMOVE:
            try:
                if key in item["music_metadata"]:
                    del item["music_metadata"][key]
            except TypeError:
                item["music_metadata"] = {}

        KEYS_MUSIC_INFO = [
            "audio_asset_id",
            "audio_cluster_id",
            "id",
            "is_explicit",
            "cover_artwork_thumbnail_uri",
            "reactive_audio_download_url",
            "fast_start_progressive_download_url",
            "highlight_start_times_in_ms",
            "dash_manifest",
            "has_lyrics",
            "duration_in_ms",
            "dark_message",
            "allows_saving",
            "is_eligible_for_audio_effects"
        ]

        try:
            if "music_info" in item["music_metadata"]:
                if "music_asset_info" in item["music_metadata"]["music_info"]:
                    for key in KEYS_MUSIC_INFO:
                        if key in item["music_metadata"]["music_info"]["music_asset_info"]:
                            del item["music_metadata"]["music_info"]["music_asset_info"][key]
                if "music_consumption_info" in item["music_metadata"]["music_info"]:
                    del item["music_metadata"]["music_info"]["music_consumption_info"]
                if "music_canonical_id" in item["music_metadata"]["music_info"]:
                    del item["music_metadata"]["music_info"]["music_canonical_id"]

        except TypeError:
            item["music_metadata"]["music_info"] = {}

        music = item["music_metadata"]

        medias = []

        images = []
        if "carousel_media" in item:
            for index in item["carousel_media"]:
                image = index["image_versions2"]["candidates"][0]["url"]
                images.append(image)
        else:
            if "image_versions2" in item:
                image = item["image_versions2"]["candidates"][0]["url"]
                images.append(image)
        medias.extend(images)

        videos = []
        if "carousel_media" in item:
            if "video_versions" in item["carousel_media"][0]:
                video = item["carousel_media"][0]["video_versions"][0]["url"]
                videos.append(video)
        if "video_versions" in item:
            video = item["video_versions"][0]["url"]
            videos.append(video)
        medias.extend(videos)

        data = {
            "pk": pk,
            "id": id,
            "user": user,
            "caption": caption,
            "music": music,
            "medias": medias
        }
        return data

    def profile(self, username: str, proxy: Optional[str] = None, **kwargs) -> dict:
        """Retrieve information from the desired Instagram user profile via the username argument.

        Arguments :
          - username (Required) Username
          - proxy = (Optional) Used as an intermediary between the client and the server you access. These parameters are an important part of the request configuration and can help you direct traffic through proxy servers that may be needed for various purposes, such as security, anonymity, or access control.

        Keyword Argument:
          - **kwargs
        """
        if not isinstance(username, str):
            raise TypeError("Invalid parameter for 'profile'. Expected str, got {}".format(
                type(username).__name__)
            )
        if proxy is not None:
            if not isinstance(proxy, str):
                raise TypeError("Invalid parameter for 'profile'. Expected str, got {}".format(
                    type(proxy).__name__)
                )

        user_agent = self.__fake.user_agent()
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        self.__headers["User-Agent"] = user_agent
        self.__headers["X-Asbd-Id"] = "129477"
        self.__headers["X-Csrftoken"] = self.__Csrftoken()
        self.__headers["X-Ig-App-Id"] = "936619743392459"
        resp = self.__session.request(
            method="GET",
            url=url,
            headers=self.__headers,
            timeout=60,
            proxies=proxy,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            result = {
                "result": data["data"]
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )

    def media(
            self,
            username: str,
            count: Optional[int] = 33,
            max_id: Optional[str] = None,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:
        """Retrieves media posted by Instagram users via the specified username argument.

        Arguments :
          - username (Required)
          - count (Optional) defaultnya 33.
          - max_id (Optional) Arguments to retrieve results from the next API.
          - proxy = (Optional) Used as an intermediary between the client and the server you access. These parameters are an important part of the request configuration and can help you direct traffic through proxy servers that may be needed for various purposes, such as security, anonymity, or access control.

        Keyword Argument:
          - **kwargs
        """
        if not isinstance(username, str):
            raise TypeError("Invalid parameter for 'media'. Expected str, got {}".format(
                type(username).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'media'. Expected int, got {}".format(
                type(count).__name__)
            )
        if max_id is not None:
            if not isinstance(max_id, str):
                raise TypeError("Invalid parameter for 'media'. Expected str, got {}".format(
                    type(max_id).__name__)
                )
        if proxy is not None:
            if not isinstance(proxy, str):
                raise TypeError("Invalid parameter for 'media'. Expected str, got {}".format(
                    type(proxy).__name__)
                )

        user_agent = self.__fake.user_agent()
        url = f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count}"\
            if max_id else f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count}&max_id={max_id}"
        self.__headers["User-Agent"] = user_agent
        self.__headers["X-Asbd-Id"] = "129477"
        self.__headers["X-Csrftoken"] = self.__Csrftoken()
        self.__headers["X-Ig-App-Id"] = "936619743392459"
        resp = self.__session.request(
            method="GET",
            url=url,
            headers=self.__headers,
            timeout=60,
            proxies=proxy,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            next_max_id = data.get("next_max_id", "")

            datas = []
            for item in data["items"]:
                data_result = self.__processmedia(item=item)
                datas.append(data_result)
            result = {
                "result": datas,
                "next_max_id": next_max_id
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )

    def comments(
            self,
            pk: str,
            min_id: Optional[str] = None,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:
        """Retrieves all comments from a user's post specified using the pk argument.

        Arguments :
          - pk (Required)
          - min_id (Optional) Arguments to retrieve results from the next API.
          - proxy = (Optional) Used as an intermediary between the client and the server you access. These parameters are an important part of the request configuration and can help you direct traffic through proxy servers that may be needed for various purposes, such as security, anonymity, or access control.

        Keyword Argument:
          - **kwargs
        """
        if not isinstance(pk, str):
            raise TypeError("Invalid parameter for 'comments'. Expected str, got {}".format(
                type(pk).__name__)
            )
        if min_id is not None:
            if not isinstance(min_id, str):
                raise TypeError("Invalid parameter for 'comments'. Expected str, got {}".format(
                    type(min_id).__name__)
                )
        if proxy is not None:
            if not isinstance(proxy, str):
                raise TypeError("Invalid parameter for 'comments'. Expected str, got {}".format(
                    type(proxy).__name__)
                )

        user_agent = self.__fake.user_agent()
        if min_id:
            min_id = quote(unquote(min_id.replace("\\", "")).replace(" ", ""))
            url = f"https://www.instagram.com/api/v1/media/{pk}/comments/?can_support_threading=true&min_id={min_id}&sort_order=popular"
        else:
            url = f"https://www.instagram.com/api/v1/media/{pk}/comments/?can_support_threading=true&permalink_enabled=false"
        self.__headers["User-Agent"] = user_agent
        self.__headers["X-Asbd-Id"] = "129477"
        self.__headers["X-Csrftoken"] = self.__Csrftoken()
        self.__headers["X-Ig-App-Id"] = "936619743392459"
        resp = self.__session.request(
            method="GET",
            url=url,
            headers=self.__headers,
            timeout=60,
            proxies=proxy,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            if "comments" in data:
                comments = data["comments"]
                for comment in comments:
                    KEYS_COMMENT_REMOVE = [
                        "type",
                        "bit_flags",
                        "did_report_as_spam",
                        "share_enabled",
                        "is_ranked_comment",
                        "comment_index",
                        "is_covered",
                        "inline_composer_display_condition",
                        "has_liked_comment",
                        "has_more_head_child_comments",
                        "has_more_tail_child_comments",
                        "private_reply_status"
                    ]
                    for key in KEYS_COMMENT_REMOVE:
                        if key in comment:
                            del comment[key]
                    KEYS_COMMENT_USER = [
                        "is_private",
                        "strong_id__",
                        "fbid_v2",
                        "is_verified",
                        "profile_pic_id",
                        "latest_reel_media",
                        "latest_besties_reel_media"
                    ]
                    if "user" in comment:
                        for key in KEYS_COMMENT_USER:
                            if key in comment["user"]:
                                del comment["user"][key]
            result = {
                "result": {
                    "comments": data["comments"],
                    "next_min_id": data.get(
                        "next_min_id", ""
                    )
                }
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )

    def be_marked(
            self,
            userid: str | int,
            count: Optional[int] = 12,
            cursor: Optional[str] = None,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:
        """Retrieves posts tagged to the user specified using the userid argument.

        Arguments :
          - userid (Required)
          - count (Optional) defaultnya 12.
          - cursor (Optional) The key used to load the next page.
          - proxy = (Optional) Used as an intermediary between the client and the server you access. These parameters are an important part of the request configuration and can help you direct traffic through proxy servers that may be needed for various purposes, such as security, anonymity, or access control.

        Keyword Argument:
          - **kwargs
        """
        if not isinstance(userid, (str | int)):
            raise TypeError("Invalid parameter for 'be_marked'. Expected str, got {}".format(
                type(userid).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'be_marked'. Expected int, got {}".format(
                type(count).__name__)
            )
        if cursor is not None:
            if not isinstance(cursor, str):
                raise TypeError("Invalid parameter for 'be_marked'. Expected str, got {}".format(
                    type(cursor).__name__)
                )
        if proxy is not None:
            if not isinstance(proxy, str):
                raise TypeError("Invalid parameter for 'allmedia'. Expected str, got {}".format(
                    type(proxy).__name__)
                )

        user_agent = self.__fake.user_agent()
        params = {
            "variables": {
                "id": f"{userid}",
                "after": f"{cursor}",
                "first": count
            } if cursor else {
                "id": f"{userid}",
                "first": count
            }
        }
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        url = f"https://www.instagram.com/graphql/query/?doc_id=17946422347485809&variables={variables}"
        self.__headers["User-Agent"] = user_agent
        self.__headers["X-Asbd-Id"] = "129477"
        self.__headers["X-Csrftoken"] = self.__Csrftoken()
        self.__headers["X-Ig-App-Id"] = "936619743392459"
        resp = self.__session.request(
            method="GET",
            url=url,
            headers=self.__headers,
            timeout=60,
            proxies=proxy,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            edges = data["data"]["user"]["edge_user_to_photos_of_you"]["edges"]
            ids = [edge["node"]["id"] for edge in edges if "node" in edge]

            page_info = data["data"]["user"]["edge_user_to_photos_of_you"]["page_info"]
            end_cursor = page_info.get("end_cursor", "")

            datas = []
            for media_id in ids:
                url = f"https://www.instagram.com/api/v1/media/{media_id}/info/"
                resp = self.__session.request(
                    method="GET",
                    url=url,
                    headers=self.__headers,
                    timeout=60,
                    proxies=proxy
                )
                status_code = resp.status_code
                content = resp.content
                if status_code == 200:
                    response = content.decode('utf-8')
                    data = json.loads(response)
                    for item in data["items"]:
                        data_result = self.__processmedia(item=item)
                        datas.append(data_result)
                else:
                    raise Exception(
                        f"Error! status code {resp.status_code} : {resp.reason}")

            result = {
                "result": datas,
                "end_cursor": end_cursor
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )

    def following(
            self,
            userid: str | int,
            count: Optional[int] = 12,
            max_id: Optional[int] = None,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:
        """Retrieves a list of users followed by users specified using the userid argument.

        Arguments :
          - userid (Required)
          - count (Optional) defaultnya 12.
          - max_id (Optional) Arguments to retrieve results from the next API.
        """
        if not isinstance(userid, (str | int)):
            raise TypeError("Invalid parameter for 'following'. Expected str, got {}".format(
                type(userid).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'following'. Expected int, got {}".format(
                type(count).__name__)
            )
        if max_id is not None:
            if not isinstance(max_id, int):
                raise TypeError("Invalid parameter for 'following'. Expected int, got {}".format(
                    type(max_id).__name__)
                )
        if proxy is not None:
            if not isinstance(proxy, str):
                raise TypeError("Invalid parameter for 'allmedia'. Expected str, got {}".format(
                    type(proxy).__name__)
                )

        user_agent = self.__fake.user_agent()
        url = f"https://www.instagram.com/api/v1/friendships/{userid}/following/?count={count}&max_id={max_id}"\
            if max_id else f"https://www.instagram.com/api/v1/friendships/{userid}/following/?count={count}"

        self.__headers["User-Agent"] = user_agent
        self.__headers["X-Asbd-Id"] = "129477"
        self.__headers["X-Csrftoken"] = self.__Csrftoken()
        self.__headers["X-Ig-App-Id"] = "936619743392459"
        resp = self.__session.request(
            method="GET",
            url=url,
            headers=self.__headers,
            timeout=60,
            proxies=proxy,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            datas = []
            next_max_id = data.get(
                "next_max_id", ""
            )
            for user in data["users"]:
                user_data = {
                    "id": user.get(
                        "pk", ""
                    ),
                    "username": user.get(
                        "username", ""
                    ),
                    "full_name": user.get(
                        "full_name", ""
                    ),
                    "profile_pic_url": user.get(
                        "profile_pic_url", ""
                    ),
                    "is_verified": user.get(
                        "is_verified", ""
                    ),
                }
                datas.append(user_data)
            result = {
                "result": datas,
                "next_max_id": next_max_id
            }
            return result
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def followers(
            self,
            userid: str | int,
            count: Optional[int] = 12,
            max_id: Optional[int] = None,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:
        """Retrieves a list of users who follow the user specified using the userid argument.

        Arguments :
          - userid (Required)
          - count (Optional) defaultnya 12.
          - max_id (Optional) Arguments to retrieve results from the next API.
          - proxy = (Optional) Used as an intermediary between the client and the server you access. These parameters are an important part of the request configuration and can help you direct traffic through proxy servers that may be needed for various purposes, such as security, anonymity, or access control.

        Keyword Argument:
          - **kwargs
        """
        if not isinstance(userid, (str | int)):
            raise TypeError("Invalid parameter for 'followers'. Expected str, got {}".format(
                type(userid).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'followers'. Expected int, got {}".format(
                type(count).__name__)
            )
        if max_id is not None:
            if not isinstance(max_id, int):
                raise TypeError("Invalid parameter for 'followers'. Expected int, got {}".format(
                    type(max_id).__name__)
                )
        if proxy is not None:
            if not isinstance(proxy, str):
                raise TypeError("Invalid parameter for 'allmedia'. Expected str, got {}".format(
                    type(proxy).__name__)
                )

        user_agent = self.__fake.user_agent()
        url = f"https://www.instagram.com/api/v1/friendships/{userid}/followers/?count={count}&max_id={max_id}"\
            if max_id else f"https://www.instagram.com/api/v1/friendships/{userid}/followers/?count={count}"

        self.__headers["User-Agent"] = user_agent
        self.__headers["X-Asbd-Id"] = "129477"
        self.__headers["X-Csrftoken"] = self.__Csrftoken()
        self.__headers["X-Ig-App-Id"] = "936619743392459"
        resp = self.__session.request(
            method="GET",
            url=url,
            headers=self.__headers,
            timeout=60,
            proxies=proxy,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            datas = []
            for user in data["users"]:
                user_data = {
                    "id": user.get(
                        "pk", ""
                    ),
                    "username": user.get(
                        "username", ""
                    ),
                    "full_name": user.get(
                        "full_name", ""
                    ),
                    "profile_pic_url": user.get(
                        "profile_pic_url", ""
                    ),
                    "is_verified": user.get(
                        "is_verified", ""
                    ),
                }
                datas.append(user_data)
            next_max_id = len(datas)
            result = {
                "result": datas,
                "next_max_id": next_max_id
            }
            return result

        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


if __name__ == "__main__":
    cookies = ''
    sb = InstagramCrawl(cookie=cookies)
