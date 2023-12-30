import unicodedata
import pytz
import hashlib
import re
import json
import random
import string
import time

from pyquery import PyQuery
from requests.sessions import Session
from requests.cookies import RequestsCookieJar
from requests.exceptions import Timeout, ReadTimeout
from urllib.parse import urljoin, urlencode, quote
from faker import Faker
from datetime import datetime
# from helper.html_parser import HtmlParser
# from helper.utility import Utility

from bs4 import BeautifulSoup
from pyquery import PyQuery as pq


class HtmlParser:
    def __init__(self):
        pass

    def bs4_parser(self, html, selector):
        result = None
        try:
            html = BeautifulSoup(html, "lxml")
            result = html.select(selector)
        except Exception as e:
            print(e)
        finally:
            return result

    def pyq_parser(self, html, selector):
        result = None
        try:
            html = pq(html)
            result = html(selector)
        except Exception as e:
            print(e)
        finally:
            return result


class Utility:
    """
    Encapsulates a collection of utility functions for various tasks.
    """
    @staticmethod
    def hashmd5(url: str):
        """Calculates the MD5 hash of the given URL.
        Returns the hashed value as a hexadecimal string.
        """
        md5hash = hashlib.md5()
        md5hash.update(url.encode('utf-8'))
        hashed = md5hash.hexdigest()
        return hashed

    @staticmethod
    def timezone(date_time, format):
        """Converts a datetime string to the corresponding time zone offset for Asia/Jakarta.
        Takes the datetime string, a format string specifying its format, and returns the offset as a string like "+0700".
        """
        tz = pytz.timezone("Asia/Jakarta")
        date = datetime.strptime(date_time, format)
        timezone = tz.localize(date).strftime("%z")
        return timezone

    @staticmethod
    def UniqClear(text):
        """Normalizes and removes non-ASCII characters from the given text.
        Returns the ASCII-only version of the text.
        """
        normalized = unicodedata.normalize('NFKD', text)
        ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
        return ascii_text

    @staticmethod
    def makeunique(datas: list):
        """
        Removes duplicate elements from a list while preserving order.
        Returns a new list containing only unique elements.
        """
        unique_list = []
        [unique_list.append(x) for x in datas if x not in unique_list]
        return unique_list

    @staticmethod
    def convertws(data: dict):
        dumps = json.dumps(data)
        without_whitespace = re.sub(r'\s+', '', dumps)
        return without_whitespace


