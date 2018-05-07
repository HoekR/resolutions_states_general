# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 16:13:24 2015

@author: rik
"""
import os, fnmatch
import csv
from lxml import etree
from lxml.cssselect import CSSSelector
from collections import Counter
from datetime import date

def recursive_glob(treeroot, pattern):
  results = []
  for base, dirs, files in os.walk(treeroot):
    goodfiles = fnmatch.filter(files, pattern)
    results.extend(os.path.join(base, f) for f in goodfiles)
  return results


class Zittingsdag:
    """zittingsdag representation"""
    def __init__(self, fl, root):
        fn = os.path.basename(fl)
        sfn = os.path.splitext(fn)[0]
        self.root = root
        self.name = sfn
        self.date = self.datecode()
        self.path = fl
        try:
            self.presentielijst = self.setnm('presentielijst')
        except IndexError:
            self.presentielijst = None
        self.resoluties = []
#       self.oorkonder = self.setnm('oorkonder')
#       self.destinataris = self.setnm('destinataris')

    def datecode(self):
        try:
            dc = date(int(self.root.get('jaar')), int(self.root.get('maand')), int(self.root.get('dag')))
        except:
            dc= None
        return dc

    def setnm(self, nm):
        selector = CSSSelector(nm)
        n = selector(self.root)
        return n[0]


    def __repr__(self):
        return self.name

class Resolutie(object):
    def __init__(self, resolutie, zittingdag, position):
        self.zittingsdag = zittingsdag
        self.position = position
        self.text = resolutie

def ifl(fl, trans=False):
    """index an xmlfile"""
    doc = etree.parse(fl)
    root = doc.getroot()
    sfn = Zittingsdag(fl, root)
    selector =  CSSSelector('resolutie')
    resoluties = selector(root)
    for r in resoluties:
        resolutie = Resolutie(r, sfn, resoluties.index(r)+1)
        sfn.resoluties.append(resolutie)
    return (root, sfn)

    
