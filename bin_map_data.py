#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 10:57:18 2019

@author: Joseph
"""

from os import listdir 
import pandas as pd
import math
import numpy as np
import csv

path = './map_data/'
file_list = listdir(path)


def lat_lon_dist(lat):
    lat_km = 110.574
    lon_km = math.cos(math.radians(lat))*111.320
    return lat_km,lon_km

def block_deg(lat_km,lon_km,block_size):
    lat_block = block_size/lat_km
    lon_block = block_size/lon_km
    return lat_block,lon_block

def bin_list(lat_block,lon_block,lat_list,lon_list):
    min_lat = lat_list.min()
    max_lat = lat_list.max()
    min_lon = lon_list.min()
    max_lon = lon_list.max()
    lat_bin_list = np.arange(min_lat-lat_block,max_lat+lat_block,lat_block)
    lon_bin_list = np.arange(min_lon-lon_block,max_lon+lon_block,lon_block)
    return lat_bin_list,lon_bin_list

def bin_lat_lon(df,bin_size):
    mean_lat = df['lat'].mean()
    lat_km,lon_km = lat_lon_dist(mean_lat)
    lat_block,lon_block = block_deg(lat_km,lon_km,bin_size)
    lat_bin_list,lon_bin_list = bin_list(lat_block,lon_block,df['lat'],df['lon'])
    df['lat_bin_no'] = pd.cut(df['lat'],lat_bin_list,labels=range(len(lat_bin_list)-1))
    df['lon_bin_no'] = pd.cut(df['lon'],lon_bin_list,labels=range(len(lon_bin_list)-1))
    df['lat_bin'] = pd.cut(df['lat'],lat_bin_list)
    df['lon_bin'] = pd.cut(df['lon'],lon_bin_list)
    len_lat_bins = len(lat_bin_list)
    len_lon_bins = len(lon_bin_list)
    df['max_lat_bin'] = len_lat_bins
    df['max_lon_bin'] = len_lon_bins
    return len_lat_bins,len_lon_bins,lat_bin_list,lon_bin_list

def combine_types(df):
    df['type'] = np.nan
    amenity_mask = df['amenity'].notnull()
    shop_mask = df['shop'].notnull()
    df.loc[amenity_mask,'type'] = df.loc[amenity_mask,'amenity']
    df.loc[shop_mask,'type'] = df.loc[shop_mask,'shop']
    
def gen_intervals(edge_list):
    bin_list = [(edge_list[i],edge_list[i+1]) for i in range(len(edge_list)-1)]
    return bin_list

def interval_df(bin_no,bin_list,label,city):
    df = pd.DataFrame()
    df['bin'] = bin_list
    df['bin_no'] = bin_no
    df['label'] = label
    df['city'] = city
    return df

def save_list(x,path):
    with open(path,'w') as csvFile:
        writer = csv.writer(csvFile)
        for val in x:
            writer.writerow([val])
    csvFile.close()
    
df = pd.DataFrame()
bin_size = float(0.25)
for f in file_list:
    data = pd.read_csv(path+f)
    print len(data), f
    if len(data)<20:
        continue
    len_lat_bins,len_lon_bins,lat_edge_list,lon_edge_list = bin_lat_lon(data,bin_size)
    city = data.city[0]
    bin_df = interval_df(range(len_lat_bins-1),gen_intervals(lat_edge_list),'lat',city)
    bin_df = bin_df.append(interval_df(range(len_lon_bins-1),gen_intervals(lon_edge_list),'lon',city))
    bin_df.to_csv('./city_data/bin_vals_'+city.replace(' ','_')+'.csv',index=False)
    combine_types(data)
    if len(df)==0:
        df = data
    else:
        df = df.append(data)

df.to_csv('./city_data/city_data.csv',index=False)
