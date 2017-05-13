# -*- coding: utf-8 -*-
"""
Created on Thu May 11 08:44:55 2017

@author: rikhoekstra
"""
import os
import regex
import argparse

def convert(indir,
            rgp,
            deel,
            b,
            e
            ):
    #THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    THIS_DIR = indir
    SRC_FN = os.path.join(THIS_DIR,  'register.txt')
    pagerange = xrange(676, 768)
    nr = 208
    page = 0
    
    templ = "staten-generaalnr-7-gs{}_{:04d}.txt"
    
    fls = [os.path.join(indir, templ.format(rgp, fl)) for fl in pagerange]
    register = [open(fl).read() for fl in fls]
    register = '\n\n'.join(register)
    
    # placeholder so that we can remove single lineends
    hnr = regex.sub('\n\n', '##', register)
    # reduce all items to a single line
    hnr = regex.sub('\n', ' ', nnr) 
    #and put in the newlines again 
    hnr = regex.sub('##', '\n\n', hnr)
    
    
    #remove (badly recognized) hyphens
    r = register.decode("utf8")
    p = regex.compile('\u2014\n')
    r = regex.sub(p, r'\n', r)
    p = regex.compile('\xbb\n')
    r = regex.sub(p, r'\n', r)
    p = regex.compile('\u2014\n')
    r = regex.sub(p, '', r)
    
    return r


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--indir', help="in directory", required="True")
    ap.add_argument('-n', '--nr', help="rgp nummer", required="True")
    ap.add_argument('-d', '--deel', help="deel nummer", required="True")
    ap.add_argument('-b', '--begin', help="begin range of pages", required="True")
    ap.add_argument('-e', '--end', help="end range of pages", required="True")
    args = vars(ap.parse_args())
    
    nnr = convert(indir=args['indir'],
            rgp=args['nr'],
            deel=args['deel'],
            b=args['begin'],
            e=args['end'])
            
    flout = os.path.join(args['indir'], 'register.txt')
    w = open(flout,'w')
    w.write(nnr)
    w.close()
