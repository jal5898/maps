#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 21:10:10 2019

@author: Joseph
"""

import cPickle
import gzip

def pickle_zippler(obj,filename,protocol=-1):
    with gzip.open(filename,'wb') as f:
        cPickle.dump(obj,f,protocol)
        
def pickle_unzippler(filename):
    with gzip.open(filename,'rb') as f:
        loaded_obj = cPickle.load(f)
        return loaded_obj

def pickle_save(obj,filename):
    with open(filename,'w') as pickleFile:
        cPickle.dump(obj,pickleFile)

def pickle_load(filename):
    with open(filename,'r') as pickleFile:
        obj = cPickle.load(pickleFile)
    return obj