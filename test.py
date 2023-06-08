# TODO Turn this whole thing into a class

import googlemaps, json, random, math, os
from decouple import config

def miles_to_meters(miles):
    """Converts miles to meters"""

    return int(abs(miles) * 1609.34)

def save_map_data(gmaps, location, distance=10):
    """Takes a snapshot of an area and save the results to a JSON"""

    # Makes sure a location tuple is passed into the response request
    if type(location) != tuple:
        coordinates = geocode_location(gmaps, location)
    else:
        coordinates = location

    distance = miles_to_meters(distance)
    place_type = 'restaurant'
    open_now = True
    keyword = None

    response = gmaps.places_nearby(
        location=coordinates,
        radius=distance,
        open_now=open_now,
        type=place_type,
        keyword=keyword,
    )

    # Sets the filename to the coordinates for easy comparison
    file_name = f"{str(coordinates[0])},{str(coordinates[1])}"

    # Creates a formatted file in the JSONs folder
    with open(f"JSONs/{file_name}.json", 'w') as file:
        json.dump(response['results'], file, indent=4)

def pick_restaurant(file):
    """Opens a snapshot JSON file and picks a restaurant from the list"""

    restaurants = json.load(open(file))
    pick = random.choice(restaurants)
    name = pick['name']
    coordinates = tuple(pick['geometry']['location'].values())
    print(name, coordinates)

def map_search_radius(location, radius):
    """Creates a bounding box that can be used to geographically filter results"""

    R = 6371e3 # Radius of the Earth

    min_lat = location[0] - radius/R*180/math.pi
    max_lat = location[0] + radius/R*180/math.pi
    min_lon = location[1] - math.asin(radius/R*180/math.pi) / math.cos(location[0]*math.pi/180)
    max_lon = location[1] + math.asin(radius/R*180/math.pi) / math.cos(location[0]*math.pi/180)

    bounding_box = {'min_lat': min_lat,'min_lon': min_lon,'max_lat': max_lat,'max_lon': max_lon,}
    return bounding_box

def geocode_location(gmaps, location):
    """Converts a place/average/Place ID into coordinates"""

    geocode_results = tuple([round(num, 4) for num in gmaps.geocode(location)[0]['geometry']['location'].values()])
    return geocode_results

def reverse_geocode_location(gmaps, coordinates):
    """Converts a tuple of coordinates to an address"""

    reverse_geocode_results = gmaps.reverse_geocode(coordinates)[0]['formatted_address']
    return reverse_geocode_results


gmaps = googlemaps.Client(key=config('API_KEY'))

# location = 'Breckenrige, MI'
location = (43.4081,-84.475)

if type(location) != tuple:
    coordinates = geocode_location(gmaps, location)
else:
    coordinates = location

file_name = f"JSONs/{str(coordinates[0])},{str(coordinates[1])}.json"

if os.path.isfile(file_name):
    pick_restaurant(file_name)
else:
    save_map_data(gmaps, coordinates)
    pick_restaurant(file_name)