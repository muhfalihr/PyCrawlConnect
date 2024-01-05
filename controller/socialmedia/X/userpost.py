import unicodedata
import pytz
import hashlib
import re
import json
import random
import string
import time

from requests.sessions import Session
from urllib.parse import quote
from faker import Faker
from datetime import datetime
from helper.utility import Utility


class Users:
    def __init__(self, cookie=None):
        self.cookie = cookie
        self.session = Session()
        self.fake = Faker()

        self.headers = dict()
        self.headers["Accept"] = "application/json, text/plain, */*"
        self.headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.headers["Sec-Fetch-Dest"] = "empty"
        self.headers["Sec-Fetch-Mode"] = "cors"
        self.headers["Sec-Fetch-Site"] = "same-site"
        self.headers["Authorization"] = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        if cookie is not None:
            self.headers["Cookie"] = cookie

    def __removeallentites(self, keyword: str, datas: dict) -> dict:
        if not isinstance(datas, dict):
            raise TypeError("Invalid parameter for '__removeallentites'. Expected dict, got {}".format(
                type(datas).__name__)
            )
        if not isinstance(keyword, str):
            raise TypeError("Invalid parameter for '__removeallentites'. Expected str, got {}".format(
                type(keyword).__name__)
            )

        KEYS_REMOVE = [
            "id_str",
            "indices",
            "media_key",
            "ext_media_availability",
            "features",
            "sizes",
            "original_info"
        ]
        if keyword in datas["legacy"]:
            if "media" in datas["legacy"][keyword]:
                for e_media in datas["legacy"][keyword]["media"]:
                    for key in self.__generatekey(
                        datas=e_media,
                        keys=KEYS_REMOVE
                    ):
                        del e_media[key]
                        url = e_media["url"]

                for key, value in datas["legacy"].items():
                    if key == "full_text":
                        datas["legacy"].update(
                            {
                                key: value.replace(url, "").rstrip()
                            }
                        )
                return
        return

    def __generatekey(self, datas: dict, keys: list):
        if not isinstance(datas, dict):
            raise TypeError("Invalid parameter for '__generatekey'. Expected dict, got {}".format(
                type(datas).__name__)
            )
        if not isinstance(keys, list):
            raise TypeError("Invalid parameter for '__generatekey'. Expected list, got {}".format(
                type(keys).__name__)
            )
        return [key for key in datas if key in keys]

    def __replacechar(self, text: str, replacement: str):
        if not isinstance(text, str):
            raise TypeError("Invalid parameter for '__replacechar'. Expected str, got {}".format(
                type(text).__name__)
            )
        if not isinstance(replacement, str):
            raise TypeError("Invalid parameter for '__replacechar'. Expected str, got {}".format(
                type(replacement).__name__)
            )

        pattern = re.compile(r'_(.*?)\.jpg')
        matches = pattern.search(
            string=text.split("/")[-1]
        )
        if matches:
            replace = matches.group(1)
            result = text.replace(replace, replacement)
            return result
        return text

    def __guest_token(self):
        user_agent = self.fake.user_agent()
        url = "https://api.twitter.com/1.1/guest/activate.json"
        self.headers["User-Agent"] = user_agent
        resp = self.session.post(
            url=url,
            headers=self.headers,
            timeout=60
        )
        status_code = resp.status_code
        content = resp.json()["guest_token"]
        if status_code == 200:
            self.headers.update({
                "X-Guest-Token": content
            })
            return self.headers["X-Guest-Token"]
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def __Csrftoken(self):
        pattern = re.compile(r'ct0=([a-zA-Z0-9_-]+)')
        matches = pattern.search(self.cookie)
        if matches:
            csrftoken = matches.group(1)
            return csrftoken
        return None

    def __processretweeted(self, data: dict):
        """
        Process retweeted tweet data and return a cleaned dictionary.
        """
        if not isinstance(data, dict):
            raise TypeError("Invalid parameter for '__processretweeted'. Expected dict, got {}".format(
                type(data).__name__)
            )
        try:
            id = data["rest_id"]
            unmention_data = data["unmention_data"]

            views = {
                key: value for key, value in data["views"].items()
                if key != "state"
            } if "views" in data else dict()

            self.__removeallentites(
                keyword="entities",
                datas=data
            )
            self.__removeallentites(
                keyword="extended_entities",
                datas=data
            )

            KEYS_REMOVE = [
                "conversation_id_str",
                "display_text_range",
                "is_quote_status",
                "possibly_sensitive",
                "possibly_sensitive_editable",
                "quoted_status_id_str",
                "quoted_status_permalink",
                "favorited",
                "retweeted",
                "user_id_str",
                "id_str"
            ]

            for key in self.__generatekey(
                datas=data["legacy"],
                keys=KEYS_REMOVE
            ):
                del data["legacy"][key]

            for key, value in data["legacy"].items():
                if key == "created_at":
                    initially = datetime.strptime(
                        value, "%a %b %d %H:%M:%S +0000 %Y"
                    )
                    new = initially.strftime("%Y-%m-%dT%H:%M:%S")
                    data["legacy"].update({key: new})

            legacy = data["legacy"]

            result = {
                "id": id,
                "unmention_data": unmention_data,
                "views": views,
                "legacy": legacy
            }
            return result
        except Exception as e:
            raise f"Error! Message {e}"

    def __processmedia(self, entry: dict = None) -> dict:
        """
        Process media entry data and return a cleaned dictionary.
        """
        if not isinstance(entry, dict):
            raise TypeError("Invalid parameter for '__processmedia'. Expected dict, got {}".format(
                type(entry).__name__)
            )
        try:
            deeper = entry["content"]["itemContent"]["tweet_results"]["result"]
            id = deeper["rest_id"]
            unmention_data = deeper["unmention_data"]

            views = {
                key: value for key, value in deeper["views"].items()
                if key != "state"
            } if "views" in deeper else dict()

            self.__removeallentites(
                keyword="entities",
                datas=deeper
            )
            self.__removeallentites(
                keyword="extended_entities",
                datas=deeper
            )

            KEYS_REMOVE = [
                "conversation_id_str",
                "display_text_range",
                "is_quote_status",
                "possibly_sensitive",
                "possibly_sensitive_editable",
                "quoted_status_id_str",
                "quoted_status_permalink",
                "favorited",
                "retweeted",
                "user_id_str",
                "id_str"
            ]

            for key in self.__generatekey(
                datas=deeper["legacy"],
                keys=KEYS_REMOVE
            ):
                del deeper["legacy"][key]

            legacy = deeper["legacy"]

            for key, value in legacy.items():
                if key == "created_at":
                    initially = datetime.strptime(
                        value, "%a %b %d %H:%M:%S +0000 %Y"
                    )
                    new = initially.strftime("%Y-%m-%dT%H:%M:%S")
                    legacy.update({key: new})

            if "retweeted_status_result" in legacy:
                retweeted_result: dict = legacy["retweeted_status_result"]["result"]
                rw = self.__processretweeted(data=retweeted_result)
                retweeted_result.clear()
                legacy["retweeted_status_result"]["result"].update(rw)

            data = {
                "id": id,
                "unmention_data": unmention_data,
                "views": views,
                "legacy": legacy
            }
            return data
        except Exception as e:
            raise f"Error! Message {e}"

    def search(self, rawquery: str, product: str, count: int = 20, cursor: str = None, proxy=None, **kwargs):
        """Function to search for the intended user from the given rawquery parameter value using the obtained Twitter API.

        Arguments :
          - rawquery
          - product
          - count
          - cursor
          - proxy
          - **kwargs
        """
        if not isinstance(rawquery, str):
            raise TypeError("Invalid parameter for 'search'. Expected str, got {}".format(
                type(rawquery).__name__)
            )
        if not isinstance(product, str):
            raise TypeError("Invalid parameter for 'search'. Expected str, got {}".format(
                type(product).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'search'. Expected int, got {}".format(
                type(count).__name__)
            )
        if cursor is not None:
            if not isinstance(cursor, str):
                raise TypeError("Invalid parameter for 'search'. Expected str, got {}".format(
                    type(cursor).__name__)
                )
        user_agent = self.fake.user_agent()
        params = {
            "variables": {
                "rawQuery": rawquery,
                "count": count,
                "cursor": cursor,
                "querySource": "typed_query",
                "product": product
            } if cursor else {
                "rawQuery": rawquery,
                "count": count,
                "querySource": "typed_query",
                "product": product
            },
            "features": {
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": False,
                "tweet_awards_web_tipping_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_media_download_video_enabled": False,
                "responsive_web_enhance_cards_enabled": False
            }
        }
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://twitter.com/i/api/graphql/Aj1nGkALq99Xg3XI0OZBtw/SearchTimeline?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.headers["User-Agent"] = user_agent
        self.headers["X-Csrf-Token"] = self.__Csrftoken()
        if self.cookie is None:
            self.headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            intructions = data["data"]["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"]
            datas = []
            for index in intructions:
                if index["type"] == "TimelineAddEntries":
                    for entry in index["entries"]:
                        if "itemContent" in entry["content"]:
                            user_results = entry["content"]["itemContent"]["user_results"]["result"]

                            KEYS_RESULT_REMOVE = [
                                "affiliates_highlighted_label",
                                "has_graduated_access",
                                "profile_image_shape"
                            ]
                            for key in self.__generatekey(
                                datas=user_results,
                                keys=KEYS_RESULT_REMOVE
                            ):
                                del user_results[key]

                            KEYS_LEGACY_REMOVE = [
                                "can_dm",
                                "can_media_tag",
                                "fast_followers_count",
                                "has_custom_timelines",
                                "is_translator",
                                "possibly_sensitive",
                                "translator_type",
                                "want_retweets",
                                "withheld_in_countries"
                            ]
                            for key in self.__generatekey(
                                datas=user_results["legacy"],
                                keys=KEYS_LEGACY_REMOVE
                            ):
                                del user_results["legacy"][key]

                            for key, value in user_results["legacy"].items():
                                if key == "profile_image_url_https":
                                    user_results["legacy"].update(
                                        {
                                            key: self.__replacechar(
                                                value,
                                                "400x400"
                                            )
                                        }
                                    )
                                if key == "created_at":
                                    initially = datetime.strptime(
                                        user_results["legacy"][key], "%a %b %d %H:%M:%S +0000 %Y"
                                    )
                                    new = initially.strftime(
                                        "%Y-%m-%dT%H:%M:%S")
                                    user_results["legacy"].update(
                                        {key: new})
                        if entry["content"].get("cursorType", "") == "Bottom":
                            value = entry["content"].get("value", "")
                        datas.append(user_results)

            cursor_value = value

            result = {
                "result": datas,
                "cursor_value": cursor_value
            }
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def profile(self, screen_name: str = None, proxy=None, **kwargs) -> dict:
        """Function to retrieve user profile details from specified screen_name. The result is a data dictionary.

        Arguments:
        - screen_name = username on twitter.
        """
        if not isinstance(screen_name, str):
            raise TypeError("Invalid parameter for 'profile'. Expected str, got {}".format(
                type(screen_name).__name__)
            )
        user_agent = self.fake.user_agent()
        params = {
            "variables": {
                "screen_name": screen_name.lower(),
                "withSafetyModeUserFields": True
            },
            "features": {
                "hidden_profile_likes_enabled": True,
                "hidden_profile_subscriptions_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "subscriptions_verification_info_is_identity_verified_enabled": True,
                "subscriptions_verification_info_verified_since_enabled": True,
                "highlights_tweets_tab_ui_enabled": True,
                "responsive_web_twitter_article_notes_tab_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True
            },
            "fieldToggles": {
                "withAuxiliaryUserLabels": True
            }
        }
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        fieldToggles = quote(params["fieldToggles"])
        url = "https://api.twitter.com/graphql/NimuplG1OB7Fd2btCLdBOw/UserByScreenName?variables={variables}&features={features}&fieldToggles={fieldToggles}".format(
            variables=variables,
            features=features,
            fieldToggles=fieldToggles
        )
        self.headers["User-Agent"] = user_agent
        if self.cookie is None:
            self.headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            result: dict = data["data"]["user"]["result"]
            KEYS_RESULT_REMOVE = [
                "affiliates_highlighted_label",
                "has_graduated_access",
                "profile_image_shape",
                "smart_blocked_by",
                "smart_blocking",
                "legacy_extended_profile",
                "is_profile_translatable",
                "has_hidden_likes_on_profile",
                "has_hidden_subscriptions_on_profile",
                "verification_info",
                "highlights_info",
                "creator_subscriptions_count"
            ]
            for key in self.__generatekey(
                datas=result,
                keys=KEYS_RESULT_REMOVE
            ):
                del result[key]

            KEYS_LEGACY_REMOVE = [
                "can_dm",
                "can_media_tag",
                "fast_followers_count",
                "has_custom_timelines",
                "is_translator",
                "possibly_sensitive",
                "translator_type",
                "want_retweets",
                "withheld_in_countries"
            ]
            for key in self.__generatekey(
                datas=result["legacy"],
                keys=KEYS_LEGACY_REMOVE
            ):
                del result["legacy"][key]

            for key, value in result["legacy"].items():
                if key == "profile_image_url_https":
                    result["legacy"].update(
                        {
                            key: self.__replacechar(
                                value,
                                "400x400"
                            )
                        }
                    )
                if key == "created_at":
                    initially = datetime.strptime(
                        result["legacy"][key], "%a %b %d %H:%M:%S +0000 %Y"
                    )
                    new = initially.strftime("%Y-%m-%dT%H:%M:%S")
                    result["legacy"].update({key: new})
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def recomendation(self, userId: str | int = None, limit: str | int = None, proxy=None) -> dict:
        """Function to retrieve recommended Twitter users according to the userId entered. The result is a data dictionary.

        Arguments:
        - userId = ID of the Twitter user.
        - limit = number of recommended users.
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'profile'. Expected str|int, got {}".format(
                type(userId).__name__)
            )

        user_agent = self.fake.user_agent()
        params = {
            "include_profile_interstitial_type": 1,
            "include_blocking": 1,
            "include_blocked_by": 1,
            "include_followed_by": 1,
            "include_want_retweets": 1,
            "include_mute_edge": 1,
            "include_can_dm": 1,
            "include_can_media_tag": 1,
            "include_ext_has_nft_avatar": 1,
            "include_ext_is_blue_verified": 1,
            "include_ext_verified_type": 1,
            "include_ext_profile_image_shape": 1,
            "skip_status": 1,
            "pc": True,
            "display_location": "profile_accounts_sidebar",
            "limit": limit,
            "user_id": userId,
            "ext": "mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,birdwatchPivot,superFollowMetadata,unmentionInfo,editControl"
        }
        url = "https://api.twitter.com/1.1/users/recommendations.json"

        self.headers["User-Agent"] = user_agent
        if self.cookie is None:
            self.headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.session.get(
            url=url,
            params=params,
            headers=self.headers,
            timeout=60,
            proxies=proxy
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            datas = json.loads(response)

            KEYS_REMOVE = [
                "protected",
                "fast_followers_count",
                "normal_followers_count",
                "utc_offset",
                "time_zone",
                "geo_enabled",
                "verified",
                "contributors_enabled",
                "is_translator",
                "is_translation_enabled",
                "profile_background_color",
                "profile_background_tile",
                "profile_link_color",
                "profile_sidebar_border_color",
                "profile_sidebar_fill_color",
                "profile_text_color",
                "profile_use_background_image",
                "default_profile",
                "default_profile_image",
                "pinned_tweet_ids",
                "pinned_tweet_ids_str",
                "has_custom_timelines",
                "can_dm",
                "can_media_tag",
                "following",
                "follow_request_sent",
                "notifications",
                "muting",
                "blocking",
                "blocked_by",
                "want_retweets",
                "advertiser_account_type",
                "advertiser_account_service_levels",
                "analytics_type",
                "profile_interstitial_type",
                "business_profile_state",
                "translator_type",
                "withheld_in_countries",
                "followed_by",
                "ext_highlighted_label",
                "ext_is_blue_verified",
                "require_some_consent"
            ]

            for data in datas:
                deeper = data["user"]
                for key in self.__generatekey(
                    datas=deeper,
                    keys=KEYS_REMOVE
                ):
                    del deeper[key]

                for key, value in deeper.items():
                    if key == "created_at":
                        initially = datetime.strptime(
                            value, "%a %b %d %H:%M:%S +0000 %Y"
                        )
                        new = initially.strftime("%Y-%m-%dT%H:%M:%S")
                        deeper.update({key: new})

            result = {
                "result": datas
            }
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def posts(self, userId: int | str = None, proxy=None, **kwargs) -> dict:
        """The function to retrieve details from a user's post uses the userId input obtained when retrieving user profile details.
        The result is a data dictionary.

        Arguments:
        - userId = ID of the Twitter user.
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'posts'. Expected str|int, got {}".format(
                type(userId).__name__)
            )
        user_agent = self.fake.user_agent()
        params = {
            "variables": {
                "userId": userId,
                "count": 20,
                "includePromotedContent": True,
                "withQuickPromoteEligibilityTweetFields": True,
                "withVoice": True,
                "withV2Timeline": True
            },
            "features": {
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": False,
                "tweet_awards_web_tipping_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_media_download_video_enabled": False,
                "responsive_web_enhance_cards_enabled": False
            }
        }
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://api.twitter.com/graphql/V1ze5q3ijDS1VeLwLY0m7g/UserTweets?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.headers["User-Agent"] = user_agent
        if self.cookie is None:
            self.headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            instructions = data["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"]
            datas = []
            for index, value in enumerate(instructions):
                if isinstance(value, dict) and value["type"] == "TimelinePinEntry":
                    deep = instructions[index]

                    entry = deep["entry"]
                    data = self.__processmedia(entry=entry)
                    datas.append(data)

                if isinstance(value, dict) and value["type"] == "TimelineAddEntries":
                    deep = instructions[index]

                    cursor_value = ""
                    for entry in deep["entries"]:
                        if entry:
                            if "itemContent" in entry["content"]:
                                data = self.__processmedia(entry=entry)
                                datas.append(data)
                            if entry["content"].get("cursorType", "") == "Bottom":
                                cursor_value += entry["content"].get(
                                    "value", "")

            result = {
                "result": datas,
                "cursor_value": cursor_value
            }
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def media(self, userId: str | int = None, count: int = 20, cursor: str = None, proxy=None, **kwargs) -> dict:
        """The function to retrieve details from the user's post uses the screen_name input. The result is a data dictionary.

        Arguments:
        - userId
        - count
        - cursor
        - proxy
        - **kwargs
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'media'. Expected str|int, got {}".format(
                type(userId).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'search'. Expected int, got {}".format(
                type(count).__name__)
            )
        if cursor is not None:
            if not isinstance(cursor, str):
                raise TypeError("Invalid parameter for 'search'. Expected str, got {}".format(
                    type(cursor).__name__)
                )
        user_agent = self.fake.user_agent()
        params = {
            "variables": {
                "userId": userId,
                "count": count,
                "includePromotedContent": False,
                "withClientEventToken": False,
                "withBirdwatchNotes": False,
                "withVoice": True,
                "withV2Timeline": True
            } if cursor is None else {
                "userId": userId,
                "count": count,
                "cursor": cursor,
                "includePromotedContent": False,
                "withClientEventToken": False,
                "withBirdwatchNotes": False,
                "withVoice": True,
                "withV2Timeline": True
            },
            "features": {
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": False,
                "tweet_awards_web_tipping_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_media_download_video_enabled": False,
                "responsive_web_enhance_cards_enabled": False
            }

        }
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://twitter.com/i/api/graphql/oMVVrI5kt3kOpyHHTTKf5Q/UserMedia?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.headers["User-Agent"] = user_agent
        if self.cookie is None:
            self.headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            instructions = data["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"]
            datas = []
            for index, value in enumerate(instructions):
                if isinstance(value, dict) and value["type"] == "TimelineAddEntries":
                    deep = instructions[index]

                    cursor_value = ""
                    for entry in deep["entries"]:
                        for key in entry:
                            if key == "content":
                                for key_content in entry[key]:
                                    if "items" in key_content:
                                        for item in entry[key]["items"]:
                                            tweet_results = item["item"]["itemContent"]["tweet_results"]["result"]
                                            twr = self.__processretweeted(
                                                data=tweet_results)
                                            datas.append(twr)
                                    if "value" in key_content:
                                        cursor_value += entry[key].get(
                                            "value", "")
            result = {
                "result": datas,
                "cursor_value": cursor_value
            }
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")


if __name__ == "__main__":
    cookie = ""
    sb = Users()
