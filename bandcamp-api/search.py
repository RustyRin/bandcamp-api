import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def clean_string(string):
    return ' '.join(string.split())

def search_artists(search_string: str):
    link = "https://bandcamp.com/search?q=" + search_string + '&item_type=b'
    try:
        response = requests.get(link)
    except requests.exceptions.MissingSchema as err:
        return err

    try:
        soup = BeautifulSoup(response.tex, "lxml")
    except:
        soup = BeautifulSoup(response.text, "html.parser")

    results = soup.find('ul', {"class": "result-items"})
    things_to_return = []

    for item in results.find_all("li"):
        band = ArtistResults()
        band.artist_title = ' '.join(item.find('div', {"class": "heading"}).text.split())
        
        try:
            band.location = ' '.join(item.find('div', {"class": "subhead"}).text.split())
        except:
            band.location = ""

        try:
            band.genre = ' '.join(item.find("div", {"class": "genre"}).text.split())
        except:
            band.genre = ''

        try:
            band.tags = ' '.join(item.find('div', {'class': "tags data-search"}).text.split())
            band.tags = band.tags.split(": ")[1:]
            band.tags = ' '.join(band.tags).split(', ')
        except:
            band.tags = []

        try:
            band.image_url = item.find('img').get('src').split('_')[0]
            band.image_url = band.image_url + '_0.jpg'
        except:
            band.image = ""

        band.artist_url = item.find('div', {'class': "itemurl"})
        band.artist_url = band.artist_url.find('a').text
        things_to_return.append(band)

    return things_to_return

def search_albums(search_string: str):
    link = "https://bandcamp.com/search?q=" + search_string + '&item_type=a'
    try:
        response = requests.get(link)
    except requests.exceptions.MissingSchema as err:
        return err

    try:
        soup = BeautifulSoup(response.tex, "lxml")
    except:
        soup = BeautifulSoup(response.text, "html.parser")

    results = soup.find('ul', {"class": "result-items"})
    things_to_return = []

    for item in results.find_all("li"):
        album = AlbumResults()

        album.album_title = clean_string(item.find('div', {"class": "heading"}).text)

        album.artist_title = clean_string(item.find('div', {"class": "subhead"}).text[3:])

        album.total_tracks = clean_string(item.find('div', {"class": "length"}).text)
        album.total_tracks = int(''.join(album.total_tracks).split(' track')[0])

        album.duration_seconds = int(item.find('div', {"class": 'length'}).text.split(', ')[1].split( )[0])*60

        album.date_released = ' '.join(item.find('div', {'class': "released"}).text.split())[9:]
        album.date_released = datetime.strptime(album.date_released, '%d %B %Y')
        album.date_released = int(time.mktime(album.date_released.timetuple()))

        album.album_url = clean_string(item.find('div', {"class": "itemurl"}).text)

        album.tags = ' '.join(item.find('div', {'class': "tags data-search"}).text.split())
        album.tags = album.tags.split(": ")[1:]
        album.tags = ' '.join(album.tags).split(', ')

        album.album_art_url = item.find('div', {"class": "art"})
        album.album_art_url = album.album_art_url.find('img').get('src')[:-5] + '0.jpg'
        
        things_to_return.append(album)

    return things_to_return


def search_tracks(search_string: str):
    link = "https://bandcamp.com/search?q=" + search_string + '&item_type=t'
    try:
        response = requests.get(link)
    except requests.exceptions.MissingSchema:
        None

    try:
        soup = BeautifulSoup(response.tex, "lxml")
    except:
        soup = BeautifulSoup(response.text, "html.parser")

    results = soup.find('ul', {"class": "result-items"})
    things_to_return = []

    for item in results.find_all("li"):
        track = TrackResults()

        track.track_title = clean_string(item.find('div', {"class": "heading"}).text)

        track.album_title = clean_string(item.find('div', {"class": "subhead"}).text).split(' by ')[0].replace('from ', '')
        
        track.artist_title = clean_string(item.find('div', {'class': "subhead"}).text).split('by ')[1]

        track.date_released = ' '.join(item.find('div', {'class': "released"}).text.split())[9:]
        track.date_released = datetime.strptime(track.date_released, '%d %B %Y')
        track.date_released = int(time.mktime(track.date_released.timetuple()))

        track.album_art_url = item.find('img').get('src').split('_')[0] +'_0.jpg'

        track.track_url = clean_string(item.find('div', {'class': "itemurl"}).text)
        
        things_to_return.append(track)

    return things_to_return

def search_fans(search_string: str):
    link = "https://bandcamp.com/search?q=" + search_string + '&item_type=f'
    try:
        response = requests.get(link)
    except requests.exceptions.MissingSchema:
        None

    try:
        soup = BeautifulSoup(response.tex, "lxml")
    except:
        soup = BeautifulSoup(response.text, "html.parser")

    results = soup.find('ul', {"class": "result-items"})
    things_to_return = []

    for item in results.find_all("li"):
        fan = FanResults()

        fan.username = clean_string(item.find("div", {"class": "heading"}).text)
        fan.fan_url = clean_string(item.find('div', {"class": "itemurl"}).text)

        try:
            fan.genre = clean_string(item.find('div', {"class": "genre"}).text).split(': ')[1]
        except:
            fan.genre = ""

        try:
            fan.profile_picture_url = clean_string(item.find('img').get('src')).split('_')[0]+'_0.jpg'
        except:
            fan.profile_picture_url = ""

        things_to_return.append(fan)

    return things_to_return


class ArtistResults():

    def __init__(self):
        self.artist_title = ""
        self.location = ""
        self.genre = ""
        self.tags = []
        self.image_url = ""
        self.artist_url = ""

class AlbumResults():

    def __init__(self):
        self.album_title = ""
        self.artist_title = ""
        self.total_tracks = 0
        self.duration_seconds = 0
        self.date_released = 0
        self.album_url = ""
        self.tags = []
        self.album_art_url = ""

class TrackResults():

    def __init__(self):
        self.track_title = ""
        self.album_title = ""
        self.artist_title = ""
        self.date_released = 0
        self.album_art_url = ""
        self.track_url = ""

class FanResults():

    def __init__(self):
        self.username = ""
        self.fan_url = ""
        self.genre = ""
        self.profile_picture_url = ""