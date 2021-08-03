#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 19:29:32 2021

@author: jay
"""



import matplotlib.pyplot as plt
import matplotlib.cm as cm

import numpy as np  
import pandas as pd
import os

path = r'/home/jay/Desktop/LFP coin cell/04 Pouch Cell/PC03 2021-07-19'

os.chdir(path)

charge_data = pd.read_csv('PC03 charge 2021-07-19.txt', sep='\t')
discharge_data = pd.read_csv('PC03 discharge 2021-07-19.txt', sep='\t')

data = charge_data
def get_step_data(data):
    a = data.loc[data.isin(['WE(1).Potential (V)']).any(axis=1)].index.tolist()
    step_start = [x + 1 for x in a]
    step_start.insert(0, 0)
    
    step_end = [x - 1 for x in a]
    step_end.append(data.index[-1])
    
    return step_start, step_end

data1 = charge_data
data2 = discharge_data
def VoltageVsCapacity(data1,data2):
    charge_step_start, charge_step_end = get_step_data(data1)
    discharge_step_start, discharge_step_end = get_step_data(data2)
    
    if len(charge_step_start) > len(discharge_step_start):
        print("Extra charge steps! Dropping the last charge step")
        charge_step_start.remove(charge_step_start[-1])
        charge_step_end.remove(charge_step_end[-1])
        
    plt.clf()
    
    color = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan','b','g','r','c','m','y','k']
    
    i= 0
    while i < len(charge_step_start):
        voltage = data1['WE(1).Potential (V)'].iloc[charge_step_start[i] : charge_step_end[i]].astype(float)
        
        time = data1['Time (s)'].iloc[charge_step_start[i] : charge_step_end[i]].astype(float)
        time = [(x - time.iloc[0])/3600 for x in time]
        current = float(data1['WE(1).Current (A)'][0])*1000
        
        capacity = [x*current for x in time]    
        
        plt.plot(capacity,voltage)
        
        voltage = data2['WE(1).Potential (V)'].iloc[discharge_step_start[i] : discharge_step_end[i]].astype(float)
        
        time = data2['Time (s)'].iloc[discharge_step_start[i] : discharge_step_end[i]].astype(float)
        time = [(x - time.iloc[0])/3600 for x in time]
        current = float(data1['WE(1).Current (A)'][0])*1000
        
        capacity = [x*current for x in time]
        
        plt.plot(capacity,voltage)    
        
        i = i+1
    
    plt.show()
    
VoltageVsCapacity(charge_data,discharge_data)