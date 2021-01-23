from dataclasses import dataclass, asdict
from exchange.binance_swap import BNDM
from exchange.huobi_swap import HBDM
from exchange.utils import parse_kline
import logging


@dataclass
class Strategy:
    id: str
    status: int
    account_id: str
    exchange: str
    api_key: str
    secret_key: str
    symbol: str
    time_period: str
    price_decimal: int
    amount_decimal: int
    base_currency: str
    target_currency: str
    position_side: str
    pause_price: float
    stop_price: float
    depth_num: int = 0
    base_amount: float = 0
    amount_raise: float = 1.0
    open_diff: float = 1
    close_diff: float = 0.01
    order_num: int = 0
    last_open_price: float = 0
    entry_price: float = 0
    amount_all: float = 0

    def cli(self):
        if self.exchange == "BINANCE":
            return BNDM(self.api_key, self.secret_key)
        if self.exchange == "HUOBI":
            return HBDM(self.api_key, self.secret_key)

    def to_dict(self):
        return asdict(self)

    async def get_price(self) -> (float, float):
        res = await self.cli().depth(self.symbol)
        return float(res['asks'][0][0]), float(res['asks'][0][0])

    async def get_kline(self, period):
        res = await self.cli().kline(symbol=self.symbol, period=period, size=14
                                     )
        ema3, ema10, atr = parse_kline(res)
        return ema3, ema10, atr

    async def position(self):
        res = await self.cli().position_info()
        for i in res:
            if i['symbol'] == self.symbol and i['positionSide'] == self.position_side:
                self.entry_price = float(i['entryPrice'])
                self.amount_all = float(i['positionAmt'])

    async def strategy_long_process(self):
        await self.position()
        price_buy, price_sell = await self.get_price()
        ema3, ema10, atr = await self.get_kline('4h')
        if self.time_period == 'd1':
            ema3, ema10, atr = await self.get_kline('1d')
        self.pause_price = ema10 - atr / 2
        self.stop_price = ema10 - 2 * atr
        amount = self.base_amount * self.amount_raise ** self.order_num
        if self.amount_all == 0:
            res = await self.cli().create_order(self.symbol, amount=amount, positionSide='LONG', side="BUY")
            self.order_num += 1
            self.last_open_price = price_sell
            return 1
        else:
            logging.error('LONG:last_price={},price={},buy_con1={},sell_con1={}'.format(self.last_open_price, price_sell, self.last_open_price * (1 - self.open_diff), self.entry_price * (1 + self.close_diff)))
            if self.pause_price < price_sell < self.last_open_price * (1 - self.open_diff):
                await self.cli().create_order(self.symbol, amount=amount, positionSide='LONG', side="BUY")
                self.order_num += 1
                self.last_open_price = price_sell
                return 2
            elif price_buy > self.entry_price * (1 + self.close_diff) or price_buy < self.stop_price:
                await self.cli().create_order(self.symbol, amount=self.amount_all, positionSide='LONG', side="SELL")
                self.last_open_price = 0
                self.order_num = 0
                return 3
            else:
                pass

        return 0

    async def strategy_short_process(self):
        await self.position()
        print(self.to_dict())
        price_buy, price_sell = await self.get_price()
        ema3, ema10, atr = await self.get_kline('4h')
        if self.time_period == 'd1':
            ema3, ema10, atr = await self.get_kline('1d')
        self.pause_price = ema10 + atr / 2
        self.stop_price = ema10 + 2 * atr
        amount = self.base_amount * self.amount_raise ** self.order_num
        if self.amount_all == 0:
            res = await self.cli().create_order(self.symbol, amount=amount, positionSide='SHORT', side="SELL")
            self.order_num += 1
            self.last_open_price = price_buy
            return -1
        else:
            logging.error('SHORT:last_price={},price={},buy_con1={},sell_con1={}'.format(self.last_open_price, price_sell, self.last_open_price * (1 + self.open_diff), self.entry_price * (1 - self.close_diff)))
            if self.pause_price > price_buy > self.last_open_price * (1 + self.open_diff):
                await self.cli().create_order(self.symbol, amount=amount, positionSide='SHORT', side="SELL")
                self.order_num += 1
                self.last_open_price = price_buy
                return -2
            elif price_sell < self.entry_price * (1 - self.close_diff) or price_sell > self.stop_price:
                await self.cli().create_order(self.symbol, amount=self.amount_all, positionSide='SHORT', side="BUY")
                self.last_open_price = 0
                self.order_num = 0
                return -3
            else:
                pass
        return 0
