#encoding=utf-8
'''
Created on 2012-2-28
@author: chunshengster@gmail.com

'''

import apns
import logging
import MySQLdb
import time
import sys,os
import traceback
from python_q4m.q4m import Q4M

try:
    import json
except:
    import simplejson as json


class App(object):
    '''
    App 运行实例，每个app（需要推送的ios app）实例化为一个App实例。
    该实例进程中实现三个功能：
    1，从ApnsQueue队列中获取需要推送的任务
    2，推送到apple的notification server
    3，周期性连接到apple的feedback server获取已经失效的device token
    Major App class definition,each App object have :
    1,One ApnsQueue connection for getting task from Queue to run
    2,apns_obj for pushing message and getting feedback
    '''

    def __init__(self, sandBox=True, cert_file=None, key_file=None, mysql_host='', mysql_db='', mysql_user='',
                 mysql_pass=''
    , Q_Table='', app_name=None):
        '''
        Constructor
        '''
        if cert_file is None or key_file is None or app_name is None:
            print "Init App error"
            return None
        else:
            (self.sandBox, self.cert_file, self.key_file, self.mysql_host, self.mysql_db, self.mysql_user,
             self.mysql_pass,
             self.Q_Table,
             self.app_name) = (
            sandBox, cert_file, key_file, mysql_host, mysql_db, mysql_user, mysql_pass, Q_Table, app_name)
            self.apns_obj = apns.APNs(use_sandbox=self.sandBox, cert_file=self.cert_file, key_file=self.key_file)

            logging.basicConfig(
                filename=os.getcwd()+"log/"+self.app_name + ".log",
                format="%(levelname)s-%(name)s : %(asctime)s - %(message)s",
                filemode='a',
                level=logging.DEBUG
            )
            self.logger = logging.getLogger(self.app_name)
            self.logger.log(logging.INFO, "App Class init by parameters: {0:>s} ".format(':'.join(str(i) for i in(\
                self.cert_file, self.key_file,\
                self.sandBox, self.mysql_db,\
                self.mysql_user, self.mysql_pass,\
                self.Q_Table, self.app_name))))


    def run(self):
        """
        App run major Loop
        """
        self.logger.info("%s got into process run " % self.app_name)
        while True:
            q = self.ApnsQueue.getQueue(self.mysql_host, self.mysql_db, self.mysql_user, self.mysql_pass, self.Q_Table);
            if q is not None:
                if  q.wait(10) == 0:
                    time.sleep(5)
                    ''
                    #TODO:在队列空闲的时间内，在apple feedback server获取失效的device token
                    ''
                    self.apns_obj.feedback_server.items()
                else:
                    res = q.dequeue()
                    self.logger.info("%s got item (%s,%s) in queue %s" % (
                        self.app_name, res['device_token'], res['payload'], self.Q_Table))
                    if self._push_to_apple(res['device_token'], res['payload']):
                        pass
                    else:
                        self.logger.error("%s got item (%s,%s) in queue %s" % (
                            self.app_name, res['device_token'], res['payload'], self.Q_Table))
                        q.abort()
                        #TODO: Do some error log
            else:
                self.logger.error("%s q=ApnsQueue.getQueue(%s, %s, %s, %s, %s) ,q is None"
                % (self.app_name, self.mysql_host, self.mysql_db, self.mysql_user, self.mysql_pass, self.Q_Table))

    def _push_to_apple(self, device_token, payload_json):
        """
        向apple 的服务器发送消息
        """
        try:
            payload_obj = json.loads(payload_json);
            payload = apns.Payload(alert=payload_obj['alert'], badge=payload_obj['badge'], sound=payload_obj['sound'])
            self.logger.info("%s will send msg to %s , msg : %s" % (
                self.app_name, device_token, payload_json))
            self.apns_obj.gateway_server.send_notification(device_token, payload)
            self.logger.info(
                "%s send msg to %s , msg : %s" % (self.app_name, device_token, payload_json))
            return True
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
            self.logger.error("%s got error %s : %s Error : %s" % (self.app_name, device_token, payload_json, e))
            return False

    @property
    def get_logger(self):
        return self.logger

    class ApnsQueue(Q4M):
        __q = None

        def __init__(self, conn, Q_Table):
            super(self.__class__, self).__init__(conn)
            self.table = Q_Table
            self.columns = ['device_token', 'payload']

        #            print self

        @staticmethod
        def getQueue(mysql_host, db_name, user_name, password, Q_Table):
            """
            不太严谨的单例模式，每个进程仅使用一个Q4M数据库的连接
            关注“App.ApnsQueue.__q” 写法，在inner class中，访问 global variable的写法
            """
            if App.ApnsQueue.__q is None:
                try:
                    conn = MySQLdb.connect(host=mysql_host, db=db_name, user=user_name, passwd=password)
                    #                    App.get_logger.info(
                    #                        "{0:>s} :App.ApnsQueue.__q is None ,connect with ({1:>s} : {2:>s} : {3:>s} : {4:>s} :{5:>s})".format(
                    #                            App.app_name,
                    #                            mysql_host,
                    #                            db_name,
                    #                            user_name,
                    #                            password,
                    #                            Q_Table))
                    App.ApnsQueue.__q = App.ApnsQueue(conn, Q_Table)
                    #                    App.get_logger.info("{0:>s} :App.ApnsQueue.__q finished connect".format(App.app_name))

                except Exception as e:
                    print e
                    sys.exit()
            return App.ApnsQueue.__q

            
            
            
            