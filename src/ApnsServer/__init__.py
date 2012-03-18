#encoding=utf-8
from App import App
import sys
import time

def runApp(sandBox=True, cert_file='', key_file='', driver='mysql', queue_host='', queue_port=3306, queue_db_name='',
           queue_username='', queue_password='', Q_name='', app_name='', is_debug=True, feedback_callback=''):
    """
    实例化App Class，仅需要调用 runApp() 方法
    """
    apns_process = App(sandBox=sandBox, cert_file=cert_file, key_file=key_file,driver=driver, Q_host=queue_host,
                       Q_port=queue_port, Q_db=queue_db_name, Q_user=queue_username, Q_pass=queue_password,
                       Q_name =Q_name, app_name=app_name, is_debug=is_debug, feedback_callback=feedback_callback)
    if apns_process:
        apns_process.run()
    else:
        sys.stderr.writelines(
            ('%s : App run failed with parameters : sandBox=%s, cert_file=%s, key_file=%s, queue_host=%s,' +
             'queue_port=%s, queue_db_name=%s, queue_username=%s, queue_password=%s,Q_name=%s, app_name=%s,is_debug=%s,' +
             'feedback_callback=%s') %
            (time.asctime(), str(sandBox), cert_file, key_file, queue_host, queue_port, queue_db_name,
             queue_username, queue_password, Q_name, app_name, str(is_debug), feedback_callback))
        return 0
