import googlemaps
import json
import geojson
import random
import math
import numpy as np
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
import os.path
import time

class Node:
    # Class used to represent the busenesses in the network

    def __init__(self, name = '', lat=0, long=0, rating=0, buss_type='', buss_categories = [], buss_image = '', buss_city = '', comp_time = 0, open_hours=[]):
        self.lat = lat
        self.long = long
        self.name = name
        self.rating = rating
        self.buss_type = buss_type
        self.buss_image = buss_image
        self.buss_city = buss_city
        self.id = ''
        self.comp_time = comp_time
        self.buss_categories = buss_categories
        self.open_hours = open_hours

    def geo_interface(self):
        self.id = '{}_{}_Node'.format(time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"))
        return {'type': 'feature', 'geometry':{ 'type' : 'point', 'coordinates': (self.lat,self.long) },
                'properties': {'name' : self.name, 'rating' : self.rating, 'buss_type' : self.buss_type, 'buss_categories':self.buss_categories,
                               'buss_image' : self.buss_image, 'buss_city' : self.buss_city, 'comp_time' : self.comp_time, 'open_hours' : self.open_hours }, 'id' : self.id}


class Edge:
    # Class used to represent the conections betweeen busenesses in the network

    def __init__(self, start_name = '', start_location = 0.0, end_name = '', end_location = 0.0, duration = 0, travel_type = 'driving', id = '', ran = 'No'):
        self.start_name = start_name
        self.start_location = start_location
        self.end_name = end_name
        self.end_location = end_location
        self.name = (start_name,end_name)
        self.duration = {'{}'.format(travel_type) : duration}
        self.id = id
        self.ran = ran

    def geo_interface(self):
        self.id = '{}_{}_Edge'.format(time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"))
        return {'type': 'feature', 'geometry':{ 'type' : 'linestring', 'coordinates': (self.start_location,self.end_location) },
                'properties': {'name' : self.name, 'start_name' : self.start_name, 'end_name' : self.end_name,'duration' : self.duration, 'randon' : self.ran}, 'id' : self.Id}
        

def get_distances(start = [], end = [], travel_type  = 'driving', mode = 'GoogleMaps'):
    # Get the traveling distance between all the points in the network with the google maps API

    distances = {}

    if mode == 'GoogleMaps':
        Key = 'AIzaSyDHL5tcjxM6Q7Iyy3nNRoZV2IMLYQrm7Uk'
        client = googlemaps.Client(self.Key)
        for start_slice in [start[i-1:i+9] for i in itertools.islice(start,0,None,10)]:
            for end_slice in [end[i-1:i+9] for i in itertools.islice(end,0,None,10)]:
                matrix = client.distance_matrix([(node.lat,node.long) for node in start_slice], [(node.lat,node.long) for node in end_slice], mode = travel_type)
                for origin in len(matrix["origin_addresses"]):
                    for destination in len(matrix["destination_addresses"]):
                        distances[(start[origin].name, end[destinations].name)] = matrix['rows'][origin]['elements'][destination]['duration']['value']

    if mode == 'Random':
        for node1 in start:
            for node2 in end:
                distances[(node1.name, node2.name)] = random.randint(2,20)

    return distances
        

def find_locations(city_name, max_points = 100):
    #Generation of random point location in a city area

    city_names = make_sure('city_names')

    assert city_name in city_names.keys()

    points = []
    for i in range(0,max_points):
        lat = round(random.uniform(city_names[city_name]['N'],city_names[city_name]['S']),6)
        long = round(random.uniform(city_names[city_name]['E'],city_names[city_name]['W']),6)
        points.append((lat,long))

    return points


def Add_nodes(city_name = 'San_Francisco', buss_type = 'Restaurants' , number = 100):
    # Ussing the Yelp library for Yelp authentification and requesting info


    auth = Oauth1Authenticator(
        consumer_key="zjqZkY01Asrg3kl0GZZj6g",
        consumer_secret="xoxaAfxSQoSzK-Vh64Hb2cNSoak",
        token="vNjjZ8y5FgjCEmFjerH7Uy9jG9lckHMs",
        token_secret="uCiFq4mzxRGMIhb-d7u3qFRJaUU"
    )
        
    client = Client(auth)

    buss_types = make_sure('buss_types')

    assert buss_type in buss_types.keys()

    locations = find_locations(city_name,number)

    if os.path.isfile('Data/{}_Data.json'.format(city_name)) == False:
        with open('Data/{}_Data.json'.format(city_name),'w') as f:
            geojson.dump({"type": "FeatureCollection","features": []}, f)

    with open('Data/{}_Data.json'.format(city_name)) as f:
            data = json.load(f)

    IDs = []    
    added = 0
    nodes_added = []

    for feature in [feature for feature in data['features'] if feature['geometry']['type'] == 'point']:
        IDs.append(feature['properties']['name'])

    for lat,long in locations:
        places = client.search_by_coordinates(lat, long, buss_type)
        for business in places.businesses:
            if business.name not in IDs:
                IDs.append(business.name)
                node = Node(business.name, business.location.coordinate.latitude, business.location.coordinate.longitude, business.rating,
                            buss_type, business.categories, business.image_url, city_name, comp_time = buss_types[buss_type]['durations'])
                data['features'].append(node.geo_interface())
                nodes_added.append(node)
                added += 1

    with open('Data/{}_Data.json'.format(city_name), 'w') as f:
        geojson.dump(data, f)

    return '{} nodes added'.format(added)





