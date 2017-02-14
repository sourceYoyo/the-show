#-*- coding: utf-8 -*-
from xml.etree import ElementTree
import re,os
import ..share
def get_element_text(element):
    if element is not None:
        return element.text
    else:
        print('the element is None!')

def getFromFile(filename):
    content = open(filename,'r',encoding='utf-8').read()
    content =re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+",u"",content)    
    root = ElementTree.fromstring(content)
    time = root.get('start-long')
    scan = root.find('scan-info')       
    post = scan.attrib
    post.update({'Information':0,'Medium':0,'Low':0,'High':0,'time':time,'title':post['target']+'扫描报告','author':'扫描器'})
    vuls = root.findall('vulnerability')           
    for vul in vuls:
        data = {}
        sec = vul.get('severity')       
        post[sec]=post[sec]+1
        data['level']=sec
        data['name']=vul.get('name')
        data['description']=vul.find('description').text
        http = vul.find('http-transactions').find('http-transaction').find('http-request')
        data['http']=ElementTree.tostring(http,encoding='utf-8',method='text')
        
        print(data)
        break
    print(post)
    
def savefromdir():
    dir = 'app/static/data/w3af'
    files = os.listdir(dir)
    for file in files:
        getFromFile(file)

#if __name__ ==  '__main__':
    #getFromFile(r'app/static/data/w3af/25_w3af.xml')
    #savefromdir()