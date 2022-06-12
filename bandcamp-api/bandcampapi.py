from datetime import datetime as dt
import json
import logging

import requests
from bs4 import BeautifulSoup
from bs4 import FeatureNotFound

from bandcampjson import BandcampJSON
from album import Album

def get_json(self, url, debugging: bool = False):
    try:
        response = requests.get(url, headers=self.headers)
    except requests.exceptions.MissingSchema:
        return None

    try:
        self.soup = BeautifulSoup(response.text, "lxml")
    except FeatureNotFound:
        self.soup = BeautifulSoup(response.text, "html.parser")

    logging.debug(" Generating BandcampJSON..")
    bandcamp_json = BandcampJSON(self.soup, debugging).generate()
    page_json = {}
    for entry in bandcamp_json:
        page_json = {**page_json, **json.loads(entry)}
    logging.debug(" BandcampJSON generated..")

    return page_json

class Bandcamp:
    def __init__(self):
        self.headers = {'User-Agent': 'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}
        self.soup = None
        self. tracks = None

    def get_album(self, album_url):
        return Album(album_url=album_url)

    # maybe make some sort of way to include search