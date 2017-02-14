#-*- coding: utf-8 -*-
from flask import *
from flask.ext.login import login_required


from ..sharedb import *
import re,os
from xml.etree import ElementTree
import time,datetime,calendar
import json



data_blue = Blueprint('data', __name__, url_prefix='/data')



'''
[['XSS',   45.0],['file_upload',       26.8],['others',   0.7]]'''


often_used_ports = [21,80,443,22]
port_dict = dict((str(port),0) for port in often_used_ports)

def ivreAnayBySource(any_source):
    sources = get_ivre_times()
    sources = sorted(sources, key=lambda d:d[1], reverse = True)
    sort_sources = sorted(sources, key=lambda d:d[1], reverse = True)  
    sort_sources.sort()  
    end = sort_sources.index(any_source)
    all_len = min(4,end)
    check_sources = sort_sources[end-all_len:end]
    hosts = get_all_scans()
    result = {}
    for host in hosts:
        addr = str(host["addr"])
        source = host['source']
        openports = host['openports']
        if (not source in check_sources) or (openports['count']<=0):
            continue
        else:
            ports = openports['tcp']['ports']
            for port in ports:
                if port in often_used_ports:
                    if not addr in result:
                        result[addr] = dict((str(port),0) for port in often_used_ports)                        
                    result[addr][str(port)] += 1   
    # 统计每次的稳定端口数
    total = dict((str(port),0) for port in often_used_ports)
    for data in result:        
        for port in result[data]:
            if result[data][str(port)]>=all_len-1:
                total[str(port)]+=1
                            
    save_anay_ivre({'source':any_source,'data':result,'total':total})


@data_blue.route("/recordIvre", methods=["GET","POST"])
@login_required
def testAnay():
    sources = get_ivre_times()
    sources = sorted(sources, key=lambda d:d[1], reverse = True)
    sort_sources = sorted(sources, key=lambda d:d[1], reverse = True)
    sort_sources.sort()
    cal_revolve_dates()
    for source in sort_sources:
        ivreAnayBySource(source)
    return 'ok'


def ivreAnay():
    sources = get_ivre_times()
    sources = sorted(sources, key=lambda d:d[1], reverse = True)
    sort_sources = sorted(sources, key=lambda d:d[1], reverse = True)
    ivreAnayBySource(sort_sources[-1])
    cal_revolve_dates()
    


                

def getAnay():


    port_stable_data=stable_data()    
    port_revolve_dates = revolve_dates()
    port_newest_data = getLatestResolve(port_revolve_dates)

    return port_revolve_dates,port_stable_data,port_newest_data



def cal_revolve_dates():
    sources = get_ivre_times()
    sources = sorted(sources, key=lambda d:d[1], reverse = True)
    sources.sort()
    sources_dict = dict((source,0) for source in sources)
    port_sources_count={}

    for port in often_used_ports:
        port_sources_count[str(port)]=dict((source,0) for source in sources)
    port_sources_count['all-hosts']=dict((source,0) for source in sources)
    hosts = get_all_scans()
    for host in hosts:
        source = host['source']
        openports = host['openports']
        port_sources_count['all-hosts'][source]+=1
        if openports['count'] >0 :
            ports = openports['tcp']['ports']            
            for port in ports:
                if not port in often_used_ports:
                    continue
                #    port_sources_count[str(port)]=sources_dict 
                port_sources_count[str(port)][source] += 1
    
    
    titles = list(source.encode('utf-8') for source in sources)
    data = []
    for port_source in port_sources_count:
        data.append({'name':port_source,'data':list(port_sources_count[port_source][source] for source in sources )})   

    save_revolve_dates({'name':'resolve','titles':titles,'data':data} )
    
def getLatestResolve(resolved_data):
    titles = []
    content = [] 
    stable = []
    temp_ser = {}

    
    sources = get_ivre_times()
    sources = sorted(sources, key=lambda d:d[1], reverse = True)
    sources.sort()
    latest_source = sources[-1]
    anay_data = get_anay_ivre()    
    for anay in anay_data:
        if anay['source']  == latest_source:
            total = anay['total']      
            for port in total:
                temp_ser[port.encode('utf-8')]=total[port]
    
    for data in resolved_data['data']:
        if data['name']=='all-hosts':
            continue
        titles.append(data['name'])
        stable.append(data['data'][-1])
        content.append(temp_ser[data['name']])
    
    return  {
        'titles':titles,
        'data':[
            {'name':'stable-hosts','data':content},
            {'name':'newest-hosts','data':stable}
            ] 
        }
    

        

def revolve_dates():
    data = get_revolve_dates()
    titles = list( title.encode('utf-8') for title in data['titles'])
    content = []
    for unit in data['data']:
        b = dict( (ti.encode('utf-8'),unit[ti]) for ti in unit)
        b['name']= b['name'].encode('utf-8')
        content.append(b)
    return {'titles':titles,'data':content}

