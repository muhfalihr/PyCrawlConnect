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
from helper.utility import Utility


class InstagramCrawl:
    def __init__(self, cookie: str = None):
        self.cookie = cookie
        self.session = Session()
        self.fake = Faker()

        self.headers = dict()
        self.headers["Accept"] = "application/json, text/plain, */*"
        self.headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.headers["Sec-Fetch-Dest"] = "empty"
        self.headers["Sec-Fetch-Mode"] = "cors"
        self.headers["Sec-Fetch-Site"] = "same-site"
        self.headers["Cookie"] = cookie

    def __Csrftoken(self):
        pattern = re.compile(r'csrftoken=([a-zA-Z0-9_-]+)')
        matches = pattern.search(self.cookie)
        if matches:
            csrftoken = matches.group(1)
            return csrftoken
        return None

    def __processmedia(self, item: dict):
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

    def profile(self, username: str, proxy=None):
        user_agent = self.fake.user_agent()
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        self.headers["User-Agent"] = user_agent
        self.headers["X-Asbd-Id"] = "129477"
        self.headers["X-Csrftoken"] = self.__Csrftoken()
        self.headers["X-Ig-App-Id"] = "936619743392459"
        resp = self.session.get(
            url=url,
            headers=self.headers,
            timeout=60,
            proxies=proxy
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
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def media(self, username: str, max_id: str = None, proxy=None):
        user_agent = self.fake.user_agent()
        max_id = f"&max_id={max_id}" if max_id else ""
        url = f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count=33{max_id}"
        self.headers["User-Agent"] = user_agent
        self.headers["X-Asbd-Id"] = "129477"
        self.headers["X-Csrftoken"] = self.__Csrftoken()
        self.headers["X-Ig-App-Id"] = "936619743392459"
        resp = self.session.get(
            url=url,
            headers=self.headers,
            timeout=60,
            proxies=proxy
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
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def comments(self, pk: str, min_id: str = None, proxy=None):
        user_agent = self.fake.user_agent()
        if min_id:
            min_id = min_id.replace("\\", "")
            min_id = unquote(min_id).replace(" ", "")
            min_id = quote(min_id)
            url = f"https://www.instagram.com/api/v1/media/{pk}/comments/?can_support_threading=true&min_id={min_id}&sort_order=popular"
        else:
            url = f"https://www.instagram.com/api/v1/media/{pk}/comments/?can_support_threading=true&permalink_enabled=false"
        self.headers["User-Agent"] = user_agent
        self.headers["X-Asbd-Id"] = "129477"
        self.headers["X-Csrftoken"] = self.__Csrftoken()
        self.headers["X-Ig-App-Id"] = "936619743392459"
        resp = self.session.get(
            url=url,
            headers=self.headers,
            timeout=60,
            proxies=proxy
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
                        "has_more_tail_child_comments"
                    ]
                    for key in KEYS_COMMENT_REMOVE:
                        if key in comment:
                            del comment[key]
                    KEYS_COMMENT_USER = [
                        "is_private",
                        "strong_id__",
                        "fbid_v2",
                        "is_verified",
                        "profile_pic_id"
                    ]
                    if "user" in comment:
                        for key in KEYS_COMMENT_USER:
                            if key in comment["user"]:
                                del comment["user"][key]
            result = {
                "result": {
                    "comments": data["comments"],
                    "next_min_id": data.get("next_min_id", "")
                }
            }
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def be_marked(self, userid: str | int, count: int = 12, cursor: str = None, proxy=None):
        user_agent = self.fake.user_agent()
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
        self.headers["User-Agent"] = user_agent
        self.headers["X-Asbd-Id"] = "129477"
        self.headers["X-Csrftoken"] = self.__Csrftoken()
        self.headers["X-Ig-App-Id"] = "936619743392459"
        resp = self.session.request(
            method="GET",
            url=url,
            headers=self.headers,
            timeout=60,
            proxies=proxy
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
                resp = self.session.request(
                    method="GET",
                    url=url,
                    headers=self.headers,
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
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")


if __name__ == "__main__":
    cookies = "ig_did=3ABCC936-AF74-4336-A4EB-7DA5FFEDA4A3; datr=gSJ5ZVzOZePX4p1BJ0SxrjNN; mid=ZXkihwAEAAFoAqJ6keaV4txQaUuz; ig_nrcb=1; shbid=\"5680\05433964907779\0541735354007:01f78d55aadf11b317d96761a907671b471332d788b998a0a27bef6a3877871f3a26f7ee\"; shbts=\"1703818007\05433964907779\0541735354007:01f7443ecb3f3d9851fcac85e8c737956542507f73840303bff7d5422651291f701fb261\"; csrftoken=UUsIB4w3gqGzHFDPYpJZn49i5vo6Dno1; ds_user_id=63948446931; rur=\"NHA\05463948446931\0541735722517:01f755f224ff5c3c15e07c9836afe974ee5f28e93f742bb5289338368f2501d3291e4412\"; sessionid=63948446931%3AMOcQTY6Lz8PHgd%3A18%3AAYeJpLEp5-QeC0dZ8n-3MA2RGzfk7bInblKDSvV9Vw"
    sb = InstagramCrawl(cookie=cookies)
