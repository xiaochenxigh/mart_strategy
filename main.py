from database.redis_tmp import rds
import json
import time
import asyncio
from exchange.swap import Strategy


async def main():
    res = rds.hkeys("STRATEGY")
    for j in res:
        s = json.loads(rds.hget("STRATEGY", j))
        M = Strategy(
            id=s.get('id'),
            status=s.get('status', 0),
            account_id=s.get('account_id'),
            exchange=s.get('exchange'),
            api_key=s.get('api_key'),
            secret_key=s.get('secret_key'),
            symbol=s.get('symbol'),
            time_period=s.get('time_period'),
            price_decimal=s.get('price_decimal'),
            amount_decimal=s.get('amount_decimal'),
            base_currency=s.get('base_currency'),
            target_currency=s.get('target_currency'),
            position_side=s.get('position_side'),
            pause_price=s.get('pause_price'),
            stop_price=s.get('stop_price'),
            depth_num=s.get('depth_num', 0),
            base_amount=s.get('base_amount', 0),
            amount_raise=s.get('amount_raise', 1),
            open_diff=s.get('open_diff', 1),
            close_diff=s.get('close_diff', 0.01),
            order_num=s.get('order_num', 0),
            last_open_price=s.get('last_open_price', 0),
            entry_price=s.get('entry_price', 0),
            amount_all=s.get('amount_all', 0))

        if M.position_side == "LONG":
            long_res = await M.strategy_long_process()
            rds.hset("STRATEGY", M.account_id + '_' + M.symbol + '_' + M.position_side, json.dumps(M.to_dict()))
            print(long_res)
        if M.position_side == 'SHORT':
            short_res = await M.strategy_short_process()
            rds.hset("STRATEGY", M.account_id + '_' + M.symbol + '_' + M.position_side, json.dumps(M.to_dict()))
            print(short_res)


asyncio.run(main())
