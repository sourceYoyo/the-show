#-*- coding: utf-8 -*-
from flask import Blueprint, render_template,request
import pymongo
from ..sharedb import *
import wifi
from werkzeug import secure_filename
from flask.ext.login import login_required, current_user
import re


wifi_blue = Blueprint('wifi', __name__, url_prefix='/wifimap')


def getSmallWifi():
    points=smallPoints()
    center=[116.33648784,40.00858704]
    if len(points)>0:
        center = [points[0][0],points[0][1]]
    isAdmin = False
    if current_user.group == 'administrator':
        isAdmin = True
    return render_template('/wifi.html',isAdmin=isAdmin,map_points=points,center_point=center)


@wifi_blue.route('/')
@login_required
def getmap():    
    name=request.args.get('name')
    ssid=request.args.get('ssid')
    mac=request.args.get('mac')    
    wifi_filter=request.args.get('filter')   
    twice = request.args.get('twice')
    if twice==None :
        return getSmallWifi()
    args = {}
    if wifi_filter!=None and wifi_filter==0:
        args['isSchoolwifi']=True
    elif wifi_filter!=None and wifi_filter==1:
        args['isSchoolwifi']=False
        
    if name!=None and name !='':        
        args['name']=name#re.compile('|'.join(name), re.IGNORECASE)
    else:
        name = ''
    if ssid!=None and ssid !='':
        args['ssid']=ssid#re.compile('|'.join(ssid), re.IGNORECASE)
    else:
        ssid = ''
    if mac!=None and mac !='':
        args['mac']=mac
    else:
        mac = ''
    points=searchPoints(args)
    center=[116.33648784,40.00858704]
    if len(points)>0:
        center = [points[0][0],points[0][1]]
    isAdmin = False
    if current_user.group == 'administrator':
        isAdmin = True
    return render_template('/wifi.html',map_points=points,center_point=center,wifi_wifiname=name,wifi_ssid=ssid,wifi_mac=mac,isAdmin=isAdmin)


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = 'app/static/wifi'
import os

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@wifi_blue.route('/save',methods=['GET', 'POST'])
@login_required
def saveFromFile():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))            
            bit_points= wifi.loadFromFile(os.path.join(UPLOAD_FOLDER, filename))
            mapPoints = wifi.getPoints(bit_points)
            all_baidu = wifi.getAllBaidu(mapPoints)
            saveWifi(all_baidu)
            return render_template('/result.html',message='upload wifi success')
    
    return 'ok'
    
    

