from database.redis_tmp import rds
import json

wangB_BTCUSDT_LONG = {
    "id": 'wangB_BTCUSDT_LONG',
    'status': 1,
    "position_side": "LONG",
    "stop_price": 0,
    "pause_price": 0,
    "exchange": "BINANCE",
    'time_period': 'h4',
    "account_id": "wangB",
    "api_key": "",
    "secret_key": "",
    "symbol": "BTCUSDT",
    'base_currency': 'USDT',
    'target_currency': 'BTC',
    "price_decimal": 2,
    "amount_decimal": 3,
    "depth_num": 3,
    "base_amount": 0.02,
    "amount_raise": 1,
    "open_diff": 0.01,
    "close_diff": 0.002
}
wangB_BTCUSDT_SHORT = {
    "id": 'wangB_BTCUSDT_SHORT',
    'status': 1,
    "position_side": "SHORT",
    "stop_price": 0,
    "pause_price": 0,
    "exchange": "BINANCE",
    'time_period': 'h4',
    "account_id": "wangB",
    "api_key": "",
    "secret_key": "",
    "symbol": "BTCUSDT",
    'base_currency': 'USDT',
    'target_currency': 'BTC',
    "price_decimal": 2,
    "amount_decimal": 3,
    "depth_num": 3,
    "base_amount": 0.02,
    "amount_raise": 1,
    "open_diff": 0.01,
    "close_diff": 0.002
}

rds.hset('STRATEGY', 'wangB_BTCUSDT_SHORT', json.dumps(wangB_BTCUSDT_SHORT))
