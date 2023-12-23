import unicodedata
import hashlib
import pytz

from datetime import datetime


class Utility:
    def __init__(self):
        pass

    def hashmd5(self, url: str):
        md5hash = hashlib.md5()
        md5hash.update(url.encode('utf-8'))
        hashed = md5hash.hexdigest()
        return hashed

    def timezone(self, date_time, format):
        tz = pytz.timezone("Asia/Jakarta")
        date = datetime.strptime(date_time, format)
        timezone = tz.localize(date).strftime("%z")
        return timezone

    def UniqClear(self, text):
        normalized = unicodedata.normalize('NFKD', text)
        ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
        return ascii_text
