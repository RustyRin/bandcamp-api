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

def are_all_songs_available(tracks):
        for track in tracks:
            if (track['file'] is None or False):
                return False

        return True

def get_track_lyrics(track_url = None):
    track_page = requests.get(track_url, headers=None)

    try:
        track_soup = BeautifulSoup(track_page.text, 'lxml')
    except FeatureNotFound:
        track_page = BeautifulSoup(track_page.text, 'html.parser')
    try:
        track_lyrics = track_soup.find('div', {'class': 'lyricsText'})
    except:
        return ''

    if track_lyrics:
        return track_lyrics.text
    else:
        return ''

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
    def __init__(self, track_url):
        self.track_title = ""                 #
        self.artist_title = ""                #
        self.album_title = ""                 #
        self.track_number = 0           #
        self.date_published = 0              #
        self.date_released = 0               #
        self.date_last_modified = 0          #
        self.tags = []                  #
        self.price = {}                 #
            # {
            # "currency": "USD",
            # "amount": 0.00
            # }
        self.album_art_url = ""
        self.duration_seconds = 0.000   #
        self.track_url = ""             #
        self.album_url = ""             #
        self.artist_url = ""            #
        self.available = False          #
        self.lyrics = ""                #

        try:
            page_json = get_json(url = track_url)

        except Exception as err:
            print(err)
            raise AttributeError("Either the album URL given is either private, deleted or the link is malformed.")

        for track_json in page_json['trackinfo']:
            # i know its its a list of 1 element, dont care
            self.track_title = track_json['title']
            self.track_number = track_json['track_num']
            self.duration_seconds = track_json['duration']

            self.artist_title = page_json['byArtist']['name']
            self.artist_url = page_json['byArtist']['@id']
            try:
                self.album_title = page_json['inAlbum']['name']
                self.album_url = page_json['inAlbum']['@id']
            except:
                # its a single
                self.album_title = ""
                self.album_url = page_json['url']

            self.track_url = track_url



            try:
                self.lyrics = get_track_lyrics(track_url)
            except:
                self.lyrics = ''

            if track_json['file'] is None:
                self.available = False
            else:
                self.available = True

            try:
                self.date_published = datetime.strptime(page_json['datePublished'], '%d %b %Y %H:%M:%S %Z')
                self.date_published = int(time.mktime(self.date_published.timetuple()))
            except:
                self.date_published = 0

            try:
                self.date_released = datetime.strptime(page_json['album_release_date'], '%d %b %Y %H:%M:%S %Z')
                self.date_released = int(time.mktime(self.date_released.timetuple()))
            except:
                self.date_released = 0

            try:
                self.date_last_modified = datetime.strptime(page_json['dateModified'], '%d %b %Y %H:%M:%S %Z')
                self.date_last_modified = int(time.mktime(self.date_last_modified.timetuple()))
            except:
                self.date_released = 0

            for tag in page_json['keywords']:
                self.tags.append(tag)

            try:
                self.price['currency'] = page_json['inAlbum']['albumRelease'][1]['offers']['priceCurrency']
                self.price['amount'] = page_json['inAlbum']['albumRelease'][1]['offers']['price']
            except:
                self.price['currency'] = page_json['inAlbum']['albumRelease'][0]['offers']['priceCurrency']
                self.price['amount'] = page_json['inAlbum']['albumRelease'][0]['offers']['price']

            self.album_art_url = page_json['image'].split('_')[0] + '_0.jpg'

Track(track_url="https://thesaxophonesus.bandcamp.com/track/take-my-fantasy-maston-remix?label=609867351&tab=music")