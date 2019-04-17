# -*- coding: utf-8 -*-

import urllib2
import requests
import json
import codecs
import sys

if __name__ == "__main__":
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    url_movie = "https://api.desimartini.com/api/movies/latest-movies-uc/?page=10&language=hi"
    url_celebs = "https://api.desimartini.com/api/celebrity/uc/?language=en&page=81"
    header = {"User-Agent": ua}
    # header = {"User-Agent": ua, "Accept-Language": "hi"}
    ty = typeEncode = sys.getfilesystemencoding()
    request = urllib2.Request(url=url_movie, headers=header)
    print(request.headers)
    print("=========================")
    response = urllib2.urlopen(request)
    print(response.headers)
    data = response.read()
    print(data)
    fi = codecs.open("./data.json", "w")
    fi.write(json.dumps(data, ensure_ascii=False))
    fi.close()