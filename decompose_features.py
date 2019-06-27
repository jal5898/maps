#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 07:38:23 2019

@author: Joseph
"""

from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

def open_list(path):
    with open(path,'r') as csvFile:
        reader = csv.reader(csvFile)
        x = []
        for row in reader:
            x = x + row
    return x

def find_first(log_idx):
    idx = next(i for i in range(len(log_idx)) if log_idx[i])
    return idx

directory = './feature_data/'
feature_df = pd.read_csv(directory+'feature_data.csv')
type_list = open_list(directory+'type_list.csv')
kernel_list = open_list(directory+'kernel_list.csv')
cols = [i+'_'+j for i in type_list for j in kernel_list]

location_df = pd.read_csv('./city_data/city_data.csv')

pca = PCA()
pca.fit(feature_df[cols])
var_explained = pca.explained_variance_ratio_
pc_thresh = 0.999
n_pc = find_first(var_explained.cumsum()>pc_thresh)+1

target = ['books','hardware','cafe']

for t in target:
    target_df = location_df.loc[location_df.type==target[0]][['lat_bin_no','lon_bin_no','city']]
    lat_bin_no = target_df.lat_bin_no
    lon_bin_no = target_df.lon_bin_no
    city = target_df.city
    
    for i,j,c in zip(lat_bin_no,lon_bin_no,city):
        
        row = feature_df.loc[(feature_df.i==i)&(feature_df.j==j)&(feature_df.city==c)]
