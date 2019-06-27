#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 19:19:51 2019

@author: Joseph
"""

import pandas as pd
import numpy as np
from scipy import signal
import csv
import datetime

df = pd.read_csv('./city_data/city_data.csv')

nDims = 100
df.loc[df.type=='yes','type'] = 'other'
type_counts = df.groupby('type').size().sort_values(ascending=False)
top_types = type_counts[:nDims].index
top_types = list(top_types[top_types!='other'])
 
def flatten_data(data,n_feat,x,y):
    data = data.reshape([x,y,-1])
    data = np.swapaxes(data,2,0)
    data = data.reshape([n_feat,-1])
    data = np.swapaxes(data,1,0)
    return data

def save_list(x,path):
    with open(path,'w') as csvFile:
        writer = csv.writer(csvFile)
        for val in x:
            writer.writerow([val])
    csvFile.close()

def add_coords(data,n_x,n_y):
    x,y = zip(*[(i,j) for j in range(n_y) for i in range(n_x)])
    x = np.array(x).reshape([-1,1])
    y = np.array(y).reshape([-1,1])
    data = np.hstack((data,x,y))
    return data
        

kernel_size = [1,3,5,11,15,21]
min_biz_thresh = 0;
feature_df = pd.DataFrame
city_list = df['city'].unique()
type_list = top_types + ['other']
features = [t+'_'+str(k) for t in type_list for k in kernel_size]
n_features = len(features)

save_list(kernel_size,'./feature_data/kernel_list.csv')
for city in city_list:
    print city
    city_df = df.loc[df.city==city]
    lat_bins = list(city_df.max_lat_bin)[0]
    lon_bins = list(city_df.max_lon_bin)[0]
    array = np.zeros([lat_bins,lon_bins,nDims],dtype=np.uint16)
    for i in range(lat_bins):
        for j in range(lon_bins):
            bin_mask = (city_df.lat_bin_no==(i))&(city_df.lon_bin_no==(j))
            if not bin_mask.any():
                continue
            bin_counts = city_df[bin_mask].groupby('type').size()
            for t in bin_counts.index:
                try:
                    idx = top_types.index(t)
                except:
                    idx = nDims-1
                array[i,j,idx] = bin_counts[t]
    
    
    filter_array = np.zeros(list(array.shape)+[len(kernel_size)])
    for k in kernel_size:
        kernel = np.ones([k,k],dtype=np.uint16)
        for idx in range(nDims):
            filter_array[:,:,idx,kernel_size.index(k)] = signal.convolve2d(array[:,:,idx],kernel,mode='same')
    
# =============================================================================
#     row = []
#     for i in range(lat_bins):
#         for j in range(lon_bins):
#     for i in [44]:
#         for j in [45]:
#             d = {k:v for k,v in zip(features,filter_array[i,j,:,:].reshape([n_features]))}
#             row.append(d)
# =============================================================================
    
    data = flatten_data(filter_array,n_features,lat_bins,lon_bins)
    data = add_coords(data,lat_bins,lon_bins)
    cols = features+['i','j']
    temp_df = pd.DataFrame(data,columns=cols)
    temp_df['city'] = city
    temp_df = temp_df.loc[(temp_df[[t+'_1' for t in type_list]].T.sum()>min_biz_thresh)]
    try:
         feature_df = feature_df.append(temp_df,ignore_index=True)
    except:
         feature_df = temp_df

time = datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')
fileName = './feature_data/feature_data_'+time+'.csv'
feature_df.to_csv(fileName,index=False)
