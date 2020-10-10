import json
import datetime
import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup

class BlogPost:
    def __init__(self, blog_id, log_no, url, title, description, date, blog_name, hyperlinks, tags, body):
        self._blog_id = blog_id
        self._log_no = log_no
        self._url = url
        self._title = title
        self._description = description
        self._date = date
        self._blog_name = blog_name
        self._hyperlinks = hyperlinks
        self._tags = tags
        self._body = body

    def __str__(self):
        s = "Blog ID : " + self._blog_id + "\n"
        s += "logNo : " + self._log_no + "\n"
        s += "포스팅 URL : " + self._url + "\n"
        s += "포스팅 제목 : " + self._title + "\n"
        s += "포스팅 설명 : " + self._description + "\n"
        s += "포스팅 날짜 : " + self._date + "\n"
        s += "블로그 이름 : " + self._blog_name + "\n"

        if self._hyperlinks:
            s += "하이퍼링크 목록 : "
            for hyperlink in self._hyperlinks:
                s += hyperlink + "\n"

        if self._tags:
            s += "태그 목록 : "
            for tag in self._tags:
                s += tag + "\n"

        s += "포스팅 내용 : " + self._body
        return s