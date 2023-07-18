import requests
from bs4 import BeautifulSoup, FeatureNotFound
import json
import random
import logging
from .bandcampjson import BandcampJSON
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


def get_current_new_and_notable_id():
    ping_size = 7          # how many guesses should be do per get/ping, max 60
    check_width = 7        # how many future IDs should be checked if they exist
    highest_known = 1835    # the highest number that got a response
    lowest_unknown = 999999      # the lowest seen number that got a response
    latest_id = None

    still_looking = True

    while still_looking:

        currently_guessing = []

        try:
            currently_guessing = random.sample(range(highest_known, lowest_unknown), ping_size)
        except:
            currently_guessing = random.sample(range(highest_known - check_width, lowest_unknown + check_width), ping_size)

        # get information
        id_string = ''
        for id in currently_guessing:
            id_string += str(id) + ','
        r = requests.get('https://bandcamp.com/api/notabletralbum/2/get?id=' + id_string)

        # see what becomes valid and invalid
        results = r.json()

        # for each guess, get next check_width entry ids
        for id in currently_guessing:
            # make check
            check_string = ''
            for i in range(check_width - 1):
                check_string += str(id + i) + ','

            check = requests.get('https://bandcamp.com/api/notabletralbum/2/get?id=' + check_string)
            check = check.json()
            
            # if a single one returns then it is the new highest known
            if check != {}:
                # it is not empty
                if len(check) == 1:
                    still_looking = False
                    latest_id = id
                    break
                if id > highest_known:
                    highest_known = id
            else:
                # it is empty
                if id < lowest_unknown:
                    lowest_unknown = id

    return latest_id


class NewAndNotable():

    def __init__(self, num_to_get: int = 5):
        self.albums = []

        current_id = get_current_new_and_notable_id()
        #ids = []
        id_string = ''

        for i in range(num_to_get):
            id_string += (str(current_id - i)) + ','

        entries = requests.get('https://bandcamp.com/api/notabletralbum/2/get?id=' + id_string)
        entries = entries.json()

        for key in entries:
            album = NewAndNotableAlbum()
            entry = {}
            entry = entries[str(key)]

            album.album_artist = entry['artist']

            album.album_title = entry['title']

            album.album_art = "https://f4.bcbits.com/img/a" + str(entry['art_id']) + "_0"

            album.album_url = entry['tralbum_url']

            album.genre = entry['genre']

            album.date_published = datetime.strptime(entry['published_date'], '%d %b %Y %H:%M:%S %Z')
            album.date_published = int(time.mktime(album.date_published.timetuple()))

            album.date_last_modified = datetime.strptime(entry['mod_date'], '%d %b %Y %H:%M:%S %Z')
            album.date_last_modified = int(time.mktime(album.date_last_modified.timetuple()))

            album.description = entry['desc']

            album.advanced['band_id'] = entry['band_id']
            album.advanced['album_id'] = entry['tralbum_id']
            album.advanced['art_id'] = entry['art_id']
            album.advanced['featured_track_id'] = entry['featured_track_id']

            self.albums.append(album)


class NewAndNotableAlbum():
    def __init__(self):

        self.album_artist = ""
        self.album_title = ""
        self.album_art = ""
        self.album_url = ""
        self.genre = ""
        self.date_published = 0
        self.date_last_modified = 0
        self.description = ""
        self.advanced = {}

        
class Charts:
    def __init__(
            self,
            main_genre: str = "all",
            sort: str = "top",
            page: int = 0,
            format: str = 'all',
            subgenre: str = ""):

        self.albums = []

        if not main_genre:
            main_genre = "all"

        if not sort:
            sort = 'top'

        if page is None or not page:
            page = 0

        if not format:
            format = 'all'

        if not subgenre:
            subgenre = ""

        arg_string = ""

        arg_string += 'g=' + main_genre

        arg_string += '&s=' + sort

        if main_genre != 'all' and ('rec' not in sort):
            # can contain subgenre
            arg_string += '&t=' + subgenre

        if 'rec' not in sort:
            # can contain format
            arg_string += '&f=' + format
        else:
            # there is a artist rec filter
            # well which one
            # most or latest
            if 'most' in sort:
                arg_string += '&r=most'
            else:
                arg_string += '&r=latest'

        arg_string += '&p=' + str(page)
        
        r = requests.get('https://bandcamp.com/api/discover/3/get_web?' + arg_string)
        r = r.json()

        for current_album in r['items']:
            album = ChartsAlbum()

            album.album_artist = current_album['secondary_text']

            album.album_title = current_album['primary_text']

            if current_album['url_hints']['custom_domain'] not in ['null', 'Null', 'None']:
                album.artist_url = 'https://' + current_album['url_hints']['subdomain'] + '.bandcamp.com'
            else:
                album.artist_url = current_album['url_hints']['custom_domain']

            if current_album['url_hints']['item_type'] == 'a':
                album.album_url = album.artist_url + '/album/' + current_album['url_hints']['slug']
            else:
                album.album_url = album.artist_url + '/track/' + current_album['url_hints']['slug']

            album.genre = current_album['genre_text']

            if current_album['location_text'] not in ['null', 'Null', "none", "None"] and current_album['location_text'] is not None:
                album.artist_location = current_album['location_text']
            else:
                album.artist_location = ""

            album.date_published = datetime.strptime(current_album['publish_date'], '%d %b %Y %H:%M:%S %Z')
            album.date_published = int(time.mktime(album.date_published.timetuple()))

            album.featured_track = {
                "title": current_album['featured_track']['title'],
                "id": current_album['featured_track']['id'],
                "duration": current_album['featured_track']['duration']
            }

            album.advanced = {
                "band_id": current_album['band_id'],
                "album_id": current_album['id'],
                "art_id": current_album['art_id'],
                "bio_image_id": current_album['bio_image']['image_id']
            }

            self.albums.append(album)


