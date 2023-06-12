
import googlemaps, json, random, time
from decouple import config

class Google():
    """Uses the Google Maps API to grab restaurants within a certain radius and select a random restaurant from the data."""

    def __init__(self):
        """Initializes the maps client that all API requests use"""
        
        self.gmaps = googlemaps.Client(key=config('API_KEY'))


    def _miles_to_meters(self, miles):
        """Converts miles to meters"""

        return int(abs(miles) * 1609.34)
    
    def _trim_data(self, data):
        """Removes restaurants from file based on type tags"""

        TYPES_TO_REMOVE = ['gas_station'] # Removal tags

        for place in data:
            if any(tag in TYPES_TO_REMOVE for tag in place['types']):
                data.remove(place)

        return data
    
    def _set_coordinates(self, location):
        """Checks if a given location are a set of coordinates and makes them that if necessary"""

        if type(location) != tuple:
            coordinates = self.geocode_location(location)
        else:
            coordinates = tuple([round(num, 4) for num in location]) # Turn into helper function

        return coordinates
    
    def _get_response(self, location, radius, type, keyword=None, open_now=True, page_token=None, min_price=None, max_price=None):
        """Creates a places_nearyby request from provided parameters"""
        response = self.gmaps.places_nearby(
            location=location,
            radius=radius,
            keyword=keyword,
            min_price=None,
            max_price=None,
            open_now=open_now,
            type=type,
            page_token=page_token
        )
        return response

    def geocode_location(self, location):
        """Converts a place/address/Place ID into coordinates"""

        geocode_results = tuple([round(num, 4) for num in self.gmaps.geocode(location)[0]['geometry']['location'].values()])
        return geocode_results

    def reverse_geocode_location(self, coordinates):
        """Converts a tuple of coordinates to an address"""

        reverse_geocode_results = self.gmaps.reverse_geocode(coordinates)[0]['formatted_address']
        return reverse_geocode_results 
    
    def geolocate(self):
        return self.gmaps.geolocate()
    
    def nearby_search(self, location, distance=1, keyword=None):
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
            type=place_type, 
            keyword=keyword)

        if keyword != None:
            data = self._trim_data(response['results'])
        else:
            data = self._trim_data(response['results'])[:result_limiter] # Limits the number of results
        next_page_token = response.get('next_page_token')

        # Goes to the next page of results from the request until everything is grabbed
        while next_page_token:
            time.sleep(2) # Prevents repeat data
            response = self._get_response(
                location=coordinates, 
                radius=distance_in_meters, 
                open_now=open_now, 
                type=place_type, 
                keyword=keyword,
                page_token=next_page_token)
            
            data.extend(self._trim_data(response.get('results')))
            next_page_token = response.get('next_page_token')

        # Writes data to a json for testing
        # with open('JSONs/test.json', 'w') as file:
        #     json.dump(data, file, indent=4)

        pick = random.choice(data)
        return pick
