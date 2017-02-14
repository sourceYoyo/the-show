import pymongo
import math
import re
import time


MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'thu-show'
MONGODB_COLLECTION_WIFIS = 'wifi'
MONGODB_COLLECTION_BUGS = 'bugs'
MONGODB_COLLECTION_POSTS = 'posts'
ROWS_PER_PAGE = 20
connection_string = "mongodb://%s:%d" % (MONGODB_SERVER, MONGODB_PORT)
content = {'by_bugs':
           {'mongodb_collection': MONGODB_COLLECTION_BUGS, 'template_html': 'search_bugs.html'},
           'by_posts':
           {'mongodb_collection': MONGODB_COLLECTION_POSTS, 'template_html': 'search_posts.html'},
           }

def searchPoints(args):    
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_WIFIS]
    points = collection.find(args).limit(100)
    results = []
    for point in points:
        result = []
        result.append(float(point['j'].encode('utf-8')))
        result.append(float(point['w'].encode('utf-8')))
        result.append('device name: '+point['name'].encode('utf-8'))
        result.append('ssid: '+point['device'].encode('utf-8'))
        result.append('location: '+point['location_source'].encode('utf-8')[:-2])
        result.append('mac: '+point['mac'].encode('utf-8'))
        if point['isSchoolwifi'] :
            result.append(1)
        else:
            result.append(0)
        results.append(result)
    return results

def saveWifi(points):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_WIFIS]
    for point in points:
        collection.save(point)    
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

def search_bug(id):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION_BUGS]
    return collection.find({'_id':id})

def search_mongodb(keywords, page, content_search_by, search_by_html):
    client = pymongo.MongoClient(connection_string)
    db = client[MONGODB_DB]
    keywords_regex = get_search_regex(keywords, search_by_html)
    collection = db[content[content_search_by]['mongodb_collection']]
    # get the total count and page:
    total_rows = collection.find(keywords_regex).count()
    total_page = int(
        math.ceil(total_rows / (ROWS_PER_PAGE * 1.0)))
    page_info = {'current': page, 'total': total_page,
                 'total_rows': total_rows, 'rows': []}
    # get the page rows
    if total_page > 0 and page <= total_page:
        row_start = (page - 1) * ROWS_PER_PAGE
        cursors = collection.find(keywords_regex)\
            .sort('datetime', pymongo.DESCENDING).skip(row_start).limit(ROWS_PER_PAGE)
        for c in cursors:
            c['datetime'] = c['datetime'].strftime('%Y-%m-%d')
            if 'url' in c:
                urlsep = c['url'].split('//')[1].split('/')
                c['url_local'] = '%s-%s.html' % (urlsep[1], urlsep[2])
            page_info['rows'].append(c)
    client.close()
    #
    return page_info

 