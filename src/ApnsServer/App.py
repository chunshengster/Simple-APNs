#encoding=utf-8
"""
Created on 2012-2-28
@author: Wang chunsheng<chunshengster@gmail.com>

"""

import logging
import time
import sys
import os
import traceback
import apns

from ApnsQueue import getApnsQueue
from ssl import SSLError

try:
    import json
except ImportError:
    import simplejson as json

class App(object):
    """
    App 运行实例，每个app（需要推送的ios app）实例化为一个App实例。
    该实例进程中实现三个功能：
    1，从ApnsQueue队列中获取需要推送的任务
    2，推送到apple的notification server
    3，周期性连接到apple的feedback server获取已经失效的device token
    Major App class definition,each App object have :
    1,One RunQueue connection for getting task from Queue to run
    2,apns_obj for pushing message and getting feedback
    """

    def __init__(self, sandBox=True, cert_file=None, key_file=None, driver='mysql', Q_host='', Q_port=3306, Q_db='',
                 Q_user='', Q_pass='', Q_name='', app_name=None, is_debug=True, feedback_callback=''):
        """
        
        """
        if (cert_file is None) or (key_file is None) or (app_name is None):
            sys.stderr.writelines(
                ('%s : Init App error:\n' +
                 '\t With parameters: sandBox=%s cert_file=%s, key_file=%s, Q_host=%s,' +
                 'Q_port=%s, Q_db=%s, Q_user=%s, Q_pass=%s, Q_name=%s app_name=%s,debug=%s,' +
                 'feedback_callback=%s \n') %
                (time.asctime(), str(sandBox), cert_file, key_file, Q_host, Q_port, Q_db, Q_user,
                 Q_pass, Q_name, app_name, str(is_debug), feedback_callback))
            return None
        else:
            (self.sandBox, self.cert_file, self.key_file, self.driver, self.Q_host, self.Q_port, self.Q_db,
             self.Q_user,
             self.Q_pass,
             self.Q_name,
             self.app_name) = (
                sandBox, cert_file, key_file, driver, Q_host, Q_port, Q_db, Q_user, Q_pass, Q_name,
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
                             ' key_file=%s, Q_host=%s, Q_port=%s, Q_db=%s, Q_user=%s,' +
                             ' Q_pass=%s, Q_name=%s, app_name=%s, is_debug=%s, feedback_callback=%s') %
                            (str(self.sandBox), self.cert_file, self.key_file, self.Q_host, self.Q_port,
                             self.Q_db, self.Q_user, self.Q_pass, self.Q_name, self.app_name,
                             str(is_debug), str(self.feedback)))
            sys.stdout.writelines(
                ('%s : App Class init by parameters: parameters: sandBox=%s, cert_file=%s,' +
                 ' key_file=%s, Q_host=%s, Q_port=%s, Q_db=%s, Q_user=%s,' +
                 ' Q_pass=%s, Q_name=%s, app_name=%s, is_debug=%s, feedback_callback=%s\n') %
                (time.asctime(), str(self.sandBox), self.cert_file, self.key_file, self.Q_host, self.Q_port,
                 self.Q_db, self.Q_user, self.Q_pass, self.Q_name, self.app_name,
                 str(is_debug), self.feedback))
            sys.stdout.flush()


    def run(self):
        """
        App run major loop
        """
        self.logger.info("%s got into process run " % self.app_name)
        while True:
            q = self.RunQueue.getQueue(self.driver, self.Q_host, self.Q_port, self.Q_db, self.Q_user,
                                       self.Q_pass, self.Q_name)
            if q is not None:
                if q.wait(10) is 0:
                    time.sleep(5)
                    #TODO(chunshengster):在队列空闲的时间内，在apple feedback server获取失效的device token
                    for item in self.apns_obj.feedback_server.items():
                        self.logger.info("got feed back item : %s" % item)
                else:
                    try:
                        item = q.dequeue()
                        if item is not None:
                            self.logger.info(
                                '{0:>s} got item ({1:>s},{2:>s}) in queue {3:>s}'.format(self.app_name, item['device_token']
                                                                                         ,
                                                                                         item['payload'], self.Q_name))
                            res = self._push_to_apple(item['device_token'], item['payload'])
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
                    except Exception as e:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stderr)

            else:
                """
                连接队列失败,sleep(120)后重新连接
                """
                self.logger.error(
                    'q=RunQueue.getQueue(%s, %s, %s, %s, %s, %s), q is None,try to reconnect' %
                    (self.Q_host, self.Q_port, self.Q_db, self.Q_user, self.Q_pass, self.Q_name))
                sys.stderr.writelines(
                    '%s : q=RunQueue.getQueue(%s, %s, %s, %s, %s, %s) ,q is None,reconnect \n' %
                    (time.asctime(), self.Q_host, self.Q_port, self.Q_db, self.Q_user, self.Q_pass,
                     self.Q_name))
                time.sleep(120)

    def _push_to_apple(self, device_token, payload_json):
        """
        向apple 的服务器发送消息
        """
        try:
            payload_obj = json.loads(payload_json)
            payload = apns.Payload(alert=payload_obj['alert'], badge=payload_obj['badge'], sound=payload_obj['sound'])
            self.logger.debug(
                '{0:>s} will send msg to {1:>s} , msg : {2:>s}'.format(self.app_name, device_token, payload_json))
            self.apns_obj.gateway_server.send_notification(device_token, payload)
            self.logger.info(
                '{0:>s} sent msg to {1:>s} , msg : {2:>s}'.format(self.app_name, device_token, payload_json))
            return True
        except SSLError as e:
            #SSL error
            self.logger.error(
                '{0:>s} got error {1:>s} : {2:>s} Error : {3:>s}'.format(self.app_name, device_token, payload_json, e))
            sys.stderr.writelines(
                '{0:>s} : {1:>s} got error {2:>s} : {3:>s} Error : {4:>s} \n'.format(time.asctime(), self.app_name,
                                                                                     device_token, payload_json,
                                                                                     str(e)))
            return None
        except ValueError as e:
            #For json string error:not a standard json string
            self.logger.error('{0:>s} got error {1:>s} : {2:>s} Error : {3:>s}'.format(self.app_name,
                                                                                       device_token, payload_json,
                                                                                       e.message))
            sys.stderr.writelines(
                '{0:>s} : {1:>s} got error {2:>s} : {3:>s} Error : {4:>s} \n'.format(time.asctime(), self.app_name,
                                                                                     device_token, payload_json,
                                                                                     str(e)))
            return False
        except Exception:
            """
            For unknowen Exceptions
            """
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stderr)
            return False

    class RunQueue(object):
        """
        与APP类绑定的运行时队列对象
        """
        _q = None

        def __init__(self):
            pass

        @staticmethod
        def getQueue(driver='mysql', Q_host='', Q_port=3306, Q_db_name='', user_name='', password='',
                     Q_name=''):
            """
            不太严谨的单例模式，每个进程仅使用一个Q4M数据库的连接
             关注“App.RunQueue.__q” 写法，在inner class中，访问 global variable的写法
            """
            if App.RunQueue._q is None:
                try:
                    App.RunQueue._q = getApnsQueue(driver=driver, Q_host=Q_host, Q_port=Q_port, Q_db_name=Q_db_name,
                                                   user_name=user_name, password=password, Q_name=Q_name)
                except Exception as e:
                    sys.stderr.writelines(
                        ('%s : cathe exception of MySQLdb connect with host=%s, port=%s, db=%s,' +
                         ' user=%s, passwd=%s, Exception: %s \n') % (
                            time.asctime(), Q_host, Q_port, Q_db_name, user_name, password, str(e)))
                    return None
            return App.RunQueue._q

            
            
            
            