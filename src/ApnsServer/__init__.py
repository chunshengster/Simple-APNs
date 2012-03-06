#encoding=utf-8
from App import App

def runApp(sandBox, cert_file, key_file, mysql_host, mysql_db, mysql_user, mysql_pass, Q_Table, app_name):
    """
    实例化App Class，仅需要调用 runApp() 方法
    """
    apns_process = App(sandBox=sandBox, cert_file=cert_file, key_file=key_file, mysql_host=mysql_host,
                       mysql_db=mysql_db, mysql_user=mysql_user, mysql_pass=mysql_pass, Q_Table=Q_Table,
                       app_name=app_name)
    apns_process.run()
