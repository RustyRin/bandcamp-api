import json
import re
import requests
from bs4 import BeautifulSoup
from bs4 import FeatureNotFound
from datetime import datetime
import time

import logging

from bandcampjson import BandcampJSON

class Album:

    def __init__(self, album_url, debugging: bool = False):
        self.album = ""
        self.artist = ""
        self.tracks = []
        self.art_url = ""
        self.album_url = ""
        self.artist_url = ""
        self.all_songs_available = False
        self.price = [0.00, "USD"]
        self.keywords = []
        self.publisher = ""
        self.preorder = False

        # need to do
        self.album_bio = ""

        self.relased = 0    # utc unixtime
        self.published = 0  # utc unixtime

        # extra, ignore
        self.soup = None

        # This stuff seems *minor* so I'm just
        # going to use a dict, if this is a problem
        # for you I'm sure you're smart enough to
        # fix it or make it better
        self.advanced = {
            "copyright": "",
            "last_edited": 0,
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

            with open('output.json', 'w+') as file:
                file.write(json.dumps(page_json, indent=4))
        except Exception as err:
            print(err)
            raise AttributeError("Either the album URL given is either private, deleted or the link is malformed.")

        self.artist = page_json['artist']

        try:
            self.album = page_json['current']['title']
        except:
            self.album = page_json['trackinfo'][0]['title']

        self.album_url = album_url

        # getting artist url
        if 'track' in page_json['url']:
            self.artist_url = page_json['url'].rpartition('/track/')[0]
        else:
            self.artist_url = page_json['url'].rpartition('/album')[0]

        for trackjson in page_json['trackinfo']:
            track = Track()

            track.set_title(trackjson['title'])
            track.set_track_number(trackjson['track_num'])
            track.set_duration_seconds(trackjson['duration'])

            # this is like this bc i was dumb and dont
            # want to fix it, dont care
            try:
                lyrics_link = str(self.artist_url + trackjson['title_link'] + '#lyrics')
                track_lyrics = self.get_track_lyrics(lyrics_link)
            except:
                track_lyrics = ''

            track.set_lyrics(track_lyrics)

            if trackjson['file'] is None:
                track.set_available(False)
            else:
                track.set_available(True)

            self.tracks.append(track)

        self.all_songs_available = self.are_all_songs_available(page_json['trackinfo'])

        self.art_url = self.get_album_art()

        self.keywords = page_json['keywords']

        self.publisher = page_json['publisher']['@id']

        self.album_bio = page_json['current']['about']

        # currently some albums get a time of 0, need to look if there are
        # some other places to find the released and publish times.
        try:
            self.relased = datetime.strptime(page_json['album_release_date'], '%d %B %Y %H:%M:%S %Z')
            self.relased = int(time.mktime(self.relased.timetuple()))
        except:
            self.relased = 0
        
        try:
            self.published = datetime.strptime(page_json['datePublished'], '%d %B %Y %H:%M:%S %Z')
            self.published = int(time.mktime(self.published.timetuple()))
        except:
            self.published = 0

        self.price[0] = float(page_json["current"]["minimum_price"])
        self.price[1] = page_json['albumRelease'][0]['offers']['priceCurrency']

        try:
            self.preorder = bool(page_json['album_is_preorder'])
        except:
            self.preorder = False


        # doing the "advanced"

        self.advanced['copyright'] = page_json['copyrightNotice']

        try:
            self.advanced['last_edited'] = datetime.strptime(page_json['dateModified'], '%d %B %Y %H:%M:%S %Z')
            self.advanced['last_edited'] = int(time.mktime(self.advanced['last_edited'].timetuple()))
        except:
            self.advanced['last_edited'] = self.published

        self.advanced['ids']['artist_id'] = page_json['current']['band_id']
        self.advanced['ids']['album_id'] = page_json['id']
        self.advanced['ids']['art_id'] = page_json['current']['art_id']
        self.advanced['ids']['seller_id'] = page_json['current']['selling_band_id']
        self.advanced['featured_track'] = page_json['additionalProperty'][1]["value"]
        self.advanced['email_required'] = page_json['current']['require_email']

        for review in page_json['comment']:
            current_review = {}
            try:
                current_review["username"] = str(review['author']['name'])
            except:
                current_review["username"] = None
            current_review['profile_url'] = review['author']['url']
            current_review['profile_picture'] = review['author']['image']
            current_review['review'] = str(review['text'][0])
            try:
                current_review['favorite_track'] = str(review['text'][1].split(": ")[1])
            except:
                current_review['favorite_track'] = None

            self.advanced['reviews'].append(current_review)

        for supporter in page_json['sponsor']:
            current_supporter = {}

            current_supporter['username'] = supporter['name']
            current_supporter['profile_url'] = supporter['url']
            current_supporter['profile_picture'] = supporter['image']

            self.advanced['supporters'].append(current_supporter)

    # setters
    def set_album(self, new_album):
        self.album = new_album

    def set_artist(self, new_artist):
        self.artist = new_artist

    # NEED TO MAKE A METHOD TO SET TRACKS
    # Idea, need a track object, and a position
    # then sets overwrites the track in the position
    # then if it doesnt exist, add to that position
    # lets say the album is 4 songs long, but you
    # are trying to add a song to position 6
    # there should be some way to handle that,
    # like what do i do to that empty position of track 5

    def set_art_url(self, new_art_url):
        self.art_url = new_art_url

    def set_album_url(self, new_album_url):
        self.art_url = new_album_url

    def set_artist_url(self, new_artist_url):
        self.artist_url = new_artist_url

    # need to check for unity in how i describe
    # if all the songs are there 
    # like should i used released ot available.
    # probably available, since a song can be released
    # but not available to stream
    # so change all occurences of released to available
    def set_all_songs_available(self, new_all_songs_available):
        self.all_songs_available = new_all_songs_available

    def set_price(self, new_amount, new_currency='USD'):
        '''Set the price of this album with an amount and currency type
        :param new_amount: The price of the album as a float
        :param new_currency: The 3 char code (ISO 4217) of a particular crrency. USD is the default
        '''
        self.price = [float(new_amount), str(new_currency)]

    # need to make two methods to add and remove keywords

    # def add_keyword(self, new_keyword):

    # def remove_keyword(self, old_keyword):

    def set_publisher(self, new_publisher):
        self.publisher = new_publisher

    def set_published_date(self, new_date):
        """Sets the published date, is in UNIX timestamp format"""
        self.published = new_date

    def set_released_date(self, new_date):
        """Sets the released date, it is in UNIX timestamp format"""
        self.relased = new_date

    def set_preorder(self, new_preorder):
        """Sets the preorder status. This is because preorder will have UNIX time of 0, which can be confusing if there is a time error"""
        self.preorder = new_preorder
    # getters
    def get_album_title(self):
        return str(self.album)

    def get_album_artist(self):
        return str(self.artist)

    def get_tracks(self):
        """Returns an array of Track objects"""
        return self.tracks

    def get_album_art_url(self):
        """Returns the URL of the album art"""
        return self.art_url

    def get_album_url(self):
        """Retuns a the Bandcamp link to the album"""
        return str(self.album_url)

    def get_artist_url(self):
        """Returns the Bandcamp link for the artist (seller)"""
        return self.artist_url

    def get_all_songs_available(self):
        """Returns True if all songs are avaible to stream. False if not"""
        return self.all_songs_available

    def get_album_price(self):
        """Returns an array to represent the price. First is the amount as float, second is the 3 char code (ISO 4217) for a given currency. Defaults to USD"""
        return self.price

    def get_album_keywords(self):
        """Returns an array of all the keywords that the artist applied to this album"""
        return self.keywords

    def get_album_publisher(self):
        """Retruns the publisher of this album"""
        return self.publisher

    def get_released_date(self):
        """Returns a UNIX timestamp of when the album was released"""
        return self.relased

    def get_published_date(self):
        """Returns a UNIX timestamp of then the album was published to Bandcamp"""
        return self.published

    def get_preorder_status(self):
        """Returns True if album is currently under preorder, False if not"""
        return self.preorder

    def get_advanced(self):
        """Returns a dict of some more 'advanced' information"""
        return self.advanced
    
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

            

    

class Track:
    def __init__(self, debugging: bool = False):
        self.title = ""
        self.track_number = ""
        self.duration_seconds = 0.00
        self.lyrics = ""
        self.available = False
        self.track_id = 0

    # setters
    def set_title(self, new_title):
        self.title = new_title

    def set_track_number(self, new_track_number):
        self.track_number = new_track_number

    def set_duration_seconds(self, new_duration):
        self.duration = new_duration

    def set_lyrics(self, new_lyrics):
        self.lyrics = new_lyrics

    def set_available(self, new_availablity):
        self.available = new_availablity

    def set_track_id(self, new_track_id):
        self.track_id = new_track_id

    # getters
    def title(self):
        return self.title

    def track(self):
        return self.track_number

    def duration_seconds(self):
        return self.duration

    def lyrics(self):
        return self.lyrics

    def available(self):
        return self.available

    def track_id(self):
        return self.track_id