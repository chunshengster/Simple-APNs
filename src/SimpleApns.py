#!/usr/bin/evn python
#coding=utf-8
'''
Created on 2012-2-25
@author: Wang Chunsheng<chunshengster@gmail.com>
simple  apns server for easy use
'''

from ApnsServer import runApp
from ConfigParser import ConfigParser
from multiprocessing import Process
from daemon.runner import *
import os

CONFIG_FILE = os.getcwd()+('/config/config.ini')

class SimpleApns(object):
    def __init__(self):
        self.name = 'SimpleApns'
        self.working_directory = os.getcwd()
        self.stdin_path = os.devnull
        self.stdout_path = os.path.join('log/SimpleApns.log')
        self.stderr_path = os.path.join('log/SimpleApns_error.log')
        self.pidfile_path = '/var/run/simpleapns.pid'
        self.pidfile_timeout = 120

    def error_parse_config(self):
        print "Config file %s parse errror !" % CONFIG_FILE
        sys.exit()

    def run(self):
        """

        """
        try:
            cfg = ConfigParser()
            re = cfg.read(CONFIG_FILE)
            if CONFIG_FILE not in re:
                self.error_parse_config()
        except Exception:
            self.error_parse_config()

        appProcess = list()
        for i in cfg.sections():
            print "Starting push process for App %s" % cfg.get(i, 'app_name')
            p = Process(target=runApp, args=(cfg.getboolean(i, 'app_sandbox'),
                                             cfg.get(i, 'app_cert'),
                                             cfg.get(i, 'app_key'),
                                             cfg.get(i,'driver'),
                                             cfg.get(i, 'queue_host'),
                                             cfg.getint(i,'queue_port'),
                                             cfg.get(i, 'queue_db_name'),
                                             cfg.get(i, 'queue_username'),
                                             cfg.get(i, 'queue_password'),
                                             cfg.get(i, 'app_queue_name'),
                                             cfg.get(i, 'app_name'),
                                             cfg.getboolean(i,'debug'),
                                             cfg.get(i,'feedback_callback'),))
            appProcess.append(p)
            p.name = cfg.get(i, 'app_name')
            p.daemon = True
            p.start()

        for p in appProcess:
            p.join()

if  '__main__' == __name__:
    simpleapns = SimpleApns()
    #取消下面第一行的注释，同时注释掉后面两行可以取消dameon模式
    simpleapns.run()
#    runner = DaemonRunner(simpleapns)
#    runner.do_action()

        
