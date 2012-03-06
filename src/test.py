#encoding=utf-8
__author__ = 'chunsheng'

from multiprocessing import Process
import os
import time
from ConfigParser import ConfigParser

config_file = 'config/config.ini'
cfg = ConfigParser()
a = cfg.read(config_file)
print a

#def info(title):
#    print title
##    print 'module name:', __name__
#    print 'parent process:', os.getppid()
#    print 'process id:', os.getpid()
#
#def f(name):
#    info('function f')
#    print 'hello', name
#    while True:
#        info('f line')
#        time.sleep(5)
#
#if __name__ == '__main__':
#    info('main line')
#    plist = list()
#    for i in [1,2,3,4,5]:
#        p = Process(target=f, args=('bob',))
#        p.daemon = True
#        plist.append(p)
#        p.start()
#
#    for p in plist:
#        p.join()

#class abc(object):
#    def __init__(self):
#        self.str = 'abc'
#    def say(self):
#        print id(self)
#        self.bbc.say()
#    @property
#    def get_str(self):
#        return self.str
#
#    class bbc(object):
#        __bbc = 'BBC'
#        def __init__(self):
#            pass
#
#        @staticmethod
#        def say():
#            abc.bbc.__bbc = 'bbc'
#            print abc.get_str.join('::')
#            print abc.bbc.__bbc
#
#if __name__ == '__main__':
#    abc_obj = abc()
#    abc_obj.say()

#class BBC(object):
#    __inst = None
#
#    class __impl:
#
#        def test(self):
#            return id(self)
#
#
#    def __init__(self):
#        if BBC.__inst is None:
#            BBC.__inst = BBC.__impl()
#
#
#    @staticmethod
#    def getBBC():
#        if not BBC.__inst:
#            BBC.__inst = object.__new__(BBC)
#            object.__init__(BBC.__inst)
#        return BBC.__inst
#
#
#    def echoBBC(self):
#        print "bbc"
#
#if __name__ == '__main__':
##    obj_abc = abc()
##    print obj_abc.__str__()
##    obj_abc.abc_bbc()
#    obj_bbc = BBC.getBBC()
#    obj_bbc.echoBBC()
#class Singleton:
#    """ A python singleton """
#
#    class __impl:
#        """ Implementation of the singleton interface """
#
#        def spam(self):
#            """ Test method, return singleton id """
#            return id(self)
#
#    # storage for the instance reference
#    __instance = None
#
#    def __init__(self):
#        """ Create singleton instance """
#        # Check whether we already have an instance
#        if Singleton.__instance is None:
#            # Create and remember instance
#            Singleton.__instance = Singleton.__impl()
#
#        # Store instance reference as the only member in the handle
#        self.__dict__['_Singleton__instance'] = Singleton.__instance
#
#    def __getattr__(self, attr):
#        """ Delegate access to implementation """
#        return getattr(self.__instance, attr)
#
#    def __setattr__(self, attr, value):
#        """ Delegate access to implementation """
#        return setattr(self.__instance, attr, value)
#
#
## Test it
#s1 = Singleton()
#print id(s1), s1.spam()
#
#s2 = Singleton()
#print id(s2), s2.spam()