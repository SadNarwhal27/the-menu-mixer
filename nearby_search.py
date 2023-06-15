"""Creates the Google class for finding nearby restaurants"""

import random
import time
# import json

import googlemaps
from decouple import config

class Google():
    """Uses the Google Maps API to grab restaurants within a certain radius and select a random 
    restaurant from the data."""

    def __init__(self):
        """Initializes the maps client that all API requests use"""

        self.gmaps = googlemaps.Client(key=config('API_KEY'))


    def _miles_to_meters(self, miles):
        """Converts miles to meters"""

        return int(abs(miles) * 1609.34)


    def _trim_data(self, data):
        """Removes restaurants from file based on type tags"""

        types_to_remove = ['gas_station', 'spa'] # Removal tags

        for place in data:
            if any(tag in types_to_remove for tag in place['types']):
                data.remove(place)

        return data


    def _set_coordinates(self, location):
        """Checks if a given location are a set of coordinates and makes them that if necessary"""

        if not isinstance(location, tuple):
            coordinates = self.geocode_location(location)
        else:
            coordinates = tuple(round(num, 4) for num in location) # Turn into helper function

        return coordinates


    def _get_response(self, location, radius, place_type, keyword=None,
                      open_now=True, page_token=None, min_price=None, max_price=None):
        """Creates a places_nearyby request from provided parameters"""

        response = self.gmaps.places_nearby(
            location=location,
            radius=radius,
            keyword=keyword,
            min_price=min_price,
            max_price=max_price,
            open_now=open_now,
            type=place_type,
            page_token=page_token
        )
        return response


    def _get_photos(self, photo_reference, maxwidth=500):
        """Gets the first photo associated with a place from Google"""

        photos_url = "https://maps.googleapis.com/maps/api/place/photo?&photo_reference="
        url = photos_url + photo_reference + f"&maxwidth={maxwidth}&key=" + config('API_KEY')
        return url


    def geocode_location(self, location):
        """Converts a place/address/Place ID into coordinates"""
        coordinates = self.gmaps.geocode(location)[0]['geometry']['location'].values()
        geocode_results = tuple(round(num, 4) for num in coordinates)
        return geocode_results


    def reverse_geocode_location(self, coordinates):
        """Converts a tuple of coordinates to an address"""

        reverse_geocode_results = self.gmaps.reverse_geocode(coordinates)[0]['formatted_address']
        return reverse_geocode_results


    def geolocate(self):
        """WIP Geolocation function"""

        return self.gmaps.geolocate()


    def nearby_search(self, location, distance=5, keyword=None):
        """Creates a maps Places API request to find nearby restaurants"""
        # Makes sure a location tuple is passed into the response request
        coordinates = self._set_coordinates(location)

        # Response parameters
        distance_in_meters = self._miles_to_meters(distance)
        place_type = 'restaurant'
        open_now = True
        result_limiter = 10

        # Pulls place data using an API request
        response = self._get_response(
            location=coordinates,
            radius=distance_in_meters,
            open_now=open_now,
            place_type=place_type,
            keyword=keyword)

        if keyword is not None:
            data = self._trim_data(response['results'])
        else:
            data = self._trim_data(response['results'])[:result_limiter] # Limits total results
        next_page_token = response.get('next_page_token')

        # Goes to the next page of results from the request until everything is grabbed
        while next_page_token:
            time.sleep(2) # Prevents repeat data
            response = self._get_response(
                location=coordinates,
                radius=distance_in_meters,
                open_now=open_now,
                place_type=place_type,
                keyword=keyword,
                page_token=next_page_token)

            data.extend(self._trim_data(response.get('results')))
            next_page_token = response.get('next_page_token')

        # # Writes data to a json for testing
        # with open('JSONs/test.json', 'w') as file:
        #     json.dump(data, file, indent=4)

        pick = random.choice(data)

        try:
            pick['photos'] = self._get_photos(pick['photos'][0]['photo_reference'])
        except:
            print('No photo associated with place')

        return pick
