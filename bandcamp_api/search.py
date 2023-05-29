import requests


class SearchResultsItemArtist:

    def __init__(self):
        self.type = 'artist'
        self.artist_id = 0
        self.art_id = 0
        self.image_id = 0
        self.artist_title = ""
        self.location = ""
        self.is_label = False
        self.tags = []
        self.image_url = ""
        self.genre = ""
        self.part = ""
        self.artist_url = ""
        self.url = ""


class SearchResultsItemAlbum:

    def __init__(self):
        self.type = "album"
        self.album_id = 0
        self.art_id = 0
        self.image_id = 0
        self.album_title = ""
        self.artist_id = 0
        self.artist_title = ""
        self.image_url = ""
        self.part = ""
        self.album_url = ""
        self.artist_url = ""
        self.url = ""


class SearchResultsItemTrack:

    def __init__(self):
        self.type = "track"
        self.track_id = 0
        self.art_id = 0
        self.image_id = 0
        self.track_title = ""
        self.artist_id = 0
        self.artist_title = ""
        self.album_title = ""
        self.image_url = ""
        self.album_id = ""
        self.part = ""
        self.track_url = ""
        self.artist_url = ""
        self.url = ""


class SearchResultsItemFan:

    def __init__(self):
        self.type = "fan"
        self.fan_id = 0
        self.art_id = 0
        self.image_id = 0
        self.fan_name = ""
        self.fan_username = ""
        self.collection_size = 0
        self.fan_genre = ""
        self.fan_image = ""
        self.fan_image_id = ""
        self.part = ""
        self.url = ""


def search(search_string: str = ""):
    # I got this api url from the iOS app
    # needs a way of removing characters
    # that will screw up an url
    # keep url safe characters

    response = requests.get(
        "https://bandcamp.com/api/fuzzysearch/2/app_autocomplete?q=" + search_string + "&param_with_locations=true")

    results = response.json()['results']

    return_results = []

    for item in results:
        # going item by item
        if item['type'] == 'b':
            # For bands and record labels
            # need to make a try catch for labels
            # normal bands do not have "artists" element
            # if it does have it, normal artist, if it does, use label object
            results_object = SearchResultsItemArtist()
            results_object.artist_id = item['id']
            results_object.art_id = item['art_id']
            results_object.image_id = item['img_id']
            results_object.artist_title = item['name']
            results_object.location = item['location']
            results_object.is_label = item['is_label']

            try:
                for tag in item['tag_names']:
                    results_object.tags.append(tag)
            except TypeError:
                pass

            results_object.image_url = "https://f4.bcbits.com/img/0000" + str(results_object.image_id) + '_0.png'

            # I have seen some bands with no main genre
            try:
                results_object.genre = item['genre_name']
            except KeyError:
                pass

            # no idea what "part" is
            # it seems to always be "z"
            try:
                results_object.part = item['part']
            except KeyError:
                pass

            results_object.artist_url = item['url']
            results_object.url = results_object.artist_url

            return_results.append(results_object)

        elif item['type'] == 'a':
            # album
            results_object = SearchResultsItemAlbum()
            results_object.album_id = item['id']
            results_object.art_id = item['art_id']
            results_object.image_id = item['img_id']
            results_object.album_title = item['name']
            results_object.artist_id = item['band_id']
            results_object.artist_title = item['band_name']
            results_object.image_url = "https://f4.bcbits.com/img/a" + str(item['art_id']) + '_0.png'
            results_object.part = item['part']

            # the url given if weird
            # it is in the style of https://bandname.bandcamp.comhttps://bandname.bandcamp.com/album/albumname
            # this should split it
            results_object.artist_url = 'https' + item['url'].split('https')[1]
            results_object.album_url = 'https' + item['url'].split('https')[2]
            results_object.url = results_object.album_url

            return_results.append(results_object)

        elif item['type'] == 't':
            # track
            results_object = SearchResultsItemTrack()
            results_object.track_id = item['id']
            results_object.art_id = item['art_id']
            results_object.track_title = item['name']
            results_object.artist_id = item['band_id']
            results_object.artist_title = item['band_name']
            results_object.album_title = item['album_name']
            results_object.album_id = item['album_id']
            results_object.image_url = "https://f4.bcbits.com/img/a" + str(item['art_id']) + "_0.png"
            results_object.part = item['part']
            results_object.artist_url = 'https' + item['url'].split('https')[1]
            results_object.track_url = 'https' + item['url'].split('https')[2]
            results_object.url = results_object.track_url

            return_results.append(results_object)

        elif item['type'] == "f":
            # fan
            results_object = SearchResultsItemFan()
            results_object.fan_id = item['id']
            results_object.art_id = item['art_id']
            results_object.image_id = item['img_id']
            results_object.fan_name = item['name']
            results_object.fan_username = item['username']
            results_object.collection_size = item['collection_size']
            results_object.fan_genre = item['genre_name']
            results_object.fan_image = "https://f4.bcbits.com/img/" + str(item['img_id']) + '_0.png'
            results_object.part = item['part']
            results_object.url = item['url']

            return_results.append(results_object)

    return return_results
