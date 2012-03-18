#encoding=utf-8
"""
the factor of ApnsQueue
"""

def getApnsQueue(driver='mysql', Q_host='', Q_port=3306, Q_db_name='', user_name='', password='',
                 Q_name=''):
    """

    """
    if driver == "mysql":
        from ApnsQ4M import ApnsQ4M

        return ApnsQ4M(Q_Table=Q_name,
                       mysql_host=Q_host,
                       mysql_port=Q_port,
                       mysql_user=user_name,
                       mysql_pass=password,
                       mysql_db=Q_db_name)

    elif driver == "redis":
        from ApnsQredis import ApnsQredis

        return ApnsQredis(key=Q_name,
                          host=Q_host,
                          port=Q_port,
                          db=int(Q_db_name),
                          password=password,
                          socket_timeout=180)


if __name__ == '__main__':
    import time

    while True:
    #        q = getApnsQueue(driver='mysql',Q_host='192.168.1.5',Q_port=3306,Q_db_name='APNQueue',
    #                     user_name='queue_user',password='queue_user_pass',Q_name='push_test_queue_table')
        q = getApnsQueue(driver='redis', Q_host='127.0.0.1', Q_port=6379, Q_db_name=int('0'),
                         user_name='', password='', Q_name='abc')
        print q
        if q:
            if q.wait(10) is 0:
                time.sleep(10)
            else:
                item = q.dequeue()
                print item
        time.sleep(10)
