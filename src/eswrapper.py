# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 16:48:32 2017

@author: rikhoekstra

inspirations:
https://qbox.io/blog/building-an-elasticsearch-index-with-python
"""
import json
from elasticsearch import Elasticsearch

#create default elasticsearch connection. 
#N.B. this works better than the mapping in the examples 

es = Elasticsearch()
    
def create_index(es, index, delete=True):
    INDEX_NAME=index
    if es.indices.exists(INDEX_NAME) and delete==True:
        print("deleting '%s' index..." % (INDEX_NAME))
        res = es.indices.delete(index = INDEX_NAME)
        print(" response: '%s'" % (res))
    # since we are running locally, use one shard and no replicas
    request_body = {
        "settings" : {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    print("creating '%s' index..." % (INDEX_NAME))
    res = es.indices.create(index = INDEX_NAME, body = request_body)
    print(" response: '%s'" % (res))


def bulkindexfrommapping(es=es, index='',type='',src=[]):
    """bulk index elasticsearch from mapping
    assuming ids are not unique"""
    create_index(es, index)
    bulk_data = []
    for item in enumerate(src):
        bulk_data.append({'index':{'_type':type, 
                                   '_index':index, 
                                   '_id':'%s' % item[0]}})
        bulk_data.append(item[1])
    es.bulk(index=index, body=bulk_data, refresh=True)


def bulk_resolutions(src=[]):
    """resolutions require some indirection"""
    create_index(es, index='resolutions')
    bluk_data = []
    for item in enumerate(src):
        bluk_data.append({'index':{'_type':'resolution', 
                                   '_index':'rsg.resolutions', 
                                   '_id': item[1] }})
        reso = src.get(item[1]).__dict__
        jeso = json.dumps(reso)
        bluk_data.append(jeso)
    es.bulk(index='reolutions', body=bluk_data, refresh=True)

def query(index, query):
    """wrapping up arcane elasticsearch results for program reuse
    Kicked out all es metadata for starts
    """
    result = es.search(index=index, body={"query": query})
    res = [hit['_source']  for hit in result['hits']['hits']]
    return res

def populate():
    eswrapper.bulk_resolutions(src=total.resolutions)
    deps = [d.__dict__ for d in parsed.deputies.values()]
    eswrapper.bulkindexfrommapping(index='deputies', type='person', src=deps)
    