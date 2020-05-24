#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 16:42:08 2020

@author: gabriel
"""

import matplotlib.pyplot as plt

from matplotlib import rc, rcParams

BKG_COLOR  = "black"
FONT_COLOR = 'white'

plt.rcParams['figure.figsize']   = [16, 8]
plt.rcParams['figure.facecolor'] = BKG_COLOR
plt.rcParams['axes.facecolor']   = BKG_COLOR

rcParams['text.color']      = FONT_COLOR
rcParams['axes.labelcolor'] = FONT_COLOR
rcParams['xtick.color']     = FONT_COLOR
rcParams['ytick.color']     = FONT_COLOR

font = {'size'   : 14,
        'family' : 'serif'}
rc('font', **font)