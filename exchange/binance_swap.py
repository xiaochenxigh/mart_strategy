import base64
import hashlib
import hmac
import datetime
import time
import aiohttp
import json
import requests
from urllib.parse import urlparse
from urllib.parse import urlencode


async def http_request(method, url, params=None, headers=None, auth=None):
    async with aiohttp.ClientSession(auth=auth) as session:
        if method == "GET":
            async with session.get(url, params=params, timeout=2, headers=headers, proxy="http://127.0.0.1:7890", ssl=False) as response:
                response = await response.read()
                return json.loads(response)
        if method == "POST":
            async with session.post(url, timeout=20, headers=headers, proxy="http://127.0.0.1:7890", ssl=False) as response:
                if response.status == 200:
                    return await response.json()
        if method == "PUT":
            async with session.put(url, timeout=20, headers=headers, proxy="http://127.0.0.1:7890", ssl=False) as response:
                if response.status == 200:
                    return await response.json()
        if method == "DELETE":
            async with session.delete(url, timeout=20, headers=headers, proxy="http://127.0.0.1:7890", ssl=False) as response:
                if response.status == 200:
                    return await response.json()
    return False


def create_sign(params, secret_key):
    params['recvWindow'] = 60000
    params['timestamp'] = str(int(time.time() * 1000) - 1000)
    # sorted_params = sorted(params.items(), key=lambda d: d[0], reverse=False)
    encode_params = urlencode(params)
    secret_key = secret_key.encode(encoding='UTF8')
    digest = hmac.new(secret_key, encode_params.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    return digest


class BNDM:
    def __init__(self, access_key, secret_key):
        self.__url = 'https://fapi.binance.com'
        self.__access_key = access_key
        self.__secret_key = secret_key

    async def depth(self, symbol) -> dict:
        path = '/fapi/v1/depth'
        req = {
            "symbol": symbol,
            'limit': '5'
        }
        url_path = self.__url + path + '?' + urlencode(req)
        return await http_request("GET", url_path)

    async def kline(self, symbol, period, size=1) -> list:
        path = '/fapi/v1/klines'
        req = {
            "symbol": symbol,
            'interval': period,
            'limit': size
        }
        url_path = self.__url + path + '?' + urlencode(req)
        return await http_request("GET", url_path)


    async def create_order(self, symbol, amount, positionSide, side, lever_rate=30):
        path = '/fapi/v1/order'
        req = {
            'symbol': symbol,
            'side': side,
            'type': 'MARKET',
            'quantity': amount,
            'positionSide': positionSide

        }
        req['signature'] = create_sign(req, secret_key=self.__secret_key)
        headers = { "X-MBX-APIKEY": self.__access_key}
        url_path = self.__url + path + '?' + urlencode(req)
        return await http_request("POST", url_path, headers=headers)


    async def cancel_order(self, symbol, order_id):
        path = '/fapi/v1/order'
        req = {
            'symbol': symbol,
            'orderId': order_id
        }
        req['signature'] = create_sign(req, secret_key=self.__secret_key)
        headers = {"X-MBX-APIKEY": self.__access_key}
        url_path = self.__url + path + '?' + urlencode(req)
        return await http_request("DELETE", url_path, headers=headers)

    async def cancel_all(self, symbol):
        path = '/fapi/v1/allOpenOrders'
        req = {'symbol': symbol}
        req['signature'] = create_sign(req, secret_key=self.__secret_key)
        headers = {"X-MBX-APIKEY": self.__access_key}
        url_path = self.__url + path + '?' + urlencode(req)
        return await http_request("DELETE", url_path, headers=headers)

    async def open_orders(self, symbol):
        path = '/fapi/v1/openOrders'
        req = {'symbol': symbol}
        req['signature'] = create_sign(req, secret_key=self.__secret_key)
        headers = {"X-MBX-APIKEY": self.__access_key}
        return await http_request('GET', self.__url + path, req, headers)

    async def get_order(self, symbol, order_id):
        path = '/fapi/v1/order'
        req = {
            'symbol': symbol,
            'orderId': order_id
        }
        req['signature'] = create_sign(req, secret_key=self.__secret_key)
        headers = {"X-MBX-APIKEY": self.__access_key}
        return await http_request('GET', self.__url + path, req, headers)

    async def balance(self):
        path = '/fapi/v2/balance'
        req = {}
        req['signature'] = create_sign(req, secret_key=self.__secret_key)
        headers = {"X-MBX-APIKEY": self.__access_key}
        return await http_request('GET', self.__url + path, req, headers)

    async def account_info(self):
        path = '/fapi/v2/account'
        req = {}
        req['signature'] = create_sign(req, secret_key=self.__secret_key)
        headers = {"X-MBX-APIKEY": self.__access_key}
        return await http_request('GET', self.__url + path, req, headers)

    async def position_info(self):
        path = '/fapi/v2/positionRisk'
        req = {}
        req['signature'] = create_sign(req, secret_key=self.__secret_key)
        headers = {"X-MBX-APIKEY": self.__access_key}
        return await http_request('GET', self.__url + path, req, headers)

#import asyncio
#cli = BNDM(access_key="Ih9HZPWUt87REAjEy1ajpmC0IJxvAIyKqSweuENc9hbTCbNOSUVOJrb3k3WYV3wW", secret_key="tz7fOdlujIJGpd02m5PmYX0yhtMSIok0Mx2ZcAex935Te391d71BTwcIFNIoBQcD")
#res = asyncio.run(cli.position_info())
#for i in res:
#    if i['symbol']=='BTCUSDT' and i['positionSide']=='SHORT':
#        print(i)
#asyncio.run(cli.create_order('BTCUSDT', 0.05, "SHORT", "BUY", 30))
#print(asyncio.run(cli.kline(symbol='BTCUSDT', period='1h',size=5)))
#asyncio.run(cli.depth(symbol='BTCUSDT'))
#print(asyncio.run(cli.account_info()))
