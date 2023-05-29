from datetime import datetime
import time
import requests

class Label:
    def __init__(self, label_id: int | str):
        self.label_id: int = 0
        self.label_title: str = ""
        self.profile_picture_id: int = 0
        self.profile_picture_url: str = ""
        self.url: str = ""
        self.type: str = "label"
        self.bio: str = ""
        self.links: list = []   # list of url strings
        self.albums: list = []
        # {
        #   "album_id": 0123456789,
        #   "album_title": "album_here",
        #   "type": "album",
        #   "artist_id": 0123456789,
        #   "artist_title": "name_here",
        #   "date_released_unix": 0123456789,
        #   "purchasable": True/False
        # }
        self.location: str = ""
        self.artists: list = []

        response = requests.get(
            url="https://bandcamp.com/api/mobile/25/band_details?band_id=" + str(label_id),
        )
        result = response.json()

        self.label_id = result['id']
        self.label_title = result['name']

        self.profile_picture_id = result['bio_image_id']
        self.profile_picture_url = "https://f4.bcbits.com/img/" + str(self.profile_picture_id) + "_0.jpg"

        self.url = result['bandcamp_url']
        self.bio = result['bio']

        for link in result['sites']:
            self.links.append(link['url'])

        for album in result['discography']:
            date_released = album['release_date']
            date_released = datetime.strptime(date_released, '%d %b %Y %H:%M:%S %Z')
            date_released = int(time.mktime(date_released.timetuple()))
            self.albums.append(
                {
                    "album_id": album['item_id'],
                    "album_title": album['title'],
                    "type": album['item_type'],
                    "artist_id": album['band_id'],
                    "artist_title": album['artist_name'],
                    "date_released_unix": date_released,
                    "purchasable": album["is_purchasable"]
                }
            )

        self.location = result['location']

        for artist in result['artists']:
            self.artists.append(
                {
                    "artist_id": artist['id'],
                    "artist_title": artist['name'],
                    "artist_image_id": artist['image_id'],
                    "artist_image_url": "https://f4.bcbits.com/img/" + str(artist['image_id']) + "_0.jpg",
                    "date_signed": artist['featured_date'],
                    "location": artist['location']
                }
            )