def stable_data():
    port_stable_data_cat = []    
    port_stable_data_ser = []
    temp_ser = dict((str(port),[]) for port in often_used_ports)
    anay_data = get_anay_ivre()    
    for anay in anay_data:
	if anay['source'] in port_stable_data_cat:
	    continue
        port_stable_data_cat.append(anay['source'])  
        total = anay['total']      
        for port in total:
            temp_ser[port.encode('utf-8')].append(total[port])
    for port in temp_ser:
        port_stable_data_ser.append({'name':'tcp/'+str(port),'data':temp_ser[port]})
    return {'categories':list(con.encode('utf-8') for con in port_stable_data_cat),'series':port_stable_data_ser}



def report_index():
    
    web_series = [{'name':'High','data':[]},{'name':'Medium','data':[]},{'name':'Low','data':[]},{'name':'Information','data':[]}]
    web_titles = []
    data = {}
    reports = allreports()
    web_category = reports[:10]
    for web in web_category:
        tr = web['target'].decode('utf-8').encode('utf-8')
        web_titles.append('<a href="%s">%s</a>'%(tr,tr))
        web_series[0]['data'].append(web['High'])
        web_series[1]['data'].append(web['Medium'])
        web_series[2]['data'].append(web['Low'])
        web_series[3]['data'].append(web['Information'])
    
    reports = allreports()
    for report in reports:
        vuls = report['vuls']
        for vul in vuls:            
            name = vul['name'].decode('utf-8').encode('utf-8')
            if name in data:
                data[name]=data[name]+1
            else:
                data[name]=1
    vuls = sorted(data.iteritems(), key=lambda d:d[1], reverse = True)
    others = 0
    result = []
    for x,y in vuls[15:]:
        others = others+y
    result.append(['others',others])

    for x,y in vuls[:15]:
        result.append([x,y])
    return web_titles,web_series,result                


        

def getBasicFlows():
    total = getTotalFlow()
    data = []
    for key,value in total.items():
        if not '_id' in key:
            data.append({'name':key,'data':value})
    return data

def readDangerFile(name):
    path = '/home/ubuntu/fileupload/'+name
    f = open(path,'r')
    data = f.readlines()
    l = len(data)
    reslt = []
    for i in range(l):
        name = data[i].split(' ')[0]
        reslt.append({'name':name})
    return reslt

def readDangerDetailFile(name):
    try:
        path = '/home/ubuntu/fileupload/'+name
        f = open(path,'r')
        data = f.readlines()
        l = len(data)
        reslt = []
        for i in range(l):
            sp = data[i].split(' ')
            title = sp[0]
            if name == 'top_domain.txt' or name == 'mal_domain.txt':
                reslt.append({'name':title,'id':sp[1][:-1]})
            else:
                reslt.append({'name':title,'ip':sp[1],'date':sp[2][:-1]})
        return reslt
    except Exception,e:
        return []


def getWebs():
    #hots = [{'name':'www.baidu.com','id':1},{'name':'weibo.com','id':2},{'name':'zhihu.com','id':3},{'name':'aiqiyi.com','id':4},{'name':'nba.hupu.com','id':5},{'name':'dota2.com','id':6},{'name':'sougou.com','id':7}]
    danger_hots  = readDangerDetailFile('mal_domain.txt')[:100]
    hots  = readDangerDetailFile('top_domain.txt')[:100]
    dangers_in  = readDangerDetailFile('domain_in.txt')[:100]
    dangers_out = readDangerDetailFile('domain_out.txt')[:100]
    #dangers_out  = [{'name':'law.tsinghua.edu.cn/','id':1},{'name':'cxkdh.lib.tsinghua.edu.cn/','id':2}]
    return hots,danger_hots,dangers_in,dangers_out
    
def getFlows():     
             
    categories = getFLowTime()
    titles = ['DNS','UDP','SSL']    
    app_data = dict((ti,[])for ti in titles)
    protocal_data = dict((ti,[])for ti in titles)

    for name in titles:
        top = toplows({'category':'app','name':name},11)
        b=None
        for t in top:
            if b != None:                 
                app_data[name].append([calendar.timegm(t['time'].utctimetuple())*1000,max(0,float(t['content'])-float(b['content']))])
            b = t
        top = toplows({'category':'protocal','name':name},11)
        b = None
        for t in top:
            if b != None:                 
                protocal_data[name].append([calendar.timegm(t['time'].utctimetuple())*1000,max(0,float(t['content']-float(b['content'])))])
            b=t
    app_series = list({'name':flow,'data':app_data[flow]} for flow in app_data)
    protocal_series = list({'name':flow,'data':protocal_data[flow]} for flow in app_data)
    return app_series,protocal_series

