#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 16:30:40 2020

@author: gabriel
"""

import plot_setup

from db import Database

import nablastat as nstat
import numpy as np

import matplotlib.pyplot as plt

Database.session()

#%%

ticker = ''
stock = Database.getHistorical(ticker)

close = np.array(stock['close'].tolist())
close = close[7000:]
R  = nstat.returns(close, timescale=45)

fig, ax = plt.subplots(1,2)
ax[0].plot(R, '.', markersize='0.8', color='orange')
ax[0].axhline(0, 0, len(R), color='white')
ax[0].set_title("<" + ticker.upper() + "> returns plot \n $\overline{R}$=" + str(round(np.mean(R),5)) + \
                "  $\sigma_R$=" + str(round(np.std(R),5)))
ax[0].grid(color=[0.2,0.2,0.2])
ax[0].set_xlabel("time (years)")
ax[0].set_ylabel("Returns")

ax[1].hist(R, bins=20, color='orange', density=True)
ax[1].axvline(0, 0, 100, color='white')
ax[1].set_title("<" + ticker.upper() + "> Returns histogram")
ax[1].set_ylabel("Relative frequency (%)")
ax[1].set_xlabel("Returns")
ax[1].grid(color=[0.2,0.2,0.2]);
