#encoding=utf-8
"""
Created on 2012-2-25
@author: chunshengster@gmail.com
Apns Queue dequeue model that using Q4m as the Queue
"""

import sys
import time

import MySQLdb
from python_q4m.q4m import Q4M

class ApnsQ4M(Q4M):
    """
    create Q4M table:
        'create table xxxx(`device_token` char(64),`payload` varchar(512))
        engine=QUEUE  charset=utf-8'
    
    """
    con = None

    def __init__(self, Q_Table='', mysql_host='', mysql_port=3306, mysql_user='', mysql_pass='', mysql_db=''):
        (self.mysql_host, self.mysql_port, self.mysql_user, self.mysql_pass, self.mysql_db) = (
            mysql_host, mysql_port, mysql_user, mysql_pass, mysql_db)

        if self.get_conn() is True:
            super(self.__class__, self).__init__(self.con)
            self.table = Q_Table
            self.columns = ['device_token', 'payload']
        else:
            return None

    def get_conn(self):
        if not self.con:
            try:
                self.con = MySQLdb.connect(host=self.mysql_host,
                                           port=self.mysql_port,
                                           db=self.mysql_db,
                                           user=self.mysql_user,
                                           passwd=self.mysql_pass)
            except Exception as e:
                sys.stderr.writelines("%s : %s %s \n" % (time.asctime(), __file__, str(e)))
                return False
        return True

if '__main__' == __name__:
    try:
        q = ApnsQ4M('push_test_queue_table', mysql_host='127.0.0.1', mysql_port=3306, mysql_user='queue_user',
                    mysql_pass='queue_user_pass', mysql_db='APNQueue')
        while True:
            if q is not None:
                if q.wait(10) is 0:
                    time.sleep(10)
                else:
                    item = q.dequeue()
                    print item

    except Exception as e:
        print str(e)
    
            

            


        