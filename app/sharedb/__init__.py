import pymongo
import math
import re
import time
from datetime import *
import calendar


MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'thu-show'
MONGODB_COLLECTION_WIFIS = 'wifi'
MONGODB_COLLECTION_FLOWS = 'flow'
MONGODB_COLLECTION_BUGS = 'report'
MONGODB_COLLECTION_POSTS = 'content'
MONGODB_COLLECTION_TOTAL = 'total'
MONGODB_COLLECTION_IVRE_ANAY = 'ivre_anay'
MONGODB_COLLECTION_IVRE_RESOLVE = 'ivre_resolve'
ROWS_PER_PAGE = 20
connection_string = "mongodb://%s:%d" % (MONGODB_SERVER, MONGODB_PORT)
content = {'by_bugs':
           {'mongodb_collection': MONGODB_COLLECTION_BUGS, 'template_html': 'search_bugs.html'},
           'by_posts':
           {'mongodb_collection': MONGODB_COLLECTION_POSTS, 'template_html': 'search_posts.html'},
           }


IVRE_DB='ivre'
IVRE_COLLECTIONS_HOSTS='hosts'

def save_anay_ivre(data):
    client = pymongo.MongoClient(connection_string)
    db = client[IVRE_DB]
    collection = db[MONGODB_COLLECTION_IVRE_ANAY]
    collection.save(data)

def save_revolve_dates(data):
    client = pymongo.MongoClient(connection_string)
    db = client[IVRE_DB]
    collection = db[MONGODB_COLLECTION_IVRE_RESOLVE]
    collection.update({'name':'resolve'},data,upsert=True)

def get_revolve_dates():
    client = pymongo.MongoClient(connection_string)
    db = client[IVRE_DB]
    collection = db[MONGODB_COLLECTION_IVRE_RESOLVE]
    return collection.find({'name':'resolve'})[0]


def get_anay_ivre():
    client = pymongo.MongoClient(connection_string)
    db = client[IVRE_DB]
    collection = db[MONGODB_COLLECTION_IVRE_ANAY]
    return collection.find()

def get_all_scans():
    client = pymongo.MongoClient(connection_string)
    db = client[IVRE_DB]
    collection = db[IVRE_COLLECTIONS_HOSTS]
    return collection.find()

def get_ivre_times():
    client = pymongo.MongoClient(connection_string)
    db = client[IVRE_DB]
    collection = db[IVRE_COLLECTIONS_HOSTS]
    return collection.distinct('source')

def get_ivre_bySource(source):
    client = pymongo.MongoClient(connection_string)
    db = client[IVRE_DB]
    collection = db[IVRE_COLLECTIONS_HOSTS]
    return collection.find({'source':source})

def get_IVRE_Num(source,port):
    client = pymongo.MongoClient(connection_string)
    db = client[IVRE_DB]
    collection = db[IVRE_COLLECTIONS_HOSTS]
    return collection.find({'source':source}).count()

def get_ivre_sourcecount(source):
    client = pymongo.MongoClient(connection_string)
    db = client[IVRE_DB]
    collection = db[IVRE_COLLECTIONS_HOSTS]
    return collection.find({'source':source}).count()


def minus_months(dt,months):
    month = dt.month - 1 - months
    if month==-1:
        month = 12
    year = dt.year - month / 12    
    day = min(dt.day,calendar.monthrange(year,month)[1])
    return dt.replace(year=year, month=month, day=day)

def deleteWifi():
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    now = datetime.utcnow()
    now = minus_months(now,1)
    collection = db[MONGODB_COLLECTION_WIFIS]
    collection.remove({"time" :  {"$lte": now}})

def updateReport(_id,target,description):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_BUGS]
    collection.update({"target":target},{"$set":{"description":description}})


def search_total(key):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_TOTAL]
    return collection.find({'key':key})

    
def smallPoints():
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_WIFIS]
    points = collection.find().limit(5000)
    points = unsame(points)
    results = []
    dangerService = ['WEP']
    for point in points:
        result = []
        result.append(float(point['j'].encode('utf-8')))
        result.append(float(point['w'].encode('utf-8')))
        result.append('device name: '+point['name'].encode('utf-8'))
        result.append('certificate service: '+point['device'].encode('utf-8'))
        result.append('mac: '+point['mac'].encode('utf-8'))
        if point['isSchoolwifi'] :
            result.append(1)
        else:
            dang = 0 
            for s in dangerService:
                if s in point['device']:
                    dang=-1
                    break
            result.append(dang)
        results.append(result)   
    client.close()
    return results

def searchPoints(args):    
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_WIFIS]
    points = collection.find(args)
    points = unsame(points)
    results = []
    dangerService = ['WEP']
    for point in points:
        result = []
        result.append(float(point['j'].encode('utf-8')))
        result.append(float(point['w'].encode('utf-8')))
        result.append('device name: '+point['name'].encode('utf-8'))
        result.append('certificate service: '+point['device'].encode('utf-8'))
        result.append('mac: '+point['mac'].encode('utf-8'))
        if point['isSchoolwifi'] :
            result.append(1)
        else:
            dang = 0 
            for s in dangerService:
                if s in point['device']:
                    dang=-1
                    break
            result.append(dang)
        results.append(result)   
    client.close()
    return results

