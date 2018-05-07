# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 09:57:49 2017

@author: rikhoekstra
"""
import os
import re
import requests
import cv2
import imutils
from collections import Counter
from unicodecsv import writer

def batch_plist(basedir='', 
                  extension='4',
                  specific=75, 
                  logging=True):
                      

    if basedir == '':
        basedir = '/Users/rikhoekstra/Downloads/rsg/ocr/'
    else: 
        basedir = basedir
    if logging==True:
        import logging
        fn = os.path.join(basedir,'plst.log')
        logging.basicConfig(filename=fn, filemode='w', level=logging.INFO)

        
    extension = extension

    dr = os.path.join(basedir, '%s' % extension, 'ocr')
    
    fls = [fl for fl in os.listdir(dr) if fl.find('html') > -1]
    fls = [fl for fl in fls if fl.find('voorwerk') == -1]
    result = []
    for fl in fls:
        fin = open(os.path.join(dr, fl))
        txt = fin.read()
        if Counter(txt)['X'] > 25:
            result.append(fl)
#    return fl
    return result

def get_img_from_url(flname, baseurl='', extension='5'):
    fn = os.path.splitext(flname)[0] + '.tiff'
    if not baseurl:
        baseurl = "http://resources.huygens.knaw.nl/retroapp/service_statengeneraal"
    url = os.path.join(baseurl, extension, 'images', fn)
    img = requests.get(url)
    basedir = '/Users/rikhoekstra/surfdrive/rsg/preslsts'
    out = os.path.join(basedir, fn)
    outfl = open(out, 'wb')
    outfl.write(img.content)
    outfl.close()
    print('written: ', out)

def rotate(image):
    im = cv2.imread(fl)
    if im != None:
       h, w = im.shape[:2]
       if h>w:
           rotated = imutils.rotate_bound(im, 90) 
       flout = os.path.splitext(fl)[0] + 'b.tiff'
       cv2.imwrite(flout, rotated)

def fl2plst(fl):
    out = []
    patdatum = re.compile('Presentes(.*)(\d{4})')
    pat = re.compile(' \d+')
    pat1 = re.compile('[-_\W]')
    flin = open(fl)
    lns = flin.readlines()
    flin.close()
    lns = [l.strip() for l in lns]
    lns = [re.sub('[\)\>]<', 'X', l) for l in lns]
    lns = [l.replace('*', '-') for l in lns]
    lns = [l.replace('\xe2\x80\x9a', '-') for l in lns]
    lns = [l.replace('\xe2\x80\xa6', '') for l in lns]
    lns = [l.replace('\xe2\x80\x94', '-') for l in lns]
    lns = [l.replace('_', '-') for l in lns]
    for l in lns:
        if pat.findall(l) > 10:
            x = patdatum.search(l)
            if x != None:
                lns.remove(l)
                l = l[x.end():]
                out.append([' '. join(x.groups())])
            fieldnames = l.split(' ')
            fieldnames.insert(0, 'name')
            out.append(fieldnames)
            try: 
                lns.remove(l)
            except ValueError:
                pass
            break
    for l in lns:
        splitted = l.split(' ') 
#        if len(splitted) >= ijk:
        nm = splitted[0]
        nm = pat1.sub('', nm)
        splitted[0] = nm
        result = []
        result.extend(splitted)
        out.append(result)
    flout = open(fl + '.csv', 'wb')
    try:
        w = writer(flout)
#        w.writeheader()
        w.writerows(out)
        flout.close()
    except UnboundLocalError:
        print 'no dates: ', fl

    