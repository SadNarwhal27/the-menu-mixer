import math, os, time, json

def map_search_radius(self, location, radius):
    """Creates a bounding box that can be used to geographically filter results"""

    R = 6371e3 # Radius of the Earth

    radius = self._miles_to_meters(radius)

    min_lat = location[0] - radius/R*180/math.pi
    max_lat = location[0] + radius/R*180/math.pi
    min_lon = location[1] - math.asin(radius/R*180/math.pi) / math.cos(location[0]*math.pi/180)
    max_lon = location[1] + math.asin(radius/R*180/math.pi) / math.cos(location[0]*math.pi/180)

    bounding_box = {'min_lat': min_lat,'min_lon': min_lon,'max_lat': max_lat,'max_lon': max_lon,}
    return bounding_box

# TODO This needs to be reworked
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

# TODO Needs to be reworked
def filter_restaurants(self, bounding_box, data):
    print('Initial Number of Restaurants: ', len(data))
    print(bounding_box)
    new_data = []
    for place in data:
        place_coordinates = (
            round(place['geometry']['location']['lat'], 4), 
            round(place['geometry']['location']['lng'], 4)
            )
        # print(place['name'], place['vicinity'], place_coordinates)
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
    # for f in new_data:
    #     print(f['name'], f['vicinity'])
    return new_data

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
    data = self._trim_data(response['results'])
    next_page_token = response.get('next_page_token')

    # Goes to the next page of results from the request until everything is grabbed
    while next_page_token:
        time.sleep(2) # Prevents repeat data
        response = self.gmaps.places_nearby(
            location=coordinates,
            radius=distance_in_meters,
            open_now=open_now,
            type=place_type,
            keyword=keyword,
            page_token=next_page_token
        )
        data.extend(response.get('results'))
        next_page_token = response.get('next_page_token')

    # Sets the filename to the coordinates for easy comparison
    file_name = f"JSONs/{str(coordinates[0])},{str(coordinates[1])}.json"

    # Grabs the search results and bounding box for the completed file
    scope = self._map_search_radius(coordinates, radius=distance)
    completed_file = {'scope': scope, 'data': data}

    # Creates a formatted file in the JSONs folder
    with open(file_name, 'w') as file:
        json.dump(completed_file, file, indent=4)