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
    def __init__(self, album_id: str | int, artist_id: str | int, advanced: bool = False):
        # base album information
        self.album_title = ""
        self.album_about = ""
        self.album_credits = ""
        self.album_id = 0
        self.art_id = 0
        self.art_url = ""
        self.album_url = ""
        self.date_released_unix = 0

        # price
        self.price = {
            "currency": None,
            "amount": None
        }
        self.is_free = None
        self.is_preorder = None
        self.is_purchasable = None
        self.is_set_price = None

        # additional album info
        self.is_digital = None
        self.featured_track_id = 0
        self.record_label_title = ""
        self.record_label_id = 0
        self.require_email = None
        self.tags = []
        self.total_tracks = 0
        self.tracks = []

        self.artist_title = ""
        self.artist_id = 0
        self.artist_url = ""

        self.type = "album"
        response = requests.get(
            url="https://bandcamp.com/api/mobile/25/tralbum_details?band_id=" + str(artist_id) +
            "&tralbum_id=" + str(album_id) + "&tralbum_type=a"
        )
        result = response.json()

        # if it throws an error, that means try as a single
        try:
            if "No such tralbum for band" in result['error_message']:
                response = requests.get(
                    url="https://bandcamp.com/api/mobile/25/tralbum_details?band_id=" + str(artist_id) +
                        "&tralbum_id=" + str(album_id) + "&tralbum_type=t"
                )
                result = response.json()
                self.type = "album-single"
        except KeyError:
            pass

        # general info
        try:
            self.album_title = result['album_title']
            if self.album_title is None:
                self.album_title = result['title']
        except KeyError:
            # good chance it is a single
            # parse though track class
            print("WARNING: Could not load album, trying to load as a track...")
            self.type = "track"
            return

        try:
            self.album_about = result['about']
        except KeyError:
            pass

        try:
            self.album_credits = result['credits']
        except KeyError:
            pass

        try:
            self.album_id = result['id']
        except KeyError:
            raise FileNotFoundError('Could not find the album ID. This is either because could not find the album or \
            it is not an album (such as a track, artist, label, etc. )')

        try:
            self.art_id = result['art_id']
        except KeyError:
            pass

        if self.art_id != 0:
            self.art_url = "https://f4.bcbits.com/img/a" + str(self.art_id) + "_0.jpg"

        try:
            self.album_url = result['bandcamp_url']
        except KeyError:
            raise FileNotFoundError("Album does not have a URL, this should not happen!")

        try:
            self.date_released_unix = result['release_date']
        except KeyError:
            pass

        # price info
        try:
            self.price = {
                "currency": result['currency'],
                "amount": result['price']
            }
        except KeyError:
            pass

        if self.price['amount'] == 0 or self.price['amount'] == 0.0:
            self.is_free = True
        else:
            self.is_free = False

        try:
            self.is_preorder = result['is_preorder']
        except KeyError:
            pass

        try:
            self.is_purchasable = result['is_purchasable']
        except KeyError:
            pass

        try:
            self.is_set_price = result['is_set_price']
        except KeyError:
            pass

        # additional album info
        try:
            self.is_digital = result['has_digital_download']
        except KeyError:
            pass

        try:
            self.featured_track_id = result['featured_track_id']
        except KeyError:
            pass

        try:
            self.record_label_title = result['label']
        except KeyError:
            pass

        try:
            self.record_label_id = result['label_id']
        except KeyError:
            pass

        try:
            self.require_email = result['require_email']
        except KeyError:
            pass

        try:
            for tag in result['tags']:
                self.tags.append(tag['name'])
        except KeyError:
            pass

        try:
            self.total_tracks = result['num_downloadable_tracks']
        except KeyError:
            pass

        try:
            self.artist_title = result['tralbum_artist']
        except KeyError:
            pass

        try:
            self.artist_id = result['band']['band_id']
        except KeyError:
            pass

        try:
            self.artist_url = self.album_url.split("album")[0]
        except KeyError:
            pass

        for track in result['tracks']:
            self.tracks.append(Track(artist_id=self.artist_id, track_id=track['track_id'], advanced=advanced))

        # advanced scraping
        # the api as i understand it, does not have a way for things like copyright, reviews, supporters
        # to get these, going to use the web scraper method
        # as this is basically legacy code, it will be slightly worse c:

        if advanced is True:
            try:
                page_json = get_json(url=self.album_url)
            except:
                raise AttributeError("Error finding needed information. Either album is private/ \
                gone, or the link is malformed")

            try:
                self.copyright = page_json['copyrightNotice']
            except KeyError:
                self.copyright = ""

            self.reviews = []
            try:
                for review in page_json['comment']:
                    current_review = {}

                    try:
                        current_review["username"] = str(review['author']['name'])
                        current_review['username'] = ' '.join(current_review["username"].split())
                    except:
                        current_review["username"] = ""

                    try:
                        current_review['profile_url'] = review['author']['url']
                    except:
                        current_review['profile_url'] = ""

                    try:
                        current_review['profile_picture'] = review['author']['image']
                        current_review['profile_picture'] = current_review['profile_picture'].split('_')[0] + '_0.jpg'
                    except:
                        current_review['profile_picture']  = ""

                    try:
                        current_review['review'] = str(review['text'][0])
                        current_review['review'] = ' '.join(current_review['review'].split())
                    except:
                        current_review['review'] = ""

                    try:
                        current_review['favorite_track'] = str(review['text'][1].split(": ")[1])
                    except:
                        current_review['favorite_track'] = ""

                    self.reviews.append(current_review)
            except:
                pass

            self.supporters = []
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


def get_album(album_id: int = None):
    """With a given album ID and artist ID, get available information"""

    response = requests.get(
        url="https://bandcamp.com/api/mobile/25/tralbum_details",
        headers={"tralbum_id": str(id)}
    )


def get_json(url, debugging: bool = False):

    headers = {'User-Agent': f'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}

    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.MissingSchema:
        return None

    try:
        soup = BeautifulSoup(response.text, "lxml")
    except FeatureNotFound:
        soup = BeautifulSoup(response.text, "html.parser")

    logging.debug(" Generating BandcampJSON..")
    bandcamp_json = BandcampJSON(soup, debugging).generate()
    page_json = {}
    for entry in bandcamp_json:
        page_json = {**page_json, **json.loads(entry)}
    logging.debug(" BandcampJSON generated..")

    return page_json