@data_blue.route("/recordW3af", methods=["GET","POST"])
@login_required
def recordW3af():
    savefromdir('w3af')
    savefromdir('w3af_new')
    return 'ok'
    
@data_blue.route("/recordFlows", methods=["GET","POST"])
@login_required
def touchRecordFlows():
    return recordFlows()

def recordFlows():
    flowdir = '/home/ubuntu/fileupload/globalinfor'
    files = os.listdir(flowdir)
    nowtime = datetime.datetime.utcnow()
    flows = {}
    for file in files:
        flows = combineFlows(saveFlowFile(file,nowtime),flows)    
    
    data = list(flows[flow] for flow in flows)
    saveFlows(data)

    return 'ok'

def combineFlows(flows1,flows2):
    flows = flows2
    for flow in flows1:
        if flow in flows:
            flows[flow]['content']+=flows1[flow]['content']
        else:
            flows[flow]=flows1[flow] 
    return flows


def saveFlowFile(name,nowtime):
    content = open('/home/ubuntu/fileupload/globalinfor/%s'%(name),'rb').read()
    content = content.decode("gb2312").encode('utf-8')    
    content = content.replace('gb2312', 'utf-8')
    root = ElementTree.fromstring(content)
    total = {}
    total['StartTime']=root.find('StartTime').text
    total['EndTime']=root.find('EndTime').text
    total['NewConnectNum']=root.find('NewConnectNum').text
    total['DeleteConnectNum']=root.find('DeleteConnectNum').text
    total['TotalPacketBytes']=root.find('TotalPacketBytes').text
    total['TotalPacketNum']=root.find('TotalPacketNum').text
    total['key']='total'
    saveTotal(total)
    
    app_nodes = root.getchildren()
    flows = {}
    for child in app_nodes:
        if  child.tag.startswith('APP'):
            category = 'app'
        elif child.tag.startswith('Protocol'):
            category = 'protocal'      
        else:
            continue 
        name = child.findtext('Name')
        if name!=None and not name.startswith('Unknown'):
            percent = child.findtext('Percent')
            times = child.findtext('Times')
            content = long(child.findtext('Bytes'))
            flows[name+'_'+category]={'name':name,'category':category,'percent':percent,'times':times,'content':content,'time':nowtime}
    return flows



def getFromFile(filename,category):
    content = open(filename,'r').read()
    content =re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+",u"",content)    
    root = ElementTree.fromstring(content)
    time = root.get('start-long')
    scan = root.find('scan-info')       
    post = scan.attrib
    post.update({'Information':0,'Medium':0,'Low':0,'High':0,'time':time,'title':post['target']+'扫描报告','author':'扫描器'})    
    vuls = root.findall('vulnerability')   
    vul_list = []        
    for vul in vuls:
        data = {}
        sec = vul.get('severity')       
        post[sec]=post[sec]+1
        data['level']=sec
        data['name']=vul.get('name')
        data['description']=vul.find('description').text
        try:
            http = vul.find('http-transactions').find('http-transaction').find('http-request')
            data['http']=ElementTree.tostring(http)
        except:
            data['http']=None
        vul_list.append(data)
    post['vuls']=vul_list
    post['sum']=len(vul_list)
    post['category']=category
    post['description']=''
    return post

def plusReport(data,report,cat):
    if report['sum'] == 0:
        return
    li = ['Low','Medium','High','Information']
    for s in li:
        data[s][cat] += report[s]
    data['all_vuls'][cat] += report['sum']
    data['all_web'][cat] +=1


def getWa3fCompare():
    data = {}
    old_total = query_report_num({'category':'w3af'})
    new_total = query_report_num({'category':'w3af_new'})
    #data['all_web']={'old':old_total,'new':new_total}    
    data['all_web']={'old':0.0,'new':0.0}
    data['all_vuls']={'old':0,'new':0}
    data['Low']={'old':0,'new':0}
    data['High']={'old':0,'new':0}
    data['Medium']={'old':0,'new':0}
    data['Information']={'old':0,'new':0}
    reports = allreports()
    for report in reports:
        if report['category'] == 'w3af':
            plusReport(data,report,'old')
        else:
            plusReport(data,report,'new')
    result = []
    ti = ['all_vuls','High','Medium','Low','Information']
    old_l = ['h','old']
    new_l = ['h','new']
    for t in ti:
        old_l.append(data[t]['old']/data['all_web']['old'])
        new_l.append(data[t]['new']/data['all_web']['new'])    
    
    result.append(old_l)
    result.append(new_l)
    return result
    
def savefromdir(dirname):
    dir = 'app/static/data/'+dirname
    files = os.listdir(dir)  
    for file in files:
        try:
            saveReport(getFromFile(dir+'/'+file,category=dirname))
        except:
            print 'save error'+file


