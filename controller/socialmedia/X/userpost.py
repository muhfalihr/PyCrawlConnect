import unicodedata
import pytz
import hashlib
import re
import json
import random
import string
import time

from requests.sessions import Session
from urllib.parse import quote, unquote
from faker import Faker
from datetime import datetime
from helper.utility import Utility


class XCrawl:
    def __init__(self, cookie=None):
        self.__cookie = cookie
        self.__session = Session()
        self.__fake = Faker()

        self.__headers = dict()
        self.__headers["Accept"] = "application/json, text/plain, */*"
        self.__headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.__headers["Sec-Fetch-Dest"] = "empty"
        self.__headers["Sec-Fetch-Mode"] = "cors"
        self.__headers["Sec-Fetch-Site"] = "same-site"
        self.__headers["Authorization"] = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        if cookie is not None:
            self.__headers["Cookie"] = cookie

        self.__generatekey = lambda datas, keys:  [
            key for key in datas if key in keys
        ]

    def __guest_token(self):
        user_agent = self.__fake.user_agent()
        url = "https://api.twitter.com/1.1/guest/activate.json"
        self.__headers["User-Agent"] = user_agent
        resp = self.__session.post(
            url=url,
            headers=self.__headers,
            timeout=60
        )
        status_code = resp.status_code
        content = resp.json()["guest_token"]
        if status_code == 200:
            self.__headers.update({
                "X-Guest-Token": content
            })
            return self.__headers["X-Guest-Token"]
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def __Csrftoken(self):
        pattern = re.compile(r'ct0=([a-zA-Z0-9_-]+)')
        matches = pattern.search(self.__cookie)
        if matches:
            csrftoken = matches.group(1)
            return csrftoken
        return None

    def __buildparams(self, **kwargs):
        func_name = kwargs["func_name"]
        match func_name:
            case "search":
                rawquery = kwargs["rawquery"]
                count = kwargs["count"]
                cursor = kwargs["cursor"]
                product = kwargs["product"]

                variables = {
                    "rawQuery": f"{rawquery}",
                    "count": count,
                    "cursor": f"{cursor}",
                    "querySource": "typed_query",
                    "product": f"{product}"
                } if cursor else {
                    "rawQuery": f"{rawquery}",
                    "count": count,
                    "querySource": "typed_query",
                    "product": f"{product}"
                }

            case "profile":
                screen_name = kwargs["screen_name"]

                variables = {
                    "screen_name": screen_name.lower(),
                    "withSafetyModeUserFields": True
                }

                fieldToggles = {"withAuxiliaryUserLabels": False}

            case "posts":
                userId = kwargs["userId"]
                count = kwargs["count"]
                cursor = kwargs["cursor"]

                variables = {
                    "userId": f"{userId}",
                    "count": count,
                    "cursor": f"{cursor}",
                    "includePromotedContent": True,
                    "withQuickPromoteEligibilityTweetFields": True,
                    "withVoice": True,
                    "withV2Timeline": True
                } if cursor else {
                    "userId": f"{userId}",
                    "count": count,
                    "includePromotedContent": True,
                    "withQuickPromoteEligibilityTweetFields": True,
                    "withVoice": True,
                    "withV2Timeline": True
                }

            case "media" | "likes":
                userId = kwargs["userId"]
                count = kwargs["count"]
                cursor = kwargs["cursor"]

                variables = {
                    "userId": f"{userId}",
                    "count": count,
                    "cursor": f"{cursor}",
                    "includePromotedContent": False,
                    "withClientEventToken": False,
                    "withBirdwatchNotes": False,
                    "withVoice": True,
                    "withV2Timeline": True
                } if cursor else {
                    "userId": f"{userId}",
                    "count": count,
                    "includePromotedContent": False,
                    "withClientEventToken": False,
                    "withBirdwatchNotes": False,
                    "withVoice": True,
                    "withV2Timeline": True
                }

            case "replies":
                userId = kwargs["userId"]
                count = kwargs["count"]
                cursor = kwargs["cursor"]

                variables = {
                    "userId": f"{userId}",
                    "count": count,
                    "cursor": f"{cursor}",
                    "includePromotedContent": True,
                    "withCommunity": True,
                    "withVoice": True,
                    "withV2Timeline": True
                } if cursor else {
                    "userId": f"{userId}",
                    "count": count,
                    "includePromotedContent": True,
                    "withCommunity": True,
                    "withVoice": True,
                    "withV2Timeline": True
                }

            case "recomendation":
                limit = kwargs["limit"]
                userId = kwargs["userId"]

            case "tweetdetail":
                focalTweetId = kwargs["focalTweetId"]
                controller_data = kwargs["controller_data"]
                cursor = kwargs["cursor"]

                variables = {
                    "focalTweetId": f"{focalTweetId}",
                    "cursor": f"{cursor}",
                    "referrer": "tweet",
                    "controller_data": f"{controller_data}",
                    "with_rux_injections": False,
                    "includePromotedContent": True,
                    "withCommunity": True,
                    "withQuickPromoteEligibilityTweetFields": True,
                    "withBirdwatchNotes": True,
                    "withVoice": True,
                    "withV2Timeline": True
                } if cursor else {
                    "focalTweetId": f"{focalTweetId}",
                    "with_rux_injections": False,
                    "includePromotedContent": True,
                    "withCommunity": True,
                    "withQuickPromoteEligibilityTweetFields": True,
                    "withBirdwatchNotes": True,
                    "withVoice": True,
                    "withV2Timeline": True
                }

                fieldToggles = {"withArticleRichContentState": False}

            case "following" | "followers" | "blue_verified_followers" | "followers_you_know":
                userId = kwargs["userId"]
                count = kwargs["count"]

                variables = {
                    "userId": f"{userId}",
                    "count": count,
                    "includePromotedContent": False
                }

        params = {
            "variables": variables,
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
            } if func_name in [
                "search", "posts", "media",
                "replies", "likes", "tweetdetail",
                "following", "followers", "blue_verified_followers",
                "followers_you_know"
            ] else {
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
            }
        } if func_name != "recomendation" else {
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
            "user_id": f"{userId}",
            "ext": "mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,birdwatchPivot,superFollowMetadata,unmentionInfo,editControl"
        }
        if func_name in ["profile", "tweetdetail"]:
            params.update(
                {
                    "fieldToggles": fieldToggles
                }
            )

        return params

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
            "original_info",
            "additional_media_info"
        ]
        if keyword in datas["legacy"]:
            KEY_CHECK = ["hashtags", "media", "symbols",
                         "timestamps", "urls", "user_mentions"]
            for kc in KEY_CHECK:
                if kc in datas["legacy"][keyword]:
                    if "hashtags" in datas["legacy"][keyword] and datas["legacy"][keyword]["hashtags"]:
                        hashtags = []
                        try:
                            for e_hashtag in datas["legacy"][keyword]["hashtags"]:
                                hashtags.append(e_hashtag["text"])
                            datas["legacy"][keyword].update(
                                {"hashtags": hashtags})
                        except TypeError:
                            pass

                    if "media" in datas["legacy"][keyword] and datas["legacy"][keyword]["media"]:
                        for e_media in datas["legacy"][keyword]["media"]:
                            for key in self.__generatekey(
                                datas=e_media,
                                keys=KEYS_REMOVE
                            ):
                                del e_media[key]
                                if "video_info" in e_media:
                                    if "aspect_ratio" in e_media["video_info"]:
                                        del e_media["video_info"]["aspect_ratio"]
                                url = e_media["url"]

                            for key, value in datas["legacy"].items():
                                if key == "full_text":
                                    datas["legacy"].update(
                                        {
                                            key: value.replace(
                                                url, "").rstrip()
                                        }
                                    )

                    if "symbols" in datas["legacy"][keyword] and datas["legacy"][keyword]["symbols"]:
                        for e_symbol in datas["legacy"][keyword]["symbols"]:
                            for key in self.__generatekey(
                                datas=e_symbol,
                                keys=KEYS_REMOVE
                            ):
                                del e_symbol[key]

                    if "timestamps" in datas["legacy"][keyword] and datas["legacy"][keyword]["timestamps"]:
                        for e_tt in datas["legacy"][keyword]["timestamps"]:
                            for key in self.__generatekey(
                                datas=e_tt,
                                keys=KEYS_REMOVE
                            ):
                                del e_tt[key]

                    if "urls" in datas["legacy"][keyword] and datas["legacy"][keyword]["urls"]:
                        for e_url in datas["legacy"][keyword]["urls"]:
                            for key in self.__generatekey(
                                datas=e_url,
                                keys=KEYS_REMOVE
                            ):
                                del e_url[key]

                    if "user_mentions" in datas["legacy"][keyword] and datas["legacy"][keyword]["user_mentions"]:
                        for e_um in datas["legacy"][keyword]["user_mentions"]:
                            for key in self.__generatekey(
                                datas=e_um,
                                keys=[kr for kr in KEYS_REMOVE if kr != "id_str"]
                            ):
                                del e_um[key]

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

    def __processuserresults(self, data: dict):
        """
        Process user results data and return a cleaned dictionary.
        """
        if not isinstance(data, dict):
            raise TypeError("Invalid parameter for '__processuserresults'. Expected dict, got {}".format(
                type(data).__name__)
            )
        datas = data["user_results"]["result"]
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
            datas=datas,
            keys=KEYS_RESULT_REMOVE
        ):
            del datas[key]

        KEYS_LEGACY_REMOVE = [
            "can_dm",
            "can_media_tag",
            "created_at",
            "default_profile",
            "default_profile_image",
            "fast_followers_count",
            "favourites_count",
            "followers_count",
            "friends_count",
            "has_custom_timelines",
            "is_translator",
            "listed_count",
            "media_count",
            "normal_followers_count",
            "pinned_tweet_ids_str",
            "possibly_sensitive",
            "statuses_count",
            "translator_type",
            "want_retweets",
            "withheld_in_countries"
        ]
        for key in self.__generatekey(
            datas=datas["legacy"],
            keys=KEYS_LEGACY_REMOVE
        ):
            del datas["legacy"][key]

        for key, value in datas["legacy"].items():
            if key == "entities":
                for entities_key in datas["legacy"][key]:
                    if "urls" in datas["legacy"][key][entities_key]:
                        if datas["legacy"][key][entities_key]["urls"]:
                            for item in datas["legacy"][key][entities_key]["urls"]:
                                del item["indices"]
            if key == "profile_image_url_https":
                datas["legacy"].update(
                    {
                        key: self.__replacechar(
                            value,
                            "400x400"
                        )
                    }
                )
            if key == "created_at":
                initially = datetime.strptime(
                    datas["legacy"][key], "%a %b %d %H:%M:%S +0000 %Y"
                )
                new = initially.strftime("%Y-%m-%dT%H:%M:%S")
                datas["legacy"].update({key: new})
        datas.update(
            {
                "legacy": {
                    "name": datas["legacy"].get(
                        "name", ""
                    ),
                    "screen_name": datas["legacy"].get(
                        "screen_name", ""
                    ),
                    "verified": datas["legacy"].get(
                        "verified", ""
                    ),
                    "description": datas["legacy"].get(
                        "description", ""
                    ),
                    "entities": datas["legacy"].get(
                        "entities", ""
                    ),
                    "location": datas["legacy"].get(
                        "location", ""
                    ),
                    "profile_banner_url": datas["legacy"].get(
                        "profile_banner_url", ""
                    ),
                    "profile_image_url_https": datas["legacy"].get(
                        "profile_image_url_https", ""
                    ),
                    "profile_interstitial_type": datas["legacy"].get(
                        "profile_interstitial_type", ""
                    ),
                    "url": datas["legacy"].get(
                        "url", ""
                    )
                }
            }
        )
        if "professional" not in datas:
            datas.update({"professional": {}})
        return datas

    def __processretweeted(self, data: dict) -> dict:
        """
        Process retweeted tweet data and return a cleaned dictionary.
        """
        if not isinstance(data, dict):
            raise TypeError("Invalid parameter for '__processretweeted'. Expected dict, got {}".format(
                type(data).__name__)
            )

        id = data["rest_id"] if "rest_id" in data else ""

        views = {
            key: value for key, value in data["views"].items()
            if key != "state"
        } if "views" in data else dict()

        core = {}
        if "core" in data:
            core = self.__processuserresults(data=data["core"])

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
            "id_str",
            "place"
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
            "views": views,
            "core": core,
            "legacy": legacy
        }
        return result

    def __processmedia(self, entry: dict = None) -> dict:
        """
        Process media entry data and return a cleaned dictionary.
        """
        if not isinstance(entry, dict):
            raise TypeError("Invalid parameter for '__processmedia'. Expected dict, got {}".format(
                type(entry).__name__)
            )

        if "content" in entry:
            deeper = entry["content"]["itemContent"]["tweet_results"]["result"]
        else:
            if "rest_id" in entry:
                deeper = entry
            else:
                deeper = entry["tweet"]

        id = deeper["rest_id"] if "rest_id" in deeper else ""
        views = {
            key: value for key, value in deeper["views"].items()
            if key != "state"
        } if "views" in deeper else dict()

        core = {}
        if "core" in deeper:
            core = self.__processuserresults(data=deeper["core"])

        legacy = {}
        if "legacy" in deeper:
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
                "id_str",
                "place"
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
                    new = initially.strftime(
                        "%Y-%m-%dT%H:%M:%S")
                    legacy.update(
                        {key: new})

            if "retweeted_status_result" in legacy:
                retweeted_result: dict = legacy["retweeted_status_result"]["result"]
                rw = self.__processretweeted(data=retweeted_result)
                retweeted_result.clear()
                legacy["retweeted_status_result"]["result"].update(rw)
            elif "retweeted_status_result" not in legacy:
                legacy.update(
                    {
                        "retweeted_status_result": {}
                    }
                )

        data = {
            "id": id,
            "views": views,
            "core": core,
            "legacy": legacy
        }
        return data

    def __coreprocess(self, instructions: list, tweetdetail: bool = False) -> dict:
        if not isinstance(instructions, list):
            raise TypeError("Invalid parameter for '__coreprocess'. Expected list, got {}".format(
                type(instructions).__name__)
            )

        datas = []
        for index, value in enumerate(instructions):
            if isinstance(value, dict) and value["type"] == "TimelineAddEntries":
                deep = instructions[index]

                cursor_value = ""
                for entry in deep["entries"]:
                    for key in entry:
                        if key == "content":
                            for key_content in entry[key]:
                                if key_content == "itemContent":
                                    if "tweet_results" in entry[key][key_content]:
                                        tweet_results = entry[key][key_content]["tweet_results"]["result"]
                                        twr = self.__processmedia(
                                            entry=tweet_results)
                                        datas.append(twr)
                                if key_content == "items":
                                    for item in entry[key][key_content]:
                                        if "tweet_results" in item["item"]["itemContent"]:
                                            tweet_results = item["item"]["itemContent"]["tweet_results"]["result"]
                                            twr = self.__processmedia(
                                                entry=tweet_results)
                                            datas.append(twr)

                            if tweetdetail:
                                if "itemContent" in entry[key]:
                                    if entry[key]["itemContent"].get("cursorType", "") == "Bottom":
                                        cursor_value += entry[key]["itemContent"].get(
                                            "value", ""
                                        )

                            if entry[key].get("cursorType", "") == "Bottom":
                                cursor_value += entry[key].get(
                                    "value", ""
                                )

            if isinstance(value, dict) and value["type"] == "TimelineAddToModule":
                deep = instructions[index]

                for entry in deep["moduleItems"]:
                    if "item" in entry:
                        deeper = entry["item"]["itemContent"]["tweet_results"]["result"]
                        tweet_results = self.__processmedia(
                            entry=deeper
                        )
                        datas.append(tweet_results)

        result = {
            "result": datas,
            "cursor_value": cursor_value
        }
        return result

    def search(self, rawquery: str, product: str, count: int = 20, cursor: str = None, proxy=None, **kwargs) -> dict:
        """Function to search for the intended user from the given rawquery parameter value using the obtained Twitter API.

        Arguments :
          - rawquery (Required) The raw query to search for.
          - product (Required) Choose between Top, Latest, People, and Media.
          - count (Optional) Amount of data.
          - cursor (Optional) The key used to load the next page.
        """
        if isinstance(rawquery, str):
            rawquery = quote(rawquery)
        elif not isinstance(rawquery, str):
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
        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            rawquery=rawquery,
            product=product,
            count=count,
            cursor=cursor
        )
        for key in params:
            params.update({key: Utility.convertws(params[key])})
            if key == "variables":
                pattern = re.compile(r'"rawQuery":"([^"]+)"')
                matches = pattern.search(params["variables"])
                if matches:
                    rq_value = matches.group(1)
                    params.update(
                        {
                            "variables": params["variables"].replace(
                                rq_value, unquote(rq_value)
                            )
                        }
                    )
        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://twitter.com/i/api/graphql/Aj1nGkALq99Xg3XI0OZBtw/SearchTimeline?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.request(
            method="GET",
            url=url,
            params=params,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            intructions = data["data"]["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"]
            datas = []
            for index, value in enumerate(intructions):
                if isinstance(value, dict) and value["type"] == "TimelineAddEntries":
                    deep = intructions[index]

                    cursor_value = ""
                    for entry in deep["entries"]:
                        match product:
                            case "People":
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
                                    cursor_value += entry["content"].get(
                                        "value", ""
                                    )
                                datas.append(user_results)

                            case "Media":
                                for key_content in entry["content"]:
                                    if "items" in key_content:
                                        for item in entry["content"]["items"]:
                                            if "item" in item:
                                                if "itemContent" in item["item"]:
                                                    deeper = item["item"]["itemContent"]["tweet_results"]["result"]
                                                    tweet_results = self.__processmedia(
                                                        entry=deeper
                                                    )
                                                    datas.append(
                                                        tweet_results
                                                    )

                                if entry["content"].get("cursorType", "") == "Bottom":
                                    cursor_value += entry["content"].get(
                                        "value", ""
                                    )

                            case "Top" | "Latest":
                                if "itemContent" in entry["content"]:
                                    deeper = entry["content"]["itemContent"]["tweet_results"]["result"]
                                    tweet_results = self.__processmedia(
                                        entry=deeper)
                                    datas.append(tweet_results)
                                if entry["content"].get("cursorType", "") == "Bottom":
                                    cursor_value += entry["content"].get(
                                        "value", ""
                                    )
                if isinstance(value, dict) and value["type"] == "TimelineAddToModule":
                    deep = intructions[index]

                    for entry in deep["moduleItems"]:
                        if "item" in entry:
                            deeper = entry["item"]["itemContent"]["tweet_results"]["result"]
                            tweet_results = self.__processmedia(
                                entry=deeper)
                            datas.append(tweet_results)

                if isinstance(value, dict) and value["type"] == "TimelineReplaceEntry":
                    deep = intructions[index]

                    entry = deep["entry"]
                    if not cursor_value:
                        if entry["content"].get("cursorType", "") == "Bottom":
                            cursor_value += entry["content"].get(
                                "value", ""
                            )

            if not datas:
                raise Exception(
                    "Error! status code 404 : Not Found"
                )

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
        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            screen_name=screen_name
        )
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
        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
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

    def recomendation(self, userId: str | int, limit: int = 20, proxy=None) -> dict:
        """Function to retrieve recommended Twitter users according to the userId entered. The result is a data dictionary.

        Arguments:
        - userId = ID of the Twitter user.
        - limit = number of recommended users.
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'recomendation'. Expected str|int, got {}".format(
                type(userId).__name__)
            )
        if isinstance(limit, str) and limit.isdigit():
            limit = int(limit)
        elif not isinstance(limit, int):
            raise TypeError("Invalid parameter for 'recomendation'. Expected int, got {}".format(
                type(limit).__name__)
            )

        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            userId=userId,
            limit=limit
        )
        url = "https://api.twitter.com/1.1/users/recommendations.json"

        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.get(
            url=url,
            params=params,
            headers=self.__headers,
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

    def posts(self, userId: int | str, count: int = 20, cursor: str = None, proxy=None, **kwargs) -> dict:
        """The function to retrieve details from a user's post uses the userId input obtained when retrieving user profile details.
        The result is a data dictionary.

        Arguments :
          - userId (Required) The ID of the rest_id key contained in the search function results.
          - count (Optional) Amount of data.
          - cursor (Optional) The key used to load the next page.
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'posts'. Expected str|int, got {}".format(
                type(userId).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'posts'. Expected int, got {}".format(
                type(count).__name__)
            )
        if cursor is not None:
            if not isinstance(cursor, str):
                raise TypeError("Invalid parameter for 'posts'. Expected str, got {}".format(
                    type(cursor).__name__)
                )
        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            userId=userId,
            count=count,
            cursor=cursor
        )
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://api.twitter.com/graphql/V1ze5q3ijDS1VeLwLY0m7g/UserTweets?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
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
                                    "value", ""
                                )

                if isinstance(value, dict) and value["type"] == "TimelineAddToModule":
                    deep = instructions[index]

                    for entry in deep["moduleItems"]:
                        if "item" in entry:
                            deeper = entry["item"]["itemContent"]["tweet_results"]["result"]
                            tweet_results = self.__processmedia(
                                entry=deeper)
                            datas.append(tweet_results)

            result = {
                "result": datas,
                "cursor_value": cursor_value
            }
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def media(self, userId: str | int, count: int = 20, cursor: str = None, proxy=None, **kwargs) -> dict:
        """The function to retrieve details from the user's post uses the screen_name input. The result is a data dictionary.

        Arguments :
          - userId (Required) The ID of the rest_id key contained in the search function results.
          - count (Optional) Amount of data.
          - cursor (Optional) The key used to load the next page.
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'media'. Expected str|int, got {}".format(
                type(userId).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'media'. Expected int, got {}".format(
                type(count).__name__)
            )
        if cursor is not None:
            if not isinstance(cursor, str):
                raise TypeError("Invalid parameter for 'media'. Expected str, got {}".format(
                    type(cursor).__name__)
                )
        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            userId=userId,
            count=count,
            cursor=cursor
        )
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://twitter.com/i/api/graphql/oMVVrI5kt3kOpyHHTTKf5Q/UserMedia?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            instructions = data["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"]
            result = self.__coreprocess(instructions=instructions)
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def replies(self, userId: str | int, count: int = 20, cursor: str = None, proxy=None, **kwargs):
        """Retrieve other users' Twitter posts that are replied to by the user whose user ID we input.

        Arguments :
          - userId (Required) The ID of the rest_id key contained in the search function results.
          - count (Optional) Amount of data.
          - cursor (Optional) The key used to load the next page.
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'replies'. Expected str|int, got {}".format(
                type(userId).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'replies'. Expected int, got {}".format(
                type(count).__name__)
            )
        if cursor is not None:
            if not isinstance(cursor, str):
                raise TypeError("Invalid parameter for 'replies'. Expected str, got {}".format(
                    type(cursor).__name__)
                )
        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            userId=userId,
            count=count,
            cursor=cursor
        )
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://twitter.com/i/api/graphql/16nOjYqEdV04vN6-rgg8KA/UserTweetsAndReplies?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            instructions = data["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"]
            result = self.__coreprocess(instructions=instructions)
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def likes(self, userId: str | int, count: int = 20, cursor: str = None, proxy=None, **kwargs):
        """Retrieve other users' Twitter posts that the user likes from the userId input.

        Arguments :
          - userId (Required) The ID of the rest_id key contained in the search function results.
          - count (Optional) Amount of data.
          - cursor (Optional) The key used to load the next page.
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'replies'. Expected str|int, got {}".format(
                type(userId).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'replies'. Expected int, got {}".format(
                type(count).__name__)
            )
        if cursor is not None:
            if not isinstance(cursor, str):
                raise TypeError("Invalid parameter for 'replies'. Expected str, got {}".format(
                    type(cursor).__name__)
                )
        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            userId=userId,
            count=count,
            cursor=cursor
        )
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://twitter.com/i/api/graphql/NpYLg91N41FVTp-5l4Ntow/Likes?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            instructions = data["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"]
            result = self.__coreprocess(instructions=instructions)
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def tweetdetail(
            self,
            focalTweetId: str | int,
            controller_data: str = "DAACDAABDAABCgABAAAAAAAAAAAKAAkXK+YwNdoAAAAAAAA=",
            cursor: str = None,
            proxy=None,
            **kwargs
    ):
        """Retrieves tweet details from each user's post.

        Arguments :
          - focalTweetId (Required) Taken from the "rest_id" key value contained in the return results of other functions.
          - controller_data (Don't change it)
          - cursor (Optional) The key used to load the next page.
        """
        if not isinstance(focalTweetId, (str | int)):
            raise TypeError("Invalid parameter for 'tweetdetail'. Expected str, got {}".format(
                type(focalTweetId).__name__)
            )
        if not isinstance(controller_data, str):
            raise TypeError("Invalid parameter for 'tweetdetail'. Expected str, got {}".format(
                type(controller_data).__name__)
            )
        if cursor is not None:
            if not isinstance(cursor, str):
                raise TypeError("Invalid parameter for 'tweetdetail'. Expected str, got {}".format(
                    type(cursor).__name__)
                )
        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            focalTweetId=focalTweetId,
            controller_data=controller_data,
            cursor=cursor
        )
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        fieldToggles = quote(params["fieldToggles"])
        url = "https://twitter.com/i/api/graphql/-H4B_lJDEA-O_7_qWaRiyg/TweetDetail?variables={variables}&features={features}&fieldToggles={fieldToggles}".format(
            variables=variables,
            features=features,
            fieldToggles=fieldToggles
        )
        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            instructions = data["data"]["threaded_conversation_with_injections_v2"]["instructions"]
            result = self.__coreprocess(
                instructions=instructions, tweetdetail=True
            )
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def following(self, userId: str | int, count: int = 20, proxy=None, **kwargs):
        """

        Arguments :
          - userId (Required) The ID of the rest_id key contained in the search function results.
          - count (Optional) Amount of data.
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'following'. Expected str|int, got {}".format(
                type(userId).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'following'. Expected int, got {}".format(
                type(count).__name__)
            )
        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            userId=userId,
            count=count
        )
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://twitter.com/i/api/graphql/0yD6Eiv23DKXRDU9VxlG2A/Following?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            instructions = data["data"]["user"]["result"]["timeline"]["timeline"]["instructions"]
            datas = []
            for index, value in enumerate(instructions):
                if isinstance(value, dict) and value["type"] == "TimelineAddEntries":
                    datas = [
                        self.__processuserresults(
                            entry["content"]["itemContent"]
                        )
                        for entry in instructions[index]["entries"]
                        if "content" in entry
                        and "itemContent" in entry["content"]
                        and "user_results" in entry["content"]["itemContent"]
                    ]

            result = {
                "result": datas
            }
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def followers(self, userId: str | int, count: int = 20, proxy=None, **kwargs):
        """

        Arguments :
          - userId (Required) The ID of the rest_id key contained in the search function results.
          - count (Optional) Amount of data.
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'following'. Expected str|int, got {}".format(
                type(userId).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'following'. Expected int, got {}".format(
                type(count).__name__)
            )
        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            userId=userId,
            count=count
        )
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://twitter.com/i/api/graphql/3_7xfjmh897x8h_n6QBqTA/Followers?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            instructions = data["data"]["user"]["result"]["timeline"]["timeline"]["instructions"]
            datas = []
            for index, value in enumerate(instructions):
                if isinstance(value, dict) and value["type"] == "TimelineAddEntries":
                    datas = [
                        self.__processuserresults(
                            entry["content"]["itemContent"]
                        )
                        for entry in instructions[index]["entries"]
                        if "content" in entry
                        and "itemContent" in entry["content"]
                        and "user_results" in entry["content"]["itemContent"]
                    ]

            result = {
                "result": datas
            }
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def blue_verified_followers(self, userId: str | int, count: int = 20, proxy=None, **kwargs):
        """

        Arguments :
          - userId (Required) The ID of the rest_id key contained in the search function results.
          - count (Optional) Amount of data.
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'following'. Expected str|int, got {}".format(
                type(userId).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'following'. Expected int, got {}".format(
                type(count).__name__)
            )
        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            userId=userId,
            count=count
        )
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://twitter.com/i/api/graphql/kNMtfqx9jhnY20rRxJUD2g/BlueVerifiedFollowers?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            instructions = data["data"]["user"]["result"]["timeline"]["timeline"]["instructions"]
            datas = []
            for index, value in enumerate(instructions):
                if isinstance(value, dict) and value["type"] == "TimelineAddEntries":
                    datas = [
                        self.__processuserresults(
                            entry["content"]["itemContent"]
                        )
                        for entry in instructions[index]["entries"]
                        if "content" in entry
                        and "itemContent" in entry["content"]
                        and "user_results" in entry["content"]["itemContent"]
                    ]

            result = {
                "result": datas
            }
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def followers_you_know(self, userId: str | int, count: int = 20, proxy=None, **kwargs):
        """

        Arguments :
          - userId (Required) The ID of the rest_id key contained in the search function results.
          - count (Optional) Amount of data.
        """
        if not isinstance(userId, (str | int)):
            raise TypeError("Invalid parameter for 'following'. Expected str|int, got {}".format(
                type(userId).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'following'. Expected int, got {}".format(
                type(count).__name__)
            )
        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()
        params = self.__buildparams(
            func_name=function_name,
            userId=userId,
            count=count
        )
        for key in params:
            params.update({key: Utility.convertws(params[key])})

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://twitter.com/i/api/graphql/NM7p_h1LQ_Jf4pEeavxM7A/FollowersYouKnow?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )
        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()
        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            instructions = data["data"]["user"]["result"]["timeline"]["timeline"]["instructions"]
            datas = []
            for index, value in enumerate(instructions):
                if isinstance(value, dict) and value["type"] == "TimelineAddEntries":
                    datas = [
                        self.__processuserresults(
                            entry["content"]["itemContent"]
                        )
                        for entry in instructions[index]["entries"]
                        if "content" in entry
                        and "itemContent" in entry["content"]
                        and "user_results" in entry["content"]["itemContent"]
                    ]

            result = {
                "result": datas
            }
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")


if __name__ == "__main__":
    cookie = ""
    sb = XCrawl()
