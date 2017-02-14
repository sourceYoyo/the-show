#-*- coding: utf-8 -*-
'''
     gpsspg api to translate gps xy
    oid=3711
    key=B64B380F0F3C336906ECA9281BF081BE

'''
import requests
import json
x1=116.321899
y1=39.998694
x2=116.343746
y2=40.018645
'''
def RealToBaidu(points):
    f = open('out.txt','r')        
    url_h = 'http://api.gpsspg.com/convert/coord/?oid=3711&key=B64B380F0F3C336906ECA9281BF081BE&from=0&to=2&latlng='
    url ='http://api.gpsspg.com/convert/coord/?oid=3711&key=B64B380F0F3C336906ECA9281BF081BE&from=0&to=2&latlng=' 
    url_end='&output=jsonp&callback=callback'
    appendURL=''   
    i = 0 
    for point in points:       
        appendURL=appendURL+point['w']+','+point['j']+';'
        i=i+1
        if i==10:
            i=0
            touchURL(url+appendURL+url_end)
            appendURL=''   
    touchURL(url+appendURL+url_end)
    return '''
def points2baidu(points): 
    url_h = 'http://api.gpsspg.com/convert/coord/?oid=3711&key=B64B380F0F3C336906ECA9281BF081BE&from=0&to=2&latlng='
    url ='http://api.gpsspg.com/convert/coord/?oid=3711&key=B64B380F0F3C336906ECA9281BF081BE&from=0&to=2&latlng=' 
    url_end='&output=jsonp&callback=callback'
    appendURL=''   
    for point in points:     

        appendURL=appendURL+point['w']+','+point['j']+';'
    return touchURL(url+appendURL+url_end,points)    

def loadFromFile(filename):
    map_file = open(filename,'rb')
    points = map_file.readlines()
    return points    

def checkSchool(name):
    names = ['Tsinghua-5G','DIVI','IVI','Tsinghua','DIVI-2']
    if name in names:
        return True
    else:
        return False

def inXimen(point):
    if float(point['j'])<116.32172:
        return True
    if float(point['j'])<116.326458 and float(point['w'])<40.010384 and float(point['w'])>40.007556:
        return True
    return False

def getAllBaidu(points):
    unsamePoints = unsame(points)
    pointMap = {}
    notBaidu = []
    for point in unsamePoints:
        if len(point['j'])>15 or inXimen(point):
            notBaidu.append(point)
            if len(notBaidu)==10:
                pointMap.update(points2baidu(notBaidu))
                notBaidu=[]
    if len(notBaidu) >0:
        pointMap.update(points2baidu(notBaidu))
    baiduPoints = []
    for point in points:
        if len(point['j'])>15 or inXimen(point):
            toP = pointMap[point['j']+point['w']]
            point['j'] = toP['lng']
            point['w'] = toP['lat']
        baiduPoints.append(point)

    return baiduPoints

def touchURL(url, points):
    result = requests.get(url).text            
    result = result[19:-1]
    print(result)
    jsonObj = json.loads(result)    
    newpoints = jsonObj['result']
    trans = {}
    for (p , to_p) in zip(points,newpoints):
        trans[p['j']+p['w']]=to_p
    return trans


def getPoints(bit_points,location_source='all'):
    l = []
    for point in bit_points:
        point = point.decode('utf-8')
        data = point.split(',')
        if location_source=='all' or data[5].startswith(location_source):
            ma = len(data)
            map_point={'mac':data[0],'name':data[1],'device':data[2],'w':data[ma-2],'j':data[ma-1][:-1],'isSchoolwifi':checkSchool(data[1])}             
            l.append(map_point)
    return l
    


   

def inTsinghua(points):
    ls = []
    notin = []
    for p in points:
        if float(p['j'])<x1 or float(p['w'])<y1:
            notin.append(p)
            continue
        if float(p['j'])>x2 or float(p['w'])>y2:
            notin.append(p)
            continue
        ls.append(p)
    return ls,notin

def unsameHtmlInfo(points):
    l = set()
    unsamePoints = []
    for data in points:
        if  not (data['j'],data['w']) in l:
            l.add((data['j'],data['w']))
            #p = 'new BMap.Point('+data['j'] +','+data['w'] +'),'+'\n'
            p = '['+data['j'][:-1] +','+data['w']+',"Wifi名:'+data['name']+'",'+'"设备名:'+data['device']+'",'+'"Mac地址:'+data['mac']+'"],'+'\n'
            unsamePoints.append(p)
    return unsamePoints
        

def translateData(points):
    l = []
    for point in points:            
        point = point.decode('utf-8')
        data = point.split(',')
        if(len(data)>6):
            assert('informal data')        
        p = 'new BMap.Point('+data[4] +','+data[3] +'),'+'\n'
    print(len(l))
    return l

def saveFile(points,filename):
    f = open(filename,'w',encoding='utf-8')
    for point in points:
        f.write(point['mac']+','+point['name']+','+point['device']+','+point['w']+','+point['j']+'\n')
    f.close()

def saveJsonTranslate():
    search = {}
    f=open('real_toBaidu.txt','r')
    f_baidu=open('out.txt','r',encoding='utf-8')
    lines = f_baidu.readlines()    
    jsonObj = json.load(f)
    bit_points= loadFromFile('wifi_infos.txt')    
    mapPoints = getPoints(bit_points)
    i=0
    for data in jsonObj:
        points = data['result']
        for point in points:                
            search[lines[i][:-1]] = point 
            i = i+1 
    for mapPoint in mapPoints:
        try:
            to_translate = search[mapPoint['j']+','+mapPoint['w']]
            mapPoint['j']=to_translate['lng']
            mapPoint['w']=to_translate['lat']  
        except:
            print()
    saveFile(mapPoints,'all_baidu.txt')
        
        
def removeUnUTF8():
    filenames = ['info_1010_building6.txt','info_1010_fit.txt','info_1011_building3.txt']
    points = loadFromFile('all_baidu_bb3.txt')
    mapPoints = getPoints(points)
    for filename in filenames:
        f = open(filename,'r',encoding='utf-8')
        lines = f.readlines()
        for line in lines:
            data = line.split(',')
            for point in mapPoints:
                if data[0]==point['mac']:
                    point['name']=data[1]
                    break
    saveFile(mapPoints,'all-baidu.txt')
        


def unsame(points):
    l = set()
    unsamePoints = []

    for data in points:
        if  not (data['j'],data['w']) in l:
            l.add((data['j'],data['w']))                        
            unsamePoints.append(data)
    return unsamePoints
#removeUnUTF8()

'''
if __name__ == '__main__':
    bit_points= loadFromFile('wifi_infos.txt')
    mapPoints = getPoints(bit_points)
    getAllBaidu(mapPoints)    
    l = unsameHtmlInfo(mapPoints)
    out = open('html_data.txt','w',encoding='utf-8')
    out.writelines(l)
'''
    
    

'''
if __name__ == "__main__":
    bit_points= loadFromFile('wifi_infos.txt')
    mapPoints = getPoints(bit_points)
    unsamePs = unsame(mapPoints)
    
    tsps,notin = inTsinghua(unsamePs)
    #RealToBaidu(notin)
    l = unsameHtmlInfo(notin)
    out = open('out.txt','w',encoding='utf-8')
    out.writelines(l)

    
'''
'''
if __name__ == "__main__":
    bit_points= loadFromFile('all_baidu.txt')
    mapPoints = getPoints(bit_points)
    l = getHtmlInfo(mapPoints)
    out = open('html_data.txt','w',encoding='utf-8')
    out.writelines(l)'''
