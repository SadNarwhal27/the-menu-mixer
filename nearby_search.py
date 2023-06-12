
import googlemaps, json, random, math, os
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
    
    def set_coordinates(self, location):
        """Checks if a given location are a set of coordinates and makes them that if necessary"""

        if type(location) != tuple:
            coordinates = self.geocode_location(location)
        else:
            coordinates = tuple([round(num, 4) for num in location]) # Turn into helper function

        return coordinates

    def _map_search_radius(self, location, radius):
        """Creates a bounding box that can be used to geographically filter results"""

        R = 6371e3 # Radius of the Earth

        radius = self._miles_to_meters(radius)

        min_lat = location[0] - radius/R*180/math.pi
        max_lat = location[0] + radius/R*180/math.pi
        min_lon = location[1] - math.asin(radius/R*180/math.pi) / math.cos(location[0]*math.pi/180)
        max_lon = location[1] + math.asin(radius/R*180/math.pi) / math.cos(location[0]*math.pi/180)

        bounding_box = {'min_lat': min_lat,'min_lon': min_lon,'max_lat': max_lat,'max_lon': max_lon,}
        return bounding_box
    
    def _filter_restaurants(self, bounding_box, data):
        print('Initial Number of Restaurants: ', len(data))
        print(bounding_box)
        new_data = []
        for place in data:
            place_coordinates = (
                round(place['geometry']['location']['lat'], 4), 
                round(place['geometry']['location']['lng'], 4)
                )
            print(place['name'], place['vicinity'], place_coordinates)
        #     # if place_coordinates[0] >= bounding_box['min_lat'] or place_coordinates[0] <= bounding_box['max_lat']:
        #     #     print('lat removed')
        #     #     data.remove(place)
        #     #     continue
        #     if place_coordinates[1] >= bounding_box['min_lon'] or place_coordinates[1] <= bounding_box['max_lon']:
        #         print('lon removed')
        #         data.remove(place)
        #         continue

        if place_coordinates[0] >= bounding_box['min_lat']:
            new_data.append(place)
        
        print(f'\n\n\nRemaining Restaurants({len(new_data)}):')
        for f in new_data:
            print(f['name'], f['vicinity'])
        return new_data


    def geocode_location(self, location):
        """Converts a place/address/Place ID into coordinates"""

        geocode_results = tuple([round(num, 4) for num in self.gmaps.geocode(location)[0]['geometry']['location'].values()])
        return geocode_results

    def reverse_geocode_location(self, coordinates):
        """Converts a tuple of coordinates to an address"""

        reverse_geocode_results = self.gmaps.reverse_geocode(coordinates)[0]['formatted_address']
        return reverse_geocode_results 
    
    def save_map_data(self, location, distance=12):
        """Takes a snapshot of an area and save the results to a JSON"""

        # Makes sure a location tuple is passed into the response request
        coordinates = self.set_coordinates(location)

        # Response parameters
        distance_in_meters = self._miles_to_meters(distance)
        place_type = 'restaurant'
        open_now = True
        keyword = None

        # Pulls place data using an API request
        response = self.gmaps.places_nearby(
            location=coordinates,
            radius=distance_in_meters,
            open_now=open_now,
            type=place_type,
            keyword=keyword,
        )

        # Sets the filename to the coordinates for easy comparison
        file_name = f"JSONs/{str(coordinates[0])},{str(coordinates[1])}.json"

        # Grabs the search results and bounding box for the completed file
        data = self._trim_data(response['results'])
        scope = self._map_search_radius(coordinates, radius=distance)
        completed_file = {'scope': scope, 'data': data}

        # Creates a formatted file in the JSONs folder
        with open(file_name, 'w') as file:
            json.dump(completed_file, file, indent=4)

    def pick_restaurant(self, file, coordinates, radius):
        """Opens a snapshot JSON file and picks a restaurant from the list"""

        all_restaurants = json.load(open(file))['data']
        restaurants = self._filter_restaurants(
            bounding_box=self._map_search_radius(coordinates, radius),
            data=all_restaurants
            )

        pick = random.choice(restaurants)
        name = pick['name']
        address = pick['vicinity']
        print(name, address)

    def compare_scopes(self, coordinates, radius):
        """Compares new search radii to existing data scopes"""

        if os.path.exists(f"JSONs/{str(coordinates[0])},{str(coordinates[1])}.json"):
            target_file = f"{str(coordinates[0])},{str(coordinates[1])}.json"
            return target_file
        else:
            target_file = None

        new_scope = self._map_search_radius(coordinates, radius)

        # Checks each file 
        for file_name in os.listdir('JSONs/'):
            file = json.load(open(f"JSONs/{file_name}"))
            existing_scope = file['scope']
            if new_scope['min_lat'] > existing_scope['min_lat']:
                continue
            elif new_scope['min_lon'] > existing_scope['min_lon']:
                continue
            elif new_scope['max_lat'] < existing_scope['max_lat']:
                continue
            elif new_scope['max_lon'] < existing_scope['max_lon']:
                continue
            else:
                target_file = file_name
                return target_file
        
        return target_file

google = Google()

location = 'mt pleasant, mi'
# location = (43.4081,-084.475)
search_radius = 5

coordinates = google.set_coordinates(location)
target_file = google.compare_scopes(coordinates=coordinates, radius=search_radius)

if target_file == None:
    google.save_map_data(coordinates)
    file_name = f"JSONs/{str(coordinates[0])},{str(coordinates[1])}.json"
    google.pick_restaurant(file_name, coordinates, search_radius)
else:
    google.pick_restaurant(f"JSONs/{target_file}", coordinates, search_radius)
