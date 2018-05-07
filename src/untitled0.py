# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 15:20:22 2017

@author: rikhoekstra
"""
from unicodecsv import reader
from collections import Counter

basedir = '/Users/rikhoekstra/surfdrive/rsg/preslsts'

fls = [os.path.join(basedir, fl) for fl in os.listdir(basedir) if fl.find('.tiff.txt') > -1]
for f in fls:
    fl2plst(f)

fls = [os.path.join(basedir, fl) for fl in os.listdir(basedir) if fl.find('.tiff.txt.csv') > -1]

nms = []
for f in fls:
    flin = open(f)
    r = reader(f)
    n = [rw[0] for rw in r]
    nms.extend(n)

for k in c.keys():
    result = {}
    for i in common:
        r = e(i[0],k)
        result[r] = (k,i)
    x = min(result.keys())
    