class X:
    def __init__(self):
        self.session = Session()
        self.jar = RequestsCookieJar()
        self.fake = Faker()
        self.parser = HtmlParser()

        self.headers = dict()
        self.headers["Accept"] = "application/json, text/plain, */*"
        self.headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.headers["Sec-Fetch-Dest"] = "empty"
        self.headers["Sec-Fetch-Mode"] = "cors"
        self.headers["Sec-Fetch-Site"] = "same-site"

    def set_cookies(self, cookies):
        for cookie in cookies:
            if cookie["name"] == "msToken":
                msToken = cookie["value"]
            self.jar.set(
                cookie["name"],
                cookie["value"],
                domain=cookie["domain"],
                path=cookie["path"],
            )
        return self.jar

    def __processmedia(self): ...

    def __removeallentites(self, keyword: str, datas: dict):
        if keyword in datas["legacy"]:
            for e_media in datas["legacy"][keyword]["media"]\
                if "media" in datas["legacy"][keyword]\
                    else datas["legacy"][keyword].update({"media": []}):
                del e_media["id_str"]
                del e_media["indices"]
                del e_media["media_key"]
                del e_media["ext_media_availability"]
                del e_media["features"]
                del e_media["sizes"]
                del e_media["original_info"]

    def __generatekey(self, datas: dict):
        for key in datas["legacy"]:
            if key in [
                "conversation_id_str",
                "display_text_range",
                "is_quote_status",
                "possibly_sensitive",
                "possibly_sensitive_editable",
                "quoted_status_id_str",
                "quoted_status_permalink",
                "user_id_str",
                "id_str"
            ]:
                yield key

    def __replacechar(self, text: str, replacement: str):
        pattern = re.compile(r'_(.*?)\.jpg')
        matches = pattern.search(
            string=text.split("/")[-1]
        )
        if matches:
            replace = matches.group(1)
            result = text.replace(replace, replacement)
            return result
        return text

    def __guest_token(self, cookies=None):
        user_agent = self.fake.user_agent()
        auth = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        url = "https://api.twitter.com/1.1/guest/activate.json"
        self.headers["User-Agent"] = user_agent
        self.headers["Authorization"] = auth
        resp = self.session.post(
            url=url,
            headers=self.headers,
            cookies=cookies,
            timeout=60
        )
        status_code = resp.status_code
        content = resp.json()["guest_token"]
        if status_code == 200:
            self.headers.update({
                "X-Guest-Token": content
            })
        return self.headers["X-Guest-Token"]

    def profile(self, screen_name: str, proxy=None, cookies=None, **kwargs) -> dict:
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.set_cookies(cookies=cookies)
        if screen_name is not None:
            if not isinstance(screen_name, str):
                raise TypeError(
                    "Invalid \"profile\" parameter, value must be type str, {} passed".format(
                        type(screen_name).__name__)
                )
            if isinstance(screen_name, str):
                screen_name = str(screen_name)
        params = {
            "variables": {
                "screen_name": screen_name,
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
        self.headers["X-Guest-Token"] = self.__guest_token()
        resp = self.session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.headers,
            cookies=cookies,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            result: dict = data["data"]["user"]
            for key, value in result["result"]["legacy"].items():
                if key == "profile_image_url_https":
                    result["result"]["legacy"].update(
                        {
                            key: self.__replacechar(
                                value,
                                "400x400"
                            )
                        }
                    )
            # results = json.dumps(result, indent=4)
            # with open("controller/socialmedia/twitter/profile.json", "w") as file:
            #     file.write(results)
            return result
        else:
            raise Exception(
                f"Error! status code {resp.status_code} : {resp.reason}")

    def userspost(self, userId: str, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.set_cookies(cookies=cookies)
        if userId is not None:
            if not isinstance(userId, str):
                raise TypeError(
                    "Invalid \"userspost\" parameter, value must be type str, {} passed".format(
                        type(userId).__name__)
                )
            if isinstance(userId, str):
                userId = str(userId)
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
        self.headers["X-Guest-Token"] = self.__guest_token()
        resp = self.session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.headers,
            cookies=cookies,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = json.loads(content.decode('utf-8'))
            return response
            # data = json.dumps(response, indent=4)
            # with open("controller/socialmedia/twitter/userspost.json", "w") as file:
            #     file.write(data)

    def media(self, screen_name):
        profile = self.profile(screen_name=screen_name)
        userId = profile["result"]["rest_id"]
        raw = self.userspost(userId=userId)
        deep = raw["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"][1]
        datas = []
        for entry in deep["entries"]:
            deeper = entry["content"]["itemContent"]["tweet_results"]["result"]
            id = deeper["rest_id"]
            unmention_data = deeper["unmention_data"]
            views = {
                key: value for key, value in deeper["views"].items()
                if key != "state"
            }
            self.__removeallentites(
                keyword="entities",
                datas=deeper
            )
            self.__removeallentites(
                keyword="extended_entities",
                datas=deeper
            )
            for key in list(
                self.__generatekey(
                    datas=deeper
                )
            ):
                del deeper["legacy"][key]

            legacy = deeper["legacy"]
            # if "quoted_status_result" in deeper:
            #     del deeper["quoted_status_result"]

            # del deeper["__typename"]
            # del deeper["core"]
            # del deeper["edit_control"]
            # del deeper["source"]
            # del deeper["quick_promote_eligibility"]

            # del deeper["legacy"]["id_str"]
            # del deeper["legacy"]["conversation_id_str"]
            # del deeper["legacy"]["display_text_range"]

            # try:
            #     em = deeper["legacy"]["entities"]["media"] if "media" in deeper["legacy"]["entities"] else None
            #     eem = deeper["legacy"]["extended_entities"]["media"] if "media" in deeper["legacy"]["extended_entities"] else None
            # except KeyError:
            #     em = None
            #     eem = None

            # if (em or eem) is not None:
            #     for entities_media, extended_entities_media in zip(em, eem):
            #         del entities_media["id_str"]
            #         del entities_media["indices"]
            #         del entities_media["media_key"]
            #         del entities_media["ext_media_availability"]
            #         del entities_media["features"]
            #         del entities_media["sizes"]
            #         del entities_media["original_info"]

            #         del extended_entities_media["id_str"]
            #         del extended_entities_media["indices"]
            #         del extended_entities_media["media_key"]
            #         del extended_entities_media["ext_media_availability"]
            #         del extended_entities_media["features"]
            #         del extended_entities_media["sizes"]
            #         del extended_entities_media["original_info"]
            return legacy

        #     datas.append(deeper)

        # result = {
        #     "result": datas
        # }
        # dumps = json.dumps(result, indent=4)
        # with open("controller/socialmedia/twitter/media.json", "w") as file:
        #     file.write(dumps)


if __name__ == "__main__":
    sb = X()
    # cek = sb.profile(username="gibran_tweet")
    # cek = sb.media("gibran_tweet")
    # print(cek)
