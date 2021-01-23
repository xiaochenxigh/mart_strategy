import base64
import hashlib
import hmac
import datetime
from urllib import parse
import urllib.parse
import aiohttp
import json
import asyncio
from operator import itemgetter
from urllib.parse import urlparse
from urllib.parse import urlencode


async def http_request(method, url, params=None, headers=None, auth=None):
    async with aiohttp.ClientSession(auth=auth) as session:
        if method == "GET":
            headers = {
                "Accept": "application/json",
                # 'Content-Type': 'application/json',
                'Accept-Language': 'zh-cn',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
            }
            async with session.get(url, params=params, timeout=2) as response:
                response = await response.read()
                return json.loads(response)
        if method == "POST":
            headers = {
                "Accept": "application/json",
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
            }
            async with session.post(url, data=json.dumps(params), timeout=20, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
    return False


async def api_key_get(url, request_path, params, ACCESS_KEY, SECRET_KEY):
    method = 'GET'
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params.update({'AccessKeyId': ACCESS_KEY,'SignatureMethod': 'HmacSHA256','SignatureVersion': '2','Timestamp': timestamp})

    host_name = host_url = url
    host_name = urlparse(host_url).hostname
    host_name = host_name.lower()

    params['Signature'] = createSign(params, method, host_name, request_path, SECRET_KEY)
    url = host_url + request_path
    return await http_request('GET', url, params)


async def api_key_post(url, request_path, params, ACCESS_KEY, SECRET_KEY):
    method = 'POST'
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params_to_sign = {'AccessKeyId': ACCESS_KEY,
                      'SignatureMethod': 'HmacSHA256',
                      'SignatureVersion': '2',
                      'Timestamp': timestamp}

    host_url = url
    host_name = urlparse(host_url).hostname
    host_name = host_name.lower()
    params_to_sign['Signature'] = createSign(params_to_sign, method, host_name, request_path, SECRET_KEY)
    url = host_url + request_path + '?' + urlencode(params_to_sign)
    return await http_request('POST', url, params)


def createSign(pParams, method, host_url, request_path, secret_key):
    sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
    encode_params = urlencode(sorted_params)
    payload = [method, host_url, request_path, encode_params]
    payload = '\n'.join(payload)
    payload = payload.encode(encoding='UTF8')
    secret_key = secret_key.encode(encoding='UTF8')
    digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    signature = signature.decode()
    return signature


class HBDM:
    def __init__(self, access_key, secret_key):
        self.__url = 'https://api.hbdm.com'
        self.__access_key = access_key
        self.__secret_key = secret_key

    @staticmethod
    def parse_data(data_dict: dict):
        status = data_dict.get('status')
        if status == 'error':
            err_code = data_dict.get('err_code')
            err_msg = data_dict.get('err_msg')
        if status == 'ok':
            return data_dict.get('data')

    async def depth(self, symbol):
        path = '/linear-swap-ex/market/depth'
        req = {
            "contract_code": symbol,
            'type': 'step0'
        }
        return await api_key_get(self.__url, path, req, self.__access_key, self.__secret_key)

    async def kline(self, symbol, period, size):
        path = '/linear-swap-ex/market/history/kline'
        req = {
            "contract_code": symbol,
            'period': period,
            'size': 60
        }
        return await api_key_get(self.__url, path, req, self.__access_key, self.__secret_key)

    async def create_order(self, symbol, amount, direction, offset, lever_rate):
        path = '/linear-swap-api/v1/swap_cross_order'
        req = {
            'contract_code': symbol,
            'order_price_type': 'optimal_20_ioc',
            'volume': amount,
            'direction': direction,
            'offset': offset,
            'lever_rate': lever_rate
        }
        return await api_key_post(self.__url, path, req, self.__access_key, self.__secret_key)

    async def cancel_order(self, symbol, order_id):
        path = '/linear-swap-api/v1/swap_cross_trigger_cancel'
        req = {
            'contract_code': symbol,
            'order_id': order_id
        }
        return await api_key_post(self.__url, path, req, self.__access_key, self.__secret_key)

    async def cancel_all(self, symbol):
        path = '/linear-swap-api/v1/swap_cross_trigger_cancelall'
        req = {
            'contract_code': symbol
        }
        return await api_key_post(self.__url, path, req, self.__access_key, self.__secret_key)

    async def open_orders(self, symbol):
        path = '/linear-swap-api/v1/swap_cross_openorders'
        req = {
            'contract_code': symbol
        }
        return await api_key_post(self.__url, path, req, self.__access_key, self.__secret_key)

    async def get_order(self, symbol, order_id):
        path = '/linear-swap-api/v1/swap_cross_order_info'
        req = {
            'contract_code': symbol,
            'order_id': order_id
        }
        return await api_key_post(self.__url, path, req, self.__access_key, self.__secret_key)

    async def account_info(self):
        path = '/linear-swap-api/v1/swap_cross_account_info'
        req = {}
        return await api_key_post(self.__url, path, req, self.__access_key, self.__secret_key)

    async def position_info(self, symbol=None):
        path = '/linear-swap-api/v1/swap_cross_position_info'
        req = {}
        if symbol:
            req['contract_code'] = symbol
        return await api_key_post(self.__url, path, req, self.__access_key, self.__secret_key)

    async def transfer(self, from_spot, to, currency, amount, margin_account):
        path = 'https://api.huobi.pro/v2/account/transfer'
        req = {
            'from': from_spot,
            'to': to,
            'currency': currency,
            'amount': amount,
            'margin-account': margin_account
        }
        # return await http_request('POST',path,req)
        return await api_key_post('https://api.huobi.pro', '/v2/account/transfer', req, self.__access_key, self.__secret_key)

# cli = HBDM(access_key='01d1b3be-e3f6eab5-67c706e9-bvrge3rf7j',secret_key='0fea5ff2-fcf2d94c-61906f30-d49a5')#wang
# cli = HBDM(access_key='a694f976-8cfde48e-9bebbe3c-xa2b53ggfc',secret_key='2b9458b6-e1f9d393-2ca5ef61-2e0f5') # zhang
# print(asyncio.get_event_loop().run_until_complete(cli.create_order('eth-usdt',1,'sell','open',30)))#800980215462445056
# print(asyncio.get_event_loop().run_until_complete(cli.get_order('eth-usdt',800980215462445056)))
# print(asyncio.get_event_loop().run_until_complete(cli.depth('eth-usdt')))
# print(asyncio.get_event_loop().run_until_complete(cli.account_info()))
# print(asyncio.get_event_loop().run_until_complete(cli.transfer('spot','linear-swap','usdt',150000,'USDT')))
# print(asyncio.get_event_loop().run_until_complete(cli.create_order('btc-usdt',1,'sell','close',30)))