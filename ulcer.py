import numpy as np
import scipy as sp


YEAR_DAYS = 252


def drawdowns(returns):
    prices = np.cumprod(1. + returns)
    maxs = np.maximum.accumulate(prices)
    return (maxs - prices) / maxs


def ulcer(returns):
    ddi = np.max(drawdowns(returns))
    ui = np.sqrt(np.mean(ddi * ddi))
    upi = np.mean(ri) / ui
    return ui, upi


def DaR(alpha, returns):
    dds = drawdowns(returns)
    dar = np.quantile(dds, alpha)
    tail = dds[dds >= dar]
    cdar = np.mean(tail)
    return dar, cdar


def pitfall(alpha, returns):
    vol = np.std(returns)
    _, cdar = DaR(alpha, returns)
    return cdar / vol


def serenity_ratio(alpha, returns):
    dds = drawdowns(returns)
    ddi = np.max(dds)
    ui = np.sqrt(np.mean(ddi * ddi))
    vol = np.std(returns)
    dar = np.quantile(dds, alpha)
    tail = dds[dds >= dar]
    cdar = np.mean(tail)

    penalized_risk = ui * vol / cdar
    return np.mean(returns) / penalized_risk


def acf(returns):
    r0 = returns - np.mean(returns)
    h = sp.linalg.hankel(r0)
    retval = np.dot(h, h)[0, :]
    retval /= len(retval)
    return retval


def improved_sharpe(returns):
    a0 = acf(retns)
    # we are only interested in a year subset
    a0 = a0[1:(YEAR_DAYS + 1)]
    vol = np.std(returns)
    var_n = vol * vol * (YEAR_DAYS + 2. * np.sum(a0 * np.array(range(YEAR_DAYS - 1, -1, -1))))
    return YEAR_DAYS * np.mean(returns) / np.sqrt(var_n)

