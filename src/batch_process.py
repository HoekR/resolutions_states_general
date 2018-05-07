# -*- coding: utf-8 -*-
"""
Created on Mon May  1 17:09:26 2017

@author: rikhoekstra
"""
import os
import re
from csv import writer
from transitioning_rsg_parser import parse, make_date
p1 = re.compile("(((?P<roman>\w*[A-Za-z]))*\s*((?P<rnr>\d{1,4}\s*\.+)))(?P<resolutie>.*)", re.UNICODE)
p2 = re.compile(r'(?P<rnr>\d{1,4}\s*\.?)(?P<resolutie>.*)', re.UNICODE) 

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

    dr = os.path.join(basedir, '%s' % extension, 'ocr')
    
    fls = [fl for fl in os.listdir(dr) if fl.find('html')]
    fls = [fl for fl in fls if fl.find('voorwerk') == -1]
    fls.sort()
    if debug == True:
        print ('debug:',  debug)
        fls = fls[:25]
    result = []
    
    if debug==True and specific:
        fl = open(os.path.join(dr, fls[specific]))
        print ("processing %s" % fls[specific])
        result.append(parse(fl))
    else:
        for fn in fls:
            fl = open(os.path.join(dr, fn), encoding='latin1')
            try:
                result.append(parse(fl))
            except UnicodeDecodeError:
                print ("skipping %s because of UNICODE ERRORS!!!" % fn )
#    return fl
    return result


def test(start_date='1 januari 1620', 
         basedir='/Users/rikhoekstra/surfdrive/rsg/ocr/', 
         vol=1, 
         debug=True):
    """als debug waar is dan parst het programma maar 100 pags"""
    import logging
    basedir = basedir
    fn = os.path.join(basedir,'rsgdiag.log')
    logging.basicConfig(filename=fn, filemode='w', level=logging.INFO)
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler(fn)
    handler.setLevel(logging.INFO)
    
    d = make_date(start_date)[1]
    rows = []
    
    
    b = batch_process(basedir=basedir, 
                      extension=vol, 
                      debug=debug, 
                      specific=None,
                      logging=True)  
    for i in  b:
        for s in i.sessions:
            if s.date:
                d = s.date
            try:
                date = date = "{:%Y-%m-%d}".format(d)
            except (AttributeError, ValueError, TypeError):
                date = start_date
            logger.info(s.resolutions.keys())
            for r in s.resolutions.keys():
                res = s.resolutions[r]
                if vol == 1:
                    pat = p1
                else:
                    pat == p2
                res.mknr(pat)
                if res.nr != '0':
                    row = [date, res.nr, 
                    res.get_resolution(sep=' '), i.pagenr, res.roman]
                    rows.append(row)
#                    print(res)
    flout = os.path.join(basedir, '%soutput.csv' % vol)
    fout = open(flout, 'w')
    w = writer(fout, delimiter='\t')
    w.writerow(['date', 'resolutionnr', 'resolution', 'pagenr', 'roman'])
    w.writerows(rows)
    fout.close()
    print ("file written to: %s" % flout)

if __name__ == '__main__':
    test(start_date='1 januari 1620', basedir='/Users/rikhoekstra/surfdrive/rsg/ocr', vol=1, debug=True)

