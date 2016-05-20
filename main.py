from Get_Data import *
from Get_Tour import *
from gurobipy import *
import http.server
import json
import numpy as np
import os.path
import geojson
import random
import math


# Start setting up a simple local server

def start_server(port=8000, bind="", cgi=False):
    if cgi==True:
        http.server.test(HandlerClass=http.server.CGIHTTPRequestHandler, port=port, bind=bind)
    else:
        http.server.test(HandlerClass=http.server.SimpleHTTPRequestHandler,port=port,bind=bind)

def make_sure(what=''):

    if what == 'city_names':
        city_names = {'San_Francisco':{'N':37.806025,'E':-122.386719,'W':-122.512437,'S':37.704589},'New_York':{'N':40.870625,'E':-73.704185,'W':-74.042530,'S':40.568426},
                    'Los_Angeles':{'N':34.109175,'E':-118.176155,'W':-118.353310,'S':34.002226}, 'Chicago':{'N':41.975189,'E':-87.532883,'W':-87.851486,'S':41.709189}}
        return city_names
    elif what == 'buss_types':
        buss_types = {'Restaurants' : {'durations':random.randint(50,70), 'open_hours' : [660,960], 'categories' : []},
                      'Shopping': {'durations':random.randint(20,30), 'open_hours' : [480,1020], 'categories' : []},'Hotels & Travel': {'durations':random.randint(540,660), 'open_hours' : [1200,1440], 'categories' : []},
                      'Arts & Entertainment': {'durations':random.randint(60,120), 'open_hours' : [540,1620], 'categories' : []},'Active Life': {'durations':random.randint(40,60), 'open_hours' : [540,1200], 'categories' : []}}
        return buss_types

def writejson(object = ''):
    ''' This method writes data in to the corresponding json file '''
    if type(object) == Tour:
        if os.path.isfile('Data/Tour_Data.json') == False:
            with open('Data/Tour_Data.json','w') as f:
                geojson.dump({"type": "FeatureCollection","features": []}, f)
        
        with open('Data/Tour_Data.json') as f:
                data = json.load(f)
        with open('Data/Tour_Data.json','w') as f:
                data['features'].append(object.geo_interface())
                geojson.dump(data, f)
    else:
        if os.path.isfile('{}_Data.json'.format(object.city_name)) == False:
            with open('{}_Data.json'.format(object.city_name),'w') as f:
                geojson.dump({"type": "FeatureCollection","features": []}, f)
        
        with open('{}_Data.json'.format(object.city_name)) as f:
                data = json.load(f)
        with open('{}_Data.json'.format(object.city_name),'w') as f:
                data['features'].append(object.geo_interface())
                geojson.dump(data, f)
