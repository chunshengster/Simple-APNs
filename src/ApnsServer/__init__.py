#encoding=utf-8
from App import App
import sys
import time

def runApp(sandBox=True, cert_file='', key_file='', mysql_host='', mysql_port=3306, mysql_db='', mysql_user='',
           mysql_pass='', Q_Table='', app_name='', is_debug=True, feedback_callback=''):
    """
    实例化App Class，仅需要调用 runApp() 方法
    """
    apns_process = App(sandBox=sandBox, cert_file=cert_file, key_file=key_file, mysql_host=mysql_host,
                       mysql_port=mysql_port, mysql_db=mysql_db, mysql_user=mysql_user, mysql_pass=mysql_pass,
                       Q_Table=Q_Table, app_name=app_name, is_debug=is_debug, feedback_callback=feedback_callback)
    if apns_process:
        apns_process.run()
    else:
        #TODO:do error log
        sys.stderr.writelines(
            ('%s : App run failed with parameters : sandBox=%s, cert_file=%s, key_file=%s, mysql_host=%s,' +
             'mysql_port=%s, mysql_db=%s, mysql_user=%s, mysql_pass=%s,Q_Table=%s, app_name=%s,is_debug=%s,' +
             'feedback_callback=%s') %
            (time.asctime(), str(sandBox), cert_file, key_file, mysql_host, mysql_port, mysql_db,
             mysql_user, mysql_pass, Q_Table, app_name, str(is_debug), feedback_callback))
        return 0
        pass
