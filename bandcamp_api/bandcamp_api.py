from datetime import datetime as dt
import json
import logging

import requests
from bs4 import BeautifulSoup
from bs4 import FeatureNotFound

from .bandcampjson import BandcampJSON
from .album import Album
from .artist import Artist
from .label import Label
from .daily import Daily, Story
from .homepage import NewAndNotable, Charts, SaleFeed, BandcampWeekly
from .genres import get_main_genres, get_subgenres
from .search import search_artists, search_albums, search_tracks, search_fans
from .track import Track

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
        self.tracks = None

    def get_album(self, album_url, skip_track_scrape: bool = False):
        """Returns information for a given album URL"""
        return Album(album_url=album_url, skip_track_scrape=skip_track_scrape)

    def get_track(self, track_url):
        """Returns information for a given track URL"""
        return Track(track_url=track_url)

    def get_artist(self, artist_url):
        """Returns information for a given artist URL"""
        return Artist(artist_url=artist_url)

    def get_label(self, label_url: str):
        """Returns information for a given label URL"""
        return Label(label_url=label_url)

    def daily_latest(self, num_to_get: int):
        """Retuns the latest Bandcamp Daily stories. Warning this is very slow."""
        return Daily().search_latest(num_to_get=num_to_get)

    def daily_best_of(self,section_slug: str, num_to_get: int):
        """Returns a list of Bandcamp Daily stories for a given Best Of section"""
        return Daily().search_best_of(section_slug=section_slug, num_to_get=num_to_get)

    def daily_franchise(self, section_slug: str, num_to_get: int):
        """Returns a list of Bandcamp Daily stories for a given franchise"""
        return Daily().search_franchises(section_slug=section_slug, num_to_get=num_to_get)

    def daily_genre(self, genre_slug: str, num_to_get: int):
        """Returns a list Bandcamp Daily stories for a given genre"""
        return Daily().search_genre(genre_slug=genre_slug, num_to_get=num_to_get)

    def daily_get_story(self, story_url: str):
        """Get information on a Bandcamp Daily story"""
        return Story(story_url = story_url)

    def new_and_notable(self, num_to_get: int = 5):
        """Returns a list of new and notable releases accoding to Bandcamp"""
        return NewAndNotable(num_to_get)

    def get_genres(self):
        """Returns a list of the main overarching genres. For more specific genres see get_subgenres()"""
        # returns a list of main genres
        return get_main_genres()

    def get_subgenres(self, main_genre: str = ""):
        """Returns a list of subgenres for a given genre. If no genre is given, all are given
        :param main_genre: Slug of the main genre. See get_genre()."""
        return get_subgenres(main_genre=main_genre)

    def charts( self, main_genre: str = "", subgenre: str = "", sort: str = "", format: str = "", page: int = 0):
        """Returns a list of ChartAlbum Objects"""
        return Charts(main_genre=main_genre, subgenre=subgenre, sort=sort, format=format, page=page)

    def sales_feed(self):
        """A list of just sold entities."""
        return SaleFeed(self)

    def bandcamp_weekly(self, id: int = 0):
        """Returns information about a Bandcamp Weekly release. If no ID is given, assumes latest."""
        return BandcampWeekly.get_show(self, id=id)
    

    # doing live streams later
    #def get_live_streams(self):
        """Returns a list of ongoing Bandcamp Livestreams"""

    #def get_planned_livestreams(self):
        """Returns a list of planned Bandcamp Livestreams"""
    
    #def get_ongoing_livestreams(self):
        """Returns a list of currently boadcasting livestreams"""

    #def get_featured_livestreams(self):
        """Returns a list of Bandcamp featured livestreams"""
        
    def search_artist(self, search_string: str = ""):
        """Search Bandcamp for an artist"""
        return search_artists(search_string=search_string)
    
    def search_albums(self, search_string: str = ""):
        """Search Bandcamp for an album"""
        return search_albums(search_string=search_string)

    def search_tracks(self, search_string: str = ""):
        """Search Bandcamp for a track"""
        return search_tracks(search_string=search_string)

    def search_fans(self, search_string: str):
        """Search Bandcamp for a fan"""
        return search_fans(search_string=search_string)