from dataclasses import dataclass, asdict
from exchange.binance_swap import BNDM
from exchange.huobi_swap import HBDM
from exchange.utils import parse_kline
from database.redis_tmp import rds
import logging
import asyncio
import time

cli_b = BNDM('', '')
symbol_list = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'LINKUSDT', 'DOTUSDT']


async def get_kline(symbol, period, size):
    res = await cli_b.kline(symbol=symbol, period=period, size=14)
    ema3, ema10, atr = parse_kline(res)
    return ema3, ema10, atr


async def kline_thread():
    while True:
        try:
            for s in symbol_list:
                h4_ema3, h4_ema10, h4_atr = await get_kline(s, '4h', 14)
                d1_ema3, d1_ema10, d1_atr = await get_kline(s, '1d', 14)
                rds.hset('H4_EMA3', s, h4_ema3)
                rds.hset('H4_EMA10', s, h4_ema10)
                rds.hset('H4_ATR', s, h4_atr)
                rds.hset('D1_EMA3', s, d1_ema3)
                rds.hset('D1_EMA10', s, d1_ema10)
                rds.hset('D1_ATR', s, d1_atr)
        except Exception as e:
            print(e)
        time.sleep(60000)


asyncio.run(kline_thread())