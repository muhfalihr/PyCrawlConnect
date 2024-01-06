import unicodedata
import hashlib
import json
import pytz
import re

from datetime import datetime


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
        """
        Converts dict data to string and removes spaces at the end of the text.
        """
        dumps = json.dumps(data)
        without_whitespace = re.sub(r'\s+', '', dumps)
        return without_whitespace

    @staticmethod
    def current_funcname():
        """
        Calls the name of the function used.
        """
        import inspect
        current_frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(current_frame)[1]
        function_name = caller_frame[3]
        return function_name
