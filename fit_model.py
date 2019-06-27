#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 07:38:23 2019

@author: Joseph
"""

from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from os import listdir
import re
import pickle

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

def get_latest_data(path):
    fileList = listdir(path)
    date_list = [re.split('feature_data_|\.csv',f)[1] for f in fileList if 'feature_data' in f]
    latest = sorted(date_list)[-1]
    fileName = 'feature_data_'+latest+'.csv'
    return fileName

def pickle_model(obj,path):
    with open(path,'w') as pickleFile:
        pickle.dump(obj,pickleFile)
    pickleFile.close()

directory = './feature_data/'
fileName = get_latest_data(directory)
feature_df = pd.read_csv(directory+fileName)
type_list = open_list(directory+'type_list.csv')
kernel_list = open_list(directory+'kernel_list.csv')
cols = [i+'_'+j for i in type_list for j in kernel_list]

location_df = pd.read_csv('./city_data/city_data.csv')

# =============================================================================
# pca = PCA()
# pca.fit(feature_df[cols])
# var_explained = pca.explained_variance_ratio_
# pc_thresh = 0.999
# n_pc = find_first(var_explained.cumsum()>pc_thresh)+1
# =============================================================================

target = ['books']
test_city = 'New Haven Connecticut'
for t in target:
    target_df = location_df.loc[location_df.type==t][['lat_bin_no','lon_bin_no','city']]
    lat_bin_no = target_df.lat_bin_no
    lon_bin_no = target_df.lon_bin_no
    city = target_df.city
    
    temp_df = pd.DataFrame()
    for i,j,c in zip(lat_bin_no,lon_bin_no,city):
        row = feature_df.loc[(feature_df.i==i)&(feature_df.j==j)&(feature_df.city==c)]
        temp_df = temp_df.append(row)
    t_cols = [c for c in temp_df.columns if t in c]
    temp_df[t_cols] = temp_df[t_cols]-1
    temp_df['target'] = 1
    feature_df['target'] = 0
    test_data = feature_df.loc[feature_df.city==test_city]
    train_data = feature_df.loc[feature_df.city!=test_city]
    
    train_data = train_data.sample(n=10000,random_state=1).append(temp_df)
    print 'Training Model...'
    logreg = LogisticRegression()

    logreg.fit(train_data[cols], train_data['target'])
    p = logreg.predict_proba(test_data[cols])
    max_lat = int(max(test_data.i))
    max_lon = int(max(test_data.j))
    output = np.zeros([max_lat+1,max_lon+1])
    lat_lon = zip(test_data.i,test_data.j)
    for i in range(len(lat_lon)):
        output[int(lat_lon[i][0]),int(lat_lon[i][1])] = p[i][1]
    plt.imshow(output)
    pickle_model(logreg,'./model/'+t+'_model.txt')
    
    