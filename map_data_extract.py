#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 12:24:44 2019

@author: Joseph
"""


import requests
import json
from geopy.geocoders import Nominatim
import math
import pandas as pd
import sys
import os.path
import time
reload(sys)
sys.setdefaultencoding('utf-8')

city_df = pd.read_csv('table-2.csv')



city_list = [city.split('[')[0] for city in city_df['City']]
state_list = [state for state in city_df['State[c]']]
city_list = [c+' '+s for c,s in zip(city_list,state_list)]
city_list = [c for c,p in zip(city_list,city_df['2018estimate']) if int(p.replace(',',''))<500000]
#city_list = ['New Haven Connecticut']
amenity_sustenance = ['restaurant','fast_food','bar','pub','cafe',\
                      'ice_cream','fast_food']
amenity_education = ['school','college','university','kindergarten','library']
amenity_healh = ['clinic','doctors','dentist','hospital','nursing_home',\
                 'pharmacy','veterinary']
amenity_arts = ['arts_centre','cinema','music_venue','nightclub','stripclub','theatre']
amenity_list = amenity_sustenance+amenity_education+amenity_healh+amenity_arts

shop_food = ['alcohol','bakery','butchers','brewing_supplies','butcher',\
             'cheese','chocolate','coffee','confectionary','convenience',\
             'deli','greengrocer','health_food','pastry','seafood']
shop_general = ['department_store','general','mall','supermarket','wholesale']
shop_clothes = ['bag','baby_goods','boutique','clothes','fabric','fashion',\
                'fashion_accessories','jewelry','shoes','watches','charity',\
                'second_hand','tailor']
shop_health = ['beauty','cosmetics','erotic','hairdresser','massage',\
               'optician','tattoo']
shop_building = ['agrarian','appliance','bathroom_furnishing','doityourself',\
                  'electrical','florist','garden_centre','glaziery','hardware',\
                  'houseware','locksmith','paint','security','trade']
#shop_list = ['books','hardware','convenience','clothes','supermarket','wholesale']
target_shop = ['books']
tag_list = dict()
for amenity in amenity_list:
    tag_list[amenity] = 'amenity'
#for shop in shop_list:
#    tag_list[shop] = 'shop'

def geocodeArea(city):
    geolocator = Nominatim(user_agent="city_compare")
    geo_results = geolocator.geocode(city, exactly_one=True)
    #just confirm the city is correct
    print geo_results.raw.get('display_name')
    #add 3600000000 to convert osm_id to area_id ~*~mysterious~*~
    area_id = 3600000000 + int(geo_results.raw.get('osm_id'))
    return str(area_id)

def query_string(area_id,tag_list):
    string = '[out:json][timeout:900];' \
    'area('+area_id+')->.searchArea;' \
    '('\
    'node["shop"](area.searchArea);'\
    'way["shop"](area.searchArea);'
    'relation["shop"](area.searchArea);'
    for key,tag in tag_list.iteritems():
        string += 'node["'+tag+'"="'+key+'"](area.searchArea);'
        string += 'way["'+tag+'"="'+key+'"](area.searchArea);'
        string += 'relation["'+tag+'"="'+key+'"](area.searchArea);'
    string +=  ');out center;'
    return string
    
#def bounding_box(lat,lon):
def make_filename(city):
    file_name = 'map_data/'+city.replace(' ','_')+'_map_data.csv'
    return file_name
def file_exists(city):
    file_name = make_filename(city)
    return os.path.isfile(file_name)
    

for city in city_list:
    if file_exists(city):
        continue
    row_list = []
    area_id = geocodeArea(city)
    q = query_string(area_id,tag_list)
    overpass_url = "http://overpass-api.de/api/interpreter"
    request_failed = True
    try_counter = 0
    while request_failed==True:
        result = requests.get(overpass_url, params={'data': q})
        try:
            data = result.json()
            request_failed=False
        except:
            try_counter += 1
            print try_counter
            time.sleep(60*try_counter)
            if try_counter>=3:
                break
    if request_failed:
        break
    data = data['elements']
    for d in data:
        row = {k:v for k,v in d.iteritems() if k in ('id','lat','lon')}
        
        tag_dict = {k:v for k,v in d['tags'].iteritems() if k in \
                    ('amenity','shop','name','addr:city','addr:housenumber',\
                     'addr:postcode','addr:state','addr:street')}
        row.update(tag_dict)
        if d['type'] in {'way','relation'}:
            row.update(d['center'])
        row['city'] = city
        row_list.append(row)
    df = pd.DataFrame(row_list)
    df.to_csv(make_filename(city))