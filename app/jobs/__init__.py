from apscheduler.schedulers.background import BackgroundScheduler
from ..sharedb import deleteWifi
from ..data import ivreAnay,recordFlows
import logging
import os
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S',filename='log.txt',filemode='a')

def wifi_del():
    deleteWifi()
def flow_cal():
    recordFlows()
    
def sudoRun(sudo_command):
    mypass = 'ubuntu@2016'
    os.system('echo %s|sudo -S %s' % (mypass, sudo_command))


def scan_ivre():
    nowtime = time.localtime()
    timestr = time.strftime("%Y%m%d",nowtime)
  
    sudoRun('cp -a scans ../timestr')
    sudoRun('rm -rf scans')
    for i in range(1,255):        
        sudoRun('ivre runscans --routable --network 101.6.'+str(i)+'.1/255.255.255.0 --output=XMLFork;')
    for i in range(1,255):
        sudoRun('ivre runscans --routable --network 166.111.'+str(i)+'.1/255.255.255.0 --output=XMLFork;')   

    cmmd = 'ivre scan2db -c nmap -s %s -r ./scans;'%(timestr)
    sudoRun(cmmd)
    ivreAnay()     

    


 
sched = BackgroundScheduler()
sched.add_job(wifi_del, 'interval', weeks = 3)
sched.add_job(flow_cal, 'interval', minutes = 10)
sched.add_job(scan_ivre, 'cron',  day_of_week='fri')

sched._logger = logging
sched.start()
