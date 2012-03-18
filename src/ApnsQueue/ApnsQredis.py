#encoding=utf-8
"""
Created on 2012-2-25
@author: chunshengster <chunshengster@gmail.com>
Apns Queue class that use Redis Queue
"""
import sys
import time

from redis_queue import Queue

try:
    import json
except ImportError:
    import simplejson as json

class ApnsQredis(Queue):
    """
    封装redis_queue，使其符合Q4M的队列用法：
        wait()
        dequque()
        abort()
        end()
        test json string: {\"device_token\":\"6c0d98c62fbae1458052af92ee64869be138b62006902078bd23250a9c2d7bca\",\"payload\":\"{\\\"alert\\\":\\\"hello,world\\\",\\\"sound\\\":\\\"default\\\",\\\"badge\\\":1}\"}
    """

    def __init__(self, key, **kwargs):
        super(self.__class__, self).__init__(key, **kwargs)
        self.current_item = None

    def dequeue(self):
        """
        you must check the item returned is None or not 
        """
        if self.current_item is not None:
            try:
                return json.loads(self.current_item)
            except ValueError as e:
                #json parse error
                sys.stderr.writelines("%s : %s \n\t %s : %s \n" % (time.asctime(), self.current_item, __file__, str(e)))
                self.current_item = None
        return None

    def wait(self, timeout=10):
        try:
            _, self.current_item = self.pop(timeout)
            return 1
        except IndexError:
            self.current_item = None
            return 0
        except Exception as e:
            sys.stderr.writelines("%s : %s \n" % (time.asctime(), str(e)))
            return None


    def abort(self):
        """
        push the current item back to the queue
        """
        if self.current_item:
            try:
                self.appendleft(self.current_item)
                self.current_item = None
                return True
            except Exception as e:
                sys.stderr.writelines("%s : %s \n" % (time.asctime(), str(e)))
        return False

    def end(self):
        pass


if '__main__' == __name__:
    import time

    try:
        q = ApnsQredis("abc", host='127.0.0.1', port=6379, db=0)
        if q is not None:
            while True:
                try:
                    if q.wait(10) == 0:
                        time.sleep(10)
                    else:
                        item = q.dequeue()
                        if item:
                            print item
                            q.abort()
                except IndexError:
                    pass
                except Exception as e:
                    print e.message
                    time.sleep(10)
                time.sleep(10)
        else:
            print "q is none"
    except Exception as e:
        print str(e)