class ChartsAlbum:
    def __init__(self):
        self.album_artist = ""
        self.album_title = ""
        self.artist_url = ""
        self.album_url = ""
        self.genre = ""
        self.artist_location = ""
        self.date_published = 0
        self.featured_track = {}
        self.advanced = {}


class SaleFeed:
    def __init__(self, time: int = 0):

        self.sold_time = 0.00000
        #self.artist = ""
        self.purchases = []
        if time == 0:
            # looks like they didnt give a start time
            # assume they just want the whatever the latest is
            r = requests.get('https://bandcamp.com/api/salesfeed/1/get')
        else:
            r = requests.get('https://bandcamp.com/api/salesfeed/1/get?start_date=' + str(time))

        r = r.json()
        for sale in r['events']:

            bought_items = []

            self.sold_time = sale['utc_date']

            for current_item in sale['items']:
                # because you can buy multiple items
                item = Item()

                item.price = {
                    "currency": current_item['currency'],
                    "price": current_item['item_price'],
                    "paid": current_item['amount_paid']
                }

                item.description = current_item['item_description']

                item.url = 'https:' + current_item['url']

                if current_item['slug_type'] == 'a':
                    item.type = 'album'
                elif current_item['slug_type'] == 't':
                    item.type = 'track'
                elif current_item['slug_type'] == 'b':
                    item.type = 'discography'
                else:
                    item.type = 'physical'

                if item.type == 'physical':
                    item.image_url = "https://f4.bcbits.com/img/" + str(current_item['package_image_id']) +"_0.jpg"
                else:
                    item.image_url = "https://f4.bcbits.com/img/a" + str(current_item['art_id']) +"_0.jpg"
                bought_items.append(item)

            self.purchases.append(bought_items)

        
class Item:
    def __init__(self):
        self.price = {}
        # {
        #   "price": 0.00,
        #   "paid": 0.00,
        #   "currency": "USD"
        # }
        self.image_url = ""

        self.description = ""

        self.type = ""
        # t for track
        # p seems to be for physical
        # a for album
        # b is full disco

        self.url = ""


class BandcampWeekly():

    def __init__(self):

        # time
        self.date_released = 0
        self.date_published = 0

        # image
        self.image_url = ""

        # audio
        self.stream_url = ""
        self.duration_seconds = 0.00

        # episode
        self.episode_title = ""
        self.series_title = "" # Normal BCW or the hipho show
        self.episode_description_long = ""
        self.episode_description_short = ""
        self.episode_subtitle = ""
        self.episode_id = 0

        # tracks
        self.tracks = []

    def get_show(self, id: int):
        if id == 0:
            r = requests.get('https://bandcamp.com/api/bcweekly/3/list')
            r = r.json()
            id = r['results'][0]['id']
        
        r = requests.get("https://bandcamp.com/api/bcweekly/2/get?id=" + str(id))
        r = r.json()

        self.date_released = datetime.strptime(r['date'], '%d %b %Y %H:%M:%S %Z')
        self.date_released = int(time.mktime(self.date_released.timetuple()))

        self.date_published = datetime.strptime(r['published_date'], '%d %b %Y %H:%M:%S %Z')
        self.date_published = int(time.mktime(self.date_published.timetuple()))

        self.image_url = "https://f4.bcbits.com/img/" + str(r['show_image_id']) + '_0.jpg'

        self.stream_url = r['audio_stream']['mp3-128']

        self.duration_seconds = r['audio_duration']

        self.episode_title = r['audio_title']
        self.series_title = r['title']
        self.episode_description_long = r['desc']
        self.episode_description_short = r['short_desc']
        self.episode_subtitle = r['subtitle']
        self.episode_id = r['show_id']
        self.tracks = []

        for track in r['tracks']:
            track_object = BandcampWeeklyTrack()

            if track['label'] != None:
                track_object.label_title = track['label']

            try:
                track_object.art_url = "https://f4.bcbits.com/img/a" + str(track['track_art_id']) + "_0.jpg"
            except:
                pass
            
            try:
                if track['album_title'] != None:
                    track_object.album_title = track['album_title']
                else:
                    track_object.album_title = track['title']
            except:
                pass

            track_object.price = {
                "currency": track['currency'],
                "amount": track['price']
            }
            if '/album/' in track['url']:
                track_object.artist_url = track['url'].split('/album/')[0]
                track_object.album_title = track['album_title']
            else:
                track_object.artist_url = track['url'].split('/track/')[0]

            try:
                track_object.album_url = track['album_url']
            except:
                pass

            track_object.track_url = track['track_url']
            track_object.track_title = track['title']
            track_object.artist_title = track['artist']

            try:
                track_object.location = track['location_text']
            except:
                pass
            
            track_object.start_timecode = track['timecode']

            self.tracks.append(track_object)

        return self


class BandcampWeeklyTrack():

    def __init__(self):
        self.art_url = ""
        self.album_title = ""
        self.label_title = ""
        self.price = {}
            # "currency": "USD",
            # "amount": 0.00
        self.artist_url = ""
        self.album_url = ""
        self.track_url = ""
        self.track_title = ""
        self.artist_title = ""
        self.location = ""
        self.start_timecode = 0
