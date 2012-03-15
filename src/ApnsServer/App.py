#encoding=utf-8
'''
Created on 2012-2-28
@author: Wang chunsheng<chunshengster@gmail.com>

'''


import logging
import MySQLdb
import time
import sys
import os
import traceback
import apns

from python_q4m.q4m import Q4M
from ssl import SSLError

try:
    import json
except:
    import simplejson as json

class App(object):
    """
    App 运行实例，每个app（需要推送的ios app）实例化为一个App实例。
    该实例进程中实现三个功能：
    1，从ApnsQueue队列中获取需要推送的任务
    2，推送到apple的notification server
    3，周期性连接到apple的feedback server获取已经失效的device token
    Major App class definition,each App object have :
    1,One ApnsQueue connection for getting task from Queue to run
    2,apns_obj for pushing message and getting feedback
    """

    def __init__(self, sandBox=True, cert_file=None, key_file=None, mysql_host='', mysql_port=3306, mysql_db='',
                 mysql_user='', mysql_pass='', Q_Table='', app_name=None, is_debug=True, feedback_callback=''):
        if (cert_file is None) or (key_file is None) or (app_name is None):
            sys.stderr.writelines(
                ('%s : Init App error:\n'+
                 '\t With parameters: sandBox=%s cert_file=%s, key_file=%s, mysql_host=%s,' +
                 'mysql_port=%s, mysql_db=%s, mysql_user=%s, mysql_pass=%s, Q_Table=%s app_name=%s,debug=%s,' +
                 'feedback_callback=%s \n') %
                (time.asctime(), str(sandBox), cert_file, key_file, mysql_host, mysql_port, mysql_db, mysql_user,
                 mysql_pass, Q_Table, app_name, str(is_debug), feedback_callback))
            return None
        else:
            (self.sandBox, self.cert_file, self.key_file, self.mysql_host, self.mysql_port, self.mysql_db,
             self.mysql_user,
             self.mysql_pass,
             self.Q_Table,
             self.app_name) = (
                sandBox, cert_file, key_file, mysql_host, mysql_port, mysql_db, mysql_user, mysql_pass, Q_Table,
                app_name)

            if is_debug is True:
                log_level = logging.DEBUG
            else:
                log_level = logging.INFO

            # feedback call back url
            if feedback_callback is '':
                self.feedback = None
            else:
                self.feedback = feedback_callback

            self.apns_obj = apns.APNs(use_sandbox=self.sandBox, cert_file=self.cert_file, key_file=self.key_file)

            dir_name, _ = os.path.split(os.path.abspath(__file__))
            logging.basicConfig(
                filename='%s/../log/App/%s.log' % (dir_name, self.app_name),
                format='%(levelname)s-%(name)s : %(asctime)s - %(message)s',
                filemode='a+',
                level=log_level
            )
            self.logger = logging.getLogger(self.app_name)
            self.logger.log(logging.INFO,
                            ('App Class init by parameters: parameters: sandBox=%s, cert_file=%s,' +
                             ' key_file=%s, mysql_host=%s, mysql_port=%s, mysql_db=%s, mysql_user=%s,' +
                             ' mysql_pass=%s, Q_Table=%s, app_name=%s, is_debug=%s, feedback_callback=%s') %
                            (str(self.sandBox), self.cert_file, self.key_file, self.mysql_host, self.mysql_port,
                             self.mysql_db, self.mysql_user, self.mysql_pass, self.Q_Table, self.app_name,
                             str(is_debug), str(self.feedback)))
            sys.stdout.writelines(
                ('%s : App Class init by parameters: parameters: sandBox=%s, cert_file=%s,' +
                 ' key_file=%s, mysql_host=%s, mysql_port=%s, mysql_db=%s, mysql_user=%s,' +
                 ' mysql_pass=%s, Q_Table=%s, app_name=%s, is_debug=%s, feedback_callback=%s\n') %
                (time.asctime(), str(self.sandBox), self.cert_file, self.key_file, self.mysql_host, self.mysql_port,
                 self.mysql_db, self.mysql_user, self.mysql_pass, self.Q_Table, self.app_name,
                 str(is_debug), self.feedback))
            sys.stdout.flush()


    def run(self):
        """
        App run major loop
        """
        self.logger.info("%s got into process run " % self.app_name)
        while True:
            q = self.ApnsQueue.getQueue(self.mysql_host, self.mysql_port, self.mysql_db, self.mysql_user,
                                        self.mysql_pass, self.Q_Table);
            if q is not None:
                if  q.wait(10) == 0:
                    time.sleep(5)
                    #TODO(chunshengster):在队列空闲的时间内，在apple feedback server获取失效的device token
                    #self.apns_obj.feedback_server.items()
                else:
                    res = q.dequeue()
                    self.logger.info(
                        '{0:>s} got item ({1:>s},{2:>s}) in queue {3:>s}'.format(self.app_name, res['device_token'],
                                                                                 res['payload'], self.Q_Table))
                    res = self._push_to_apple(res['device_token'], res['payload'])
                    if res is None:
                        """
                        队列回退,队列元素退回,目前在SSLError的情况下会返回None,sleep(10)
                        """
                        q.abort()
                        time.sleep(10)
                    elif res is False:
                        """
                        发送数据异常,抛弃队列元素
                        """
                        q.end()
            else:
                """
                连接队列失败,sleep(120)后重新连接
                """
                self.logger.error(
                    'q=ApnsQueue.getQueue(%s, %s, %s, %s, %s, %s), q is None,try to reconnect' %
                    (self.mysql_host, self.mysql_port, self.mysql_db, self.mysql_user, self.mysql_pass, self.Q_Table))
                sys.stderr.writelines(
                    '%s : q=ApnsQueue.getQueue(%s, %s, %s, %s, %s, %s) ,q is None,reconnect \n' %
                    (time.asctime(), self.mysql_host, self.mysql_port, self.mysql_db, self.mysql_user, self.mysql_pass,
                     self.Q_Table))
                time.sleep(120)

    def _push_to_apple(self, device_token, payload_json):
        """
        向apple 的服务器发送消息
        """
        try:
            payload_obj = json.loads(payload_json);
            payload = apns.Payload(alert=payload_obj['alert'], badge=payload_obj['badge'], sound=payload_obj['sound'])
            self.logger.debug(
                '{0:>s} will send msg to {1:>s} , msg : {2:>s}'.format(self.app_name, device_token, payload_json))
            self.apns_obj.gateway_server.send_notification(device_token, payload)
            self.logger.info(
                '{0:>s} sent msg to {1:>s} , msg : {2:>s}'.format(self.app_name, device_token, payload_json))
            return True
        except SSLError as e:
            """
            SSL error 
            """
            self.logger.error(
                '{0:>s} got error {1:>s} : {2:>s} Error : {3:>s}'.format(self.app_name, device_token, payload_json, e))
            sys.stderr.writelines(
                '{0:>s} : {1:>s} got error {2:>s} : {3:>s} Error : {4:>s} \n'.format(time.asctime(), self.app_name,
                                                                                  device_token, payload_json,
                                                                                  str(e)))
            return None
        except ValueError as e:
            """
            For json string error:not a standard json string
            """
            self.logger.error('{0:>s} got error {1:>s} : {2:>s} Error : {3:>s}'.format(self.app_name,
                                                                                       device_token, payload_json,
                                                                                       e.message))
            sys.stderr.writelines(
                '{0:>s} : {1:>s} got error {2:>s} : {3:>s} Error : {4:>s} \n'.format(time.asctime(), self.app_name,
                                                                                  device_token, payload_json,
                                                                                  str(e)))
            return False
        except Exception as e:
            """
            For unknowen Exceptions
            """

            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stderr)
            return False

    class ApnsQueue(Q4M):
        _q = None

        def __init__(self, conn, Q_Table):
            super(self.__class__, self).__init__(conn)
            self.table = Q_Table
            self.columns = ['device_token', 'payload']

        @staticmethod
        def getQueue(mysql_host='', mysql_port=3306, db_name='', user_name='', password='', Q_Table=''):
            """
            不太严谨的单例模式，每个进程仅使用一个Q4M数据库的连接
             关注“App.ApnsQueue.__q” 写法，在inner class中，访问 global variable的写法
            """
            if App.ApnsQueue._q is None:
                try:
                    conn = MySQLdb.connect(host=mysql_host, port=mysql_port, db=db_name, user=user_name,
                                           passwd=password)
                    if conn:
                        App.ApnsQueue._q = App.ApnsQueue(conn, Q_Table)
                except Exception as e:
                    sys.stderr.writelines(
                        ('%s : cathe exception of MySQLdb connect with host=%s, port=%s, db=%s,' +
                         ' user=%s, passwd=%s, Exception: %s \n') % (
                            time.asctime(), mysql_host, mysql_port, db_name, user_name, password, str(e)))
                    return None
            return App.ApnsQueue._q

            
            
            
            