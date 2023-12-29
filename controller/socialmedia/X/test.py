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
from helper.html_parser import HtmlParser
from helper.utility import Utility


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

    def replacechar(self, text: str, replacement: str):
        pattern = re.compile(r'_(.*?)\.jpg')
        matches = pattern.search(
            string=text.split("/")[-1]
        )
        if matches:
            replace = matches.group(1)
            result = text.replace(replace, replacement)
            return result
        return text

    def guest_token(self, cookies=None):
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

    def profile(self, username: str, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.set_cookies(cookies=cookies)
        if username is not None:
            if not isinstance(username, str):
                raise TypeError(
                    "Invalid \"profile\" parameter, value must be type str, {} passed".format(
                        type(username).__name__)
                )
            if isinstance(username, str):
                username = str(username)
        params = {
            "variables": {
                "screen_name": username,
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
        self.headers["X-Guest-Token"] = self.guest_token()
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
                            key: self.replacechar(
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

    def userspost(self, userid: str, proxy=None, cookies=None, **kwargs):
        user_agent = self.fake.user_agent()
        if cookies:
            cookies = self.set_cookies(cookies=cookies)
        if userid is not None:
            if not isinstance(userid, str):
                raise TypeError(
                    "Invalid \"userspost\" parameter, value must be type str, {} passed".format(
                        type(userid).__name__)
                )
            if isinstance(userid, str):
                userid = str(userid)
        params = {
            "variables": {
                "userId": userid,
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
        self.headers["X-Guest-Token"] = self.guest_token()
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


if __name__ == "__main__":
    sb = X()
    cek = sb.profile(username="AM_EllaJKT48")
    # print(cek)
