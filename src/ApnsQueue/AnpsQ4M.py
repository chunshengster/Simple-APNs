'''
Created on 2012-2-25

@author: chunshengster@gmail.com

Apns Queue dequeue model that using Q4m as the Queue
'''
from python_q4m.q4m import *
class ApnsQ4M(Q4M):
    '''
    
    '''

    def __init__(self,con):
        '''
        Constructor
        '''
        super(self.__class__, self).__init__(con)
        self.table   = 'queue_table'
        self.columns = ['id',
                        'msg',
                        ]
        