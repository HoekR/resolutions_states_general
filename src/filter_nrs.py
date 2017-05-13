# -*- coding: utf-8 -*-
"""
Created on Mon May  8 17:16:39 2017

@author: rikhoekstra
"""

infl = open('/Users/rikhoekstra/Downloads/rsg/ocr/vntest.csv')
from csv import DictReader, DictWriter
r = DictReader(infl)
fieldnames = r.fieldnames

flout = open('/Users/rikhoekstra/Downloads/rsg/ocr/filteredtest.csv', 'w')
w = DictWriter(flout, fieldnames=fieldnames)
w.writeheader()
out = []
oldnr = 0
for row in r:
    nr = row['resolutionnr']
    if nr not in ['0', 0]:
        out.append(row)
  

w.writerows(out)
flout.close()
