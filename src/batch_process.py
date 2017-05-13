# -*- coding: utf-8 -*-
"""
Created on Mon May  1 17:09:26 2017

@author: rikhoekstra
"""
import os
from unicodecsv import writer
from transitioning_rsg_parser import parse, make_date


def batch_process(basedir='', 
                  extension='4',
                  specific=75,
                  debug=False, 
                  logging=True):
                      

    if basedir == '':
        basedir = '/Users/rikhoekstra/Downloads/rsg/ocr/'
    else: 
        basedir = basedir
    if logging==True:
        import logging
        fn = os.path.join(basedir,'rsg.log')
        logging.basicConfig(filename=fn, filemode='w', level=logging.INFO)

        
    extension = extension

    dr = basedir+extension
    
    fls = [fl for fl in os.listdir(dr) if fl.find('html')]
    fls = [fl for fl in fls if fl.find('voorwerk') == -1]
    if debug == True:
        print debug
        fls = fls[:100]
    result = []
    
    if debug==True and specific:
        fl = open(os.path.join(dr, fls[specific]))
        print "processing %s" % fls[specific]
#        import pdb; pdb.set_trace()
        result.append(parse(fl))
    else:
        for fl in fls:
            fl = open(os.path.join(dr, fl))
            result.append(parse(fl))
#    return fl
    return result


def test(startdate='1 januari 1620', debug=True):
    d = make_date(startdate)[1]
    rows = []
    b = batch_process(basedir='/Users/rikhoekstra/Downloads/rsg/ocr/', extension='4', debug=debug, specific=None)  
    for i in  b:
        for s in i.sessions:
            if s.date:
                d = s.date
            try:
                date = d
            except AttributeError:
                date = "01-01-1620" 
            
            for r in s.resolutions.keys():
                res = s.resolutions[r]
                res.mknr()
                row = [date, res.nr, 
                res.get_resolution(sep=''), i.pagenr]
                rows.append(row)
    flout = '/Users/rikhoekstra/Downloads/rsg/ocr/vntest.csv'
    fout = open(flout, 'w')
    w = writer(fout)
    w.writerow(['date', 'resolutionnr', 'resolution', 'pagenr'])
    w.writerows(rows)
    fout.close()
    return b

if __name__ == '__main__':
    b = batch_process(basedir='/Users/rikhoekstra/Downloads/rsg/ocr/', 
                      extension='4', 
                      specific=75, 
                      debug=True)
