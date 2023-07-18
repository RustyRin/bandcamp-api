'''
Need to do
'''
from .bandcampjson import BandcampJSON
import requests
import logging
from bs4 import BeautifulSoup, FeatureNotFound
import json
from datetime import datetime
import time


def get_json(url, debugging: bool = False):
    header = {'User-Agent': f'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}

    try:
        response = requests.get(url, headers=header)
    except requests.exceptions.MissingSchema:
        return None

    try:
        soup = BeautifulSoup(response.text, "lxml")
    except FeatureNotFound:
        soup = BeautifulSoup(response.text, "html.parser")

    logging.debug(" Generating JSON...")

    bandcamp_json = BandcampJSON(soup, debugging).generate()
    page_json = {}
    for entry in bandcamp_json:
        page_json = {**page_json, **json.loads(entry)}

    logging.debug(' Bandcamp JSON generated...')

    return page_json


class Track:
    def __init__(self, artist_id: int, track_id: int, advanced: bool = False):

        # object info
        self.type = "track"

        # track information
        self.track_id: int = 0
        self.track_title: str = ""
        self.track_number: int = 0
        self.track_duration_seconds: float = 0.00
        self.track_streamable: bool = None
        self.has_lyrics: bool = None
        self.lyrics: str = ""
        self.is_price_set: bool = None
        self.price: dict = {}
        self.require_email: bool = None
        self.is_purchasable: bool = None
        self.is_free: bool = None
        self.is_preorder: bool = None
        self.tags: list = []
        self.track_url: str = ""

        # art
        self.art_id: int = 0
        self.art_url: str = ""

        # artist information
        self.artist_id: int = 0
        self.artist_title: str = ""

        # album information
        self.album_id: int = 0
        self.album_title: str = ""

        # label
        self.label_id: int = 0
        self.label_title: str = ""

        # about
        self.about: str = ""
        self.credits: str = ""
        self.date_released_unix: int = 0

        # advanced
        self.date_last_modified_unix: int = 0
        self.date_published_unix: int = 0
        self.supporters: list = []


        response = requests.get(
            url="https://bandcamp.com/api/mobile/25/tralbum_details?band_id=" + str(artist_id) +
                "&tralbum_id=" + str(track_id) + "&tralbum_type=t"
        )
        result = response.json()
        self.track_id = result['id']
        self.track_title = result['title']
        self.track_number = result['tracks'][0]['track_num']
        self.track_duration_seconds = result['tracks'][0]['duration']
        self.track_streamable = result['tracks'][0]['is_streamable']
        self.has_lyrics = result['tracks'][0]['has_lyrics']

        # getting lyrics, if there is any
        if self.has_lyrics is True:
            r = requests.get("https://bandcamp.com/api/mobile/25/tralbum_lyrics?tralbum_id=" + str(self.track_id) + \
                             "&tralbum_type=t")
            rr = r.json()
            self.lyrics = rr['lyrics'][str(self.track_id)]

        self.is_price_set = result['is_set_price']
        self.price = {
            "currency": result['currency'],
            "amount": result['price']
        }
        self.require_email = result['require_email']
        self.is_purchasable = result['is_purchasable']
        self.is_free = result['free_download']
        self.is_preorder = result['is_preorder']

        for tag in result['tags']:
            self.tags.append(tag['name'])

        self.art_id = result['art_id']
        self.art_url = "https://f4.bcbits.com/img/a" + str(self.art_id) + "_0.jpg"

        self.artist_id = result['band']['band_id']
        self.artist_title = result['band']['name']

        self.album_id = result['album_id']
        self.album_title = result['album_title']

        self.label_id = result['label_id']
        self.label_title = result['label']

        self.about = result['about']
        self.credits = result['credits']

        self.date_released_unix = result['release_date']

        self.track_url = result['bandcamp_url']

        if advanced:
            try:
                page_json = get_json(url=self.track_url)
            except:
                raise FileNotFoundError("Could not get advanced data for track (ID:", self.track_id, ")")

            try:
                self.date_last_modified_unix = datetime.strptime(page_json['dateModified'], '%d %b %Y %H:%M:%S %Z')
                self.date_last_modified_unix = int(time.mktime(self.date_last_modified_unix.timetuple()))
            except:
                self.date_last_modified_unix = 0

            try:
                self.date_published_unix = datetime.strptime(page_json['datePublished'], '%d %b %Y %H:%M:%S %Z')
                self.date_published_unix = int(time.mktime(self.date_published_unix.timetuple()))
            except:
                self.date_published_unix = 0

            try:
                for supporter in page_json['sponsor']:
                    try:
                        current_supporter = {
                            'username': supporter['name'],
                            'profile_url': supporter['url'],
                            'profile_picture': supporter['image'].split('_')[0] + '_0.jpg'
                        }
                        self.supporters.append(current_supporter)
                    except:
                        pass
            except:
                pass