def unsame(points):
    l = set()
    unsamePoints = []

    for data in points:
        if  not (data['j'],data['w']) in l:
            l.add((data['j'],data['w']))                        
            unsamePoints.append(data)
    return unsamePoints

def saveWifi(points):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_WIFIS]
    for point in points:        
        point['time'] = datetime.now()
        collection.update({'mac':point['mac'],'j':point['j'],'w':point['w']},point,upsert=True)
    client.close()

def toplows(args,num):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_FLOWS]        
    data = collection.find(args).sort('time',pymongo.DESCENDING).limit(num)
    return data



def saveReport(w3af):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_BUGS]        
    collection.save(w3af)
    client.close()

def saveTotal(total):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_TOTAL]        
    collection.update({'key':'total'},total,upsert=True)
    client.close()



def getTotalFlow():
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_TOTAL]        
    return collection.find({'key':'total'})[0]

def getFLowTime():
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_FLOWS]
    return collection.distinct('time')

def saveFlows(flows):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_FLOWS]
    for flow in flows:
        collection.save(flow)    
    client.close()

def get_total_count():
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection_bugs = db[MONGODB_COLLECTION_BUGS]
    total_count_bugs = collection_bugs.find().count()
    collection_drops = db[MONGODB_COLLECTION_POSTS]
    total_count_posts = collection_drops.find().count()
    client.close()
    return (total_count_bugs, total_count_posts)

def get_search_regex(keywords, search_by_html):
    keywords_regex = {}
    kws = [ks for ks in keywords.strip().split(' ') if ks != '']
    field_name = 'html' if search_by_html else 'title'
    if len(kws) > 0:
        reg_pattern = re.compile('|'.join(kws), re.IGNORECASE)
        # keywords_regex[field_name]={'$regex':'|'.join(kws)}
        keywords_regex[field_name] = reg_pattern

    return keywords_regex

def search_post(id):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_POSTS]
    return collection.find({'_id':id})

from bson.objectid import ObjectId
def search_report(target):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_BUGS]
    return collection.find({'target':target})

def query_report_num(q):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_BUGS]
    return collection.find(q).count()

def allreports():
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_BUGS]
    return collection.find().sort([('High',pymongo.DESCENDING),('sum',pymongo.DESCENDING),('Medium',pymongo.DESCENDING)])


def search_bug(id):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_BUGS]
    return collection.find({'_id':ObjectId(id)})



def search_mongodb_reports(keywords, page, content_search_by, search_by_html):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    keywords_regex = get_search_regex(keywords, search_by_html)
    collection = db[content[content_search_by]['mongodb_collection']]
    # get the total count and page:
    total_rows = collection.find(keywords_regex).count()
    total_page = int(
        math.ceil(total_rows / (ROWS_PER_PAGE * 1.0)))
    if total_page==0:
        total_page = 1
    page_info = {'current': page, 'total': total_page,
                 'total_rows': total_rows, 'rows': []}
    # get the page rows
    if total_page > 0 and page <= total_page:
        row_start = (page - 1) * ROWS_PER_PAGE
        cursors = collection.find(keywords_regex)\
            .sort([('high',pymongo.DESCENDING),('sum',pymongo.DESCENDING)]).skip(row_start).limit(ROWS_PER_PAGE)
        for c in cursors:            
            if 'url' in c:
                urlsep = c['url'].split('//')[1].split('/')
                c['url_local'] = '%s-%s.html' % (urlsep[1], urlsep[2])            
            page_info['rows'].append(c)
    client.close()
    #
    return page_info

def search_mongodb(keywords, page, content_search_by, search_by_html):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    keywords_regex = get_search_regex(keywords, search_by_html)
    collection = db[content[content_search_by]['mongodb_collection']]
    # get the total count and page:
    total_rows = collection.find(keywords_regex).count()
    total_page = int(
        math.ceil(total_rows / (ROWS_PER_PAGE * 1.0)))
    if total_page==0:
        total_page = 1
    page_info = {'current': page, 'total': total_page,
                 'total_rows': total_rows, 'rows': []}
    # get the page rows
    if total_page > 0 and page <= total_page:
        row_start = (page - 1) * ROWS_PER_PAGE
        cursors = collection.find(keywords_regex)\
            .sort('time', pymongo.DESCENDING).skip(row_start).limit(ROWS_PER_PAGE)
        for c in cursors:
            c['datetime'] = c['created']
            c['category'] = db['category'].find({'_id':ObjectId(c['category'])})[0]['slug']
            if 'url' in c:
                urlsep = c['url'].split('//')[1].split('/')
                c['url_local'] = '%s-%s.html' % (urlsep[1], urlsep[2])
            page_info['rows'].append(c)
    client.close()
    #
    return page_info

 


