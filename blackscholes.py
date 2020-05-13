#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  9 00:36:34 2020

@author: gabriel
"""

import numpy as np
from scipy.stats import norm 
    

class BlackScholes(object):
    def __init__(self, opt):
        self.T = opt.K
        self.K = opt.K
        
    
    def compute_d(self, t, st, r, sig):
        self.d1  = (1/(sig*np.sqrt(self.T-t))) * (np.log(st/self.K) + (r+sig**2/2)*(self.T-t))
        self.d2  = self.d1 - sig * np.sqrt(self.T-t)
        
        
    def call_value(self, t, st, r, sig):
        self.compute_d(t, st, r, sig)
        return norm.cdf(self.d1)*st - norm.cdf(self.d2)*self.K * np.exp(-r*(self.T-t))


    def put_value(self, t, st, r, sig):
        self.compute_d(t, st, r, sig)
        return norm.cdf(-self.d2)*self.K*np.exp(-r*(self.T-t)) - norm.cdf(-self.d1)*st

    
    def compute_greeks(self, t, st, r, sig):
        self.compute_d(t, st, r, sig)
        greeks = {'delta_call' : self.greek_delta_call(t, st),
                  'delta_put'  : self.greek_delta_put(t, st),
                  'gamma'      : self.greek_gamma(t, st, sig), 
                  'vega'       : self.greek_vega(t, st),
                  'theta_call' : self.greek_theta_call(t, st, sig, r), 
                  'theta_put'  : self.greek_theta_put(t, st, sig, r), 
                  'rho_call'   : self.greek_rho_call(t, st, sig, r), 
                  'rho_put'    : self.greek_rho_put(t, st, sig, r)}
        return greeks
        

    def greek_delta_call(self, t, st):
        return norm.cdf(self.d1)
    

    def greek_delta_put(self, t, st):
        return -norm.cdf(-self.d1)
    
    
    def greek_gamma(self, t, st, sig):
        return norm.pdf(self.d1) / (st * sig * np.sqrt(self.T - t))
    
    
    def greek_vega(self, t, st):
        return st * norm.pdf(self.d1)*np.sqrt(self.T - t)
    
    
    def greek_theta_call(self, t, st, sig, r):
        return -(st*norm.pdf(self.d1)*sig) / (2*np.sqrt(self.T-t)) - (r*self.K*norm.cdf(self.d2)*np.exp(-r*(self.T-t)))
    
    
    def greek_theta_put(self, t, st, sig, r):
        return -(st*norm.pdf(self.d1)*sig) / (2*np.sqrt(self.T-t)) + (r*self.K*norm.cdf(-self.d2)*np.exp(-r*(self.T-t)))

    
    def greek_rho_call(self, t, st, sig, r):
        return self.K*norm.cdf(self.d2)*(self.T-t)*np.exp(-r*(self.T-t))
        
    def greek_rho_put(self, t, st, sig, r):
        return -self.K*norm.cdf(-self.d2)*(self.T-t)*np.exp(-r*(self.T-t))