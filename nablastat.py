#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  9 02:37:16 2020

@author: gabriel
"""

import numpy as np


def wiener(t_max, dt):
    '''
        Generates a Wiener process in the interval
        [0, t_max] with a step size of dt
    '''
    increments = np.random.normal(0, dt, size=[int(t_max/dt), 1])
    W = np.cumsum(increments)
    return W



def gbm(init, mu, sigma, t_max, dt):
    '''
        Simulated a geometric Brownian motion with value at t=0 of init, drift mu, 
        volatility sigma. The time interval is [0, t_max] with a step size of dt
    '''
    t = np.arange(0,t_max,dt)
    W = wiener(t_max, dt)
    factor = (mu - sigma**2 / 2)
    S = init * np.exp(t*factor + sigma*W)
    return S



def returns(stock, timescale=1):
    '''
        Calculates the stock's returns using a certain timescale (in days)
    '''
    return (stock[timescale:] - stock[:-timescale]) / stock[:-timescale]



def drift_estimate(stock, delta_t):
    '''
        Estimates the drift of a given stock using a step size of delta_t (in days)
    '''
    R = returns(stock, delta_t)
    return np.mean(R) / (float(delta_t)/365)



def volatility_estimate(stock, delta_t):
    '''
        Estimates the volatility of a given stock using a step size of delta_t (in days)
    '''
    R = returns(stock, delta_t)
    return np.sqrt(np.sum(np.square(R - np.mean(R))) / ((float(delta_t)/365) * (len(R)-1)))
