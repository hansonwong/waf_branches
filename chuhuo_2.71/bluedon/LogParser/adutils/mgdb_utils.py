#!/usr/bin/env python
# coding=utf-8

from pymongo import ASCENDING
from pymongo import MongoClient


class MongoDBFlowStatistic(object):
    def __init__(self, tb):
        super(MongoDBFlowStatistic, self).__init__()
        self.tb = tb
        # create index
        self.tb.create_index([('sIP', ASCENDING),('AppMark', ASCENDING),
                              ('Date', ASCENDING), ('timestamp', ASCENDING)],
                             unique=True)

    def update_traffic(self, ip, app, date, ts, up, dw, tt):
        record = dict(sIP=ip, AppMark=app, Date=date, timestamp=ts,
                      Up=up, Down=dw, Total=tt)


        pass

if __name__ == '__main__':
    pass
