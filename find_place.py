
import googlemaps, random, math, os
from decouple import config

class Google():
    """Uses the Google Maps API to grab restaurants within a certain radius and select a random restaurant from the data."""

    def __init__(self):
        """Initializes the maps client that all API requests use"""
        
        self.gmaps = googlemaps.Client(key=config('API_KEY'))


    def _miles_to_meters(self, miles):
        """Converts miles to meters"""

        return int(abs(miles) * 1609.34)

    def _set_coordinates(self, location):
        """Checks if a given location are a set of coordinates and makes them that if necessary"""

        if type(location) != tuple:
            coordinates = self._geocode_location(location)
        else:
            coordinates = tuple([round(num, 4) for num in location]) # Turn into helper function

        return coordinates
    
    def _geocode_location(self, location):
        """Converts a place/address/Place ID into coordinates"""

        geocode_results = tuple([round(num, 4) for num in self.gmaps.geocode(location)[0]['geometry']['location'].values()])
        return geocode_results
    
    def find_place(self, location, search_radius):
        radius_in_meters = self._miles_to_meters(search_radius)
        coordinates = self._set_coordinates(location)

        restaurants = self.gmaps.find_place(
            input='restaurant',
            input_type='textquery',
            fields=['name', 'formatted_address'],
            location_bias=f"circle:{radius_in_meters}@{coordinates[0]},{coordinates[1]}"
        )

        return restaurants
    
google = Google()
print(google.find_place('breckenridge, mi', 1))