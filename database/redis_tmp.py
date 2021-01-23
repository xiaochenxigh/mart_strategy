import redis
import json
import time


class Redis:
    def __init__(self, host, port, db=0):
        self.__host = host
        self.__port = port
        self.__db = db
        self.__pool = None

    def get_pool(self):
        if not self.__pool:
            self.__pool = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, decode_responses=True))  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
        return self.__pool




rds = Redis('localhost', 6379, 0).get_pool()