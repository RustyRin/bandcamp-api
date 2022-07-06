import json
import requests
from bs4 import BeautifulSoup
from bs4 import FeatureNotFound
from datetime import datetime
import time

import logging

from .bandcampjson import BandcampJSON
from .track import Track

class Album:

    def __init__(self, album_url, debugging: bool = False):
        self.album_title = ""
        self.artist_title = ""
        self.tracks = []
        self.art_url = ""
        self.album_url = ""
        self.artist_url = ""
        self.all_songs_available = False
        self.price = {}
        self.keywords = []
        self.publisher_title = ""
        self.preorder = False

        # need to do
        self.album_bio = ""

        self.date_released = 0    # utc unixtime
        self.date_published = 0  # utc unixtime
        self.date_last_modified = 0

        # extra, ignore
        self.soup = None

        # This stuff seems *minor* so I'm just
        # going to use a dict, if this is a problem
        # for you I'm sure you're smart enough to
        # fix it or make it better
        self.advanced = {
            "copyright": "",
            "ids": {
                "artist_id": 0,
                "album_id": 0,
                "art_id": 0,
                "seller_id": 0,
            },
            "featured_track": 0,
            "email_required": False,
            "reviews": [],
            "supporters": []
        }

        try:
            page_json = self.get_json(url = album_url)

        except Exception as err:
            print(err)
            raise AttributeError("Either the album URL given is either private, deleted or the link is malformed.")

        self.artist_title = page_json['artist']
        self.artist_title = ' '.join(self.artist_title.split())

        try:
            self.album_title = page_json['current']['title']
            self.album_title = ' '.join(self.album_title.split())
        except:
            self.album_title = page_json['trackinfo'][0]['title']

        self.album_url = album_url

        # getting artist url
        if 'track' in page_json['url']:
            self.artist_url = page_json['url'].rpartition('/track/')[0]
        else:
            self.artist_url = page_json['url'].rpartition('/album')[0]

        for trackjson in page_json['trackinfo']:
            try:
                track = Track(str(self.artist_url + trackjson['title_link']))
                self.tracks.append(track)
            except:
                pass

        self.all_songs_available = self.are_all_songs_available(page_json['trackinfo'])

        self.art_url = 'https://f4.bcbits.com/img/a' + str(page_json['current']['art_id']) + '_0.jpg'

        self.keywords = page_json['keywords']

        self.publisher = page_json['publisher']['@id']

        if page_json['current']['about'] != None:
            self.album_bio = page_json['current']['about']

        # currently some albums get a time of 0, need to look if there are
        # some other places to find the released and publish times.
        try:
            self.date_released = datetime.strptime(page_json['album_release_date'], '%d %b %Y %H:%M:%S %Z')
            self.date_released = int(time.mktime(self.date_released.timetuple()))
        except:
            self.date_released = 0
        
        try:
            self.date_published = datetime.strptime(page_json['datePublished'], '%d %b %Y %H:%M:%S %Z')
            self.date_published = int(time.mktime(self.date_published.timetuple()))
        except:
            self.date_published = 0

        self.price['amount'] = float(page_json["current"]["minimum_price"])
        self.price['currency'] = page_json['albumRelease'][0]['offers']['priceCurrency']

        try:
            self.preorder = bool(page_json['album_is_preorder'])
        except:
            self.preorder = False


        # doing the "advanced"
        try:
            self.advanced['copyright'] = page_json['copyrightNotice']
        except:
            self.advanced['copyright'] = ""

        try:
            self.date_last_modified = datetime.strptime(page_json['dateModified'], '%d %b %Y %H:%M:%S %Z')
            self.date_last_modified = int(time.mktime(self.date_last_modified.timetuple()))
        except:
            self.advanced['last_edited'] = self.date_published

        self.advanced['ids']['artist_id'] = page_json['current']['band_id']
        self.advanced['ids']['album_id'] = page_json['id']
        self.advanced['ids']['art_id'] = page_json['current']['art_id']
        self.advanced['ids']['seller_id'] = page_json['current']['selling_band_id']
        self.advanced['featured_track'] = page_json['additionalProperty'][1]["value"]

        if page_json['current']['require_email'] != None:
            self.advanced['email_required'] = page_json['current']['require_email']
        else:
            self.advanced['email_required'] = False
        
        try:
            for review in page_json['comment']:
                current_review = {}
                try:
                    current_review["username"] = str(review['author']['name'])
                    current_review['username'] =  ' '.join( current_review["username"].split())
                except:
                    current_review["username"] = ""

                current_review['profile_url'] = review['author']['url']

                current_review['profile_picture'] = review['author']['image']
                current_review['profile_picture'] = current_review['profile_picture'].split('_')[0] + '_0.jpg'

                current_review['review'] = str(review['text'][0])
                current_review['review'] = ' '.join(current_review['review'].split())
                try:
                    current_review['favorite_track'] = str(review['text'][1].split(": ")[1])
                except:
                    current_review['favorite_track'] = ""

                self.advanced['reviews'].append(current_review)
        except:
            pass

        try:
            for supporter in page_json['sponsor']:
                try:
                    current_supporter = {}

                    current_supporter['username'] = supporter['name']
                    current_supporter['profile_url'] = supporter['url']
                    current_supporter['profile_picture'] = supporter['image'].split('_')[0] + '_0.jpg'

                    self.advanced['supporters'].append(current_supporter)
                except:
                    pass
        except:
            pass
    
    # other methods
    # need to organize the order of methods
    @staticmethod
    def generate_album_url(artist: str, slug: str, page_type: str) -> str:
        """Generate an album url based on the artist and album name

        :param artist: artist name
        :param slug: Slug of album/track
        :param page_type: Type of page album/track
        :return: url as str
        """
        return f"http://{artist}.bandcamp.com/{page_type}/{slug}"

    def get_album_art(self) -> str:
        """Find and retrieve album art url from page

        :return: url as str
        """
        try:
            url = self.soup.find(id='tralbumArt').find_all('a')[0]['href']
            return url
        except None:
            pass

    def get_json(self, url, debugging: bool = False):

        headers = {'User-Agent': f'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}

        try:
            response = requests.get(url, headers=headers)
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

    def are_all_songs_available(self, tracks):
        for track in tracks:
            if (track['file'] is None or False):
                return False

        return True

    def get_track_lyrics(self, track_url = None):
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