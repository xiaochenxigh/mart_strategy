import numpy as np
import pandas as pd
import talib


def parse_kline(res: list) -> [float, float, float]:
    tmp = []
    #print(len(res))
    for i in res:
        tmp.append([float(i[4]), float(i[2]), float(i[3])])

    a = np.array(tmp)
    b = pd.DataFrame(a)
    close = np.array(b[0])
    high = np.array(b[1])
    low = np.array(b[2])
    #print(tmp)

    ema3 = talib.EMA(np.array(close), timeperiod=3)
    ema10 = talib.EMA(np.array(close), timeperiod=10)
    atr = talib.ATR(high, low, close, timeperiod=10)
    #print(atr)
    return ema3[-1], ema10[-1], atr[-1]


