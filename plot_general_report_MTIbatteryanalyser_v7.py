#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 01:00:35 2021

@author: jay
"""


import matplotlib.pyplot as plt
import matplotlib.cm as cm

import numpy as np  
import pandas as pd
import os

# --> Enter the path for the excel sheet within the quotes #
path = r"/mnt/01D32FA04B3DCAD0/Thermal Runaway Sensor Data/02 Thermal Runaway/03 LFP Graphite cells/LFP Graphite cell data/03 LFP Graphite full cell"

# --> Enter the file name for the excel sheet within the quotes #
filename = 'CC52_2021-07-07_v1.xls'

# --> Enter 'name', 'title' and 'active_material_weight' based on the data
name = 'CC52'           # Cell identification
title = 'LFP Graphite cell' + " "    # Cell type
active_material_weight = 2.528   # weight in mg

# --> Enter the path for saving figures within the quotes #
# fig_save_path = r'/mnt/01D32FA04B3DCAD0/Thermal Runaway Sensor Data/02 Thermal Runaway/03 LFP Graphite cells/LFP Graphite cell data/03 LFP Graphite full cell'

results_dir = r"/mnt/01D32FA04B3DCAD0/Thermal Runaway Sensor Data/02 Thermal Runaway/03 LFP Graphite cells/LFP Graphite cell data/03 LFP Graphite full cell plots/"

os.chdir(path)

# Reading multiple sheets at the same time
# Creates a dictionary of dataframes
data=pd.read_excel(filename,sheet_name=None)

# Reads the column headers from the first sheet
column_header = data.get('Sheet1').columns

# Converting the dictionary of dataframes into a single dataframe
# Dictionary can cause jumbling of columns; Reordering the columns based on column headers
if type(data) == dict:
    data = pd.concat(data.values())
    data = data.reindex(columns=column_header)

# Data has the serial number from excel as the index
# Reindexing to avoid repetitions    
data = data.T.reset_index().T # Using numbers as column headers temporarily
data = data.reset_index(drop=True)

# General report from MTI analyser has 3 header rows
# The first three rows are made headers and are removed from the data
data.columns=pd.MultiIndex.from_arrays(data.iloc[0:3].values)
data = data.iloc[3:]

# Since the data is concatenated from several sheets it may have repeated header rows which should be removed by looking for certain strings
data = data[~data.iloc[:,2].isin(['Step Type','Record ID'])]
data = data.reset_index(drop=True) # Resetting index again because it may have changed due to the removal of redundant header rows

# # Change 'name', 'title' and 'active_material_weight' based on the data
# name = 'CC52'
# title = "LFP Graphite cell "
# active_material_weight = 2.528   # weight in mg

def get_step_data(data):
    # Modifying the extracted data
    mod_data = data[data.iloc[:,0].isnull()] # removing rows with the 'cycle ID' values 
    mod_data = mod_data.reset_index() # resetting index because data maybe from multiple sheets
    
    charge_step_start = [i for i, x in enumerate(mod_data.iloc[:,3]) if x == "CC_Chg"] # Checking the 'Step Type' for Charge step
    charge_step_start = [x+1 for x in charge_step_start]
    
    discharge_step_start = [i for i, x in enumerate(mod_data.iloc[:,3]) if x == "CC_DChg"] # Checking the 'Step Type' for Charge step
    discharge_step_start = [x+1 for x in discharge_step_start]
    
    # Even number of charge and discharge steps must be present
    # charge_step_start.remove(charge_step_start[-1])
    # discharge_step_start.remove(discharge_step_start[-1])
    
    # For charge before discharge
    if charge_step_start[0] < discharge_step_start[0]: # Checking only the first step to determine which step comes first
        print("Charge before discharge")
        
        i = 0
        while i < len(charge_step_start)-1:
            if not charge_step_start[i] < discharge_step_start[i] : # All charge steps should occur before discharge steps. Sometimes there are errors in the data. This condition will check for those errors
                print("Abnormalities detected!"+str(i)+"cycle")
                discharge_step_start.remove(discharge_step_start[i])

            if not charge_step_start[i+1] > discharge_step_start[i] :
                print("Abnormalities detected!"+str(i+1)+"cycle")
                charge_step_start.remove(charge_step_start[i+1])

            i = i + 1
            
        charge_step_end = [x-2 for x in discharge_step_start] # Charge step end is one row above the discharge step start
        discharge_step_end = [x-2 for x in charge_step_start[1:]] # Discharge step end is one row above the consequent charge step start
        discharge_step_end.append(mod_data.index[-1])
        
       
            
    # For discharge before charge
    elif charge_step_start[0] > discharge_step_start[0]: # Checking only the first step to determine which step comes first
        print("Discharge before charge")
        
        i = 0
        while i < len(discharge_step_start)-1:
            if not discharge_step_start[i] < charge_step_start[i] : # All charge steps should occur before discharge steps. Sometimes there are errors in the data. This condition will check for those errors
                print("Abnormalities detected!"+str(i)+"cycle")
                charge_step_start.remove(charge_step_start[i])
                
            if not discharge_step_start[i+1] > charge_step_start[i] :
                print("Abnormalities detected!"+str(i+1)+"cycle")
                discharge_step_start.remove(discharge_step_start[i+1])
                
            i = i + 1
            
        discharge_step_end = [x-2 for x in charge_step_start] #
        charge_step_end = [x-2 for x in discharge_step_start[1:]] # 
        charge_step_end.append(mod_data.index[-1])
        
    return mod_data, charge_step_start, charge_step_end, discharge_step_start, discharge_step_end
    

def CapacityVsCycle(data,name):
    
    # a =4 # starting cycle; usually 3 formation cycles at 0.1 C. Therefore start from 3 
    a = 1
    
    mod_data, charge_step_start, charge_step_end, discharge_step_start, discharge_step_end = get_step_data(data)
    
    charge_capacities = mod_data.iloc[charge_step_end,8] #values in mAh
    discharge_capacities = mod_data.iloc[discharge_step_end,8] #values in mAh
    
    charge_capacities = charge_capacities/(active_material_weight/1000) #values in mAh/g
    discharge_capacities = discharge_capacities/(active_material_weight/1000) #values in mAh/g
    
    coulombic_efficiency = discharge_capacities.reset_index(drop=True) / charge_capacities.reset_index(drop=True) * 100
    
    cycle = np.arange(1,len(charge_step_start)+1) #Assuming no errors in the charge steps; ie every charge step occurs exactly once per cycle
    
    fig, ax1 = plt.subplots()
    
    ax1.set_xlabel("Cycle number", fontname='Times New Roman', fontsize=12)
    ax1.set_ylabel("Capacity (mAh/g)", fontname='Times New Roman', fontsize=12)
    ax1.plot(cycle[a:], charge_capacities[a:], marker='o', color='blue', markersize=3, linewidth=0, label="Charge capacity")
    ax1.plot(cycle[a:], discharge_capacities[a:], marker='o', color='maroon', markersize=3, linewidth=0, label="Discharge capacity")
    
    ax1.set_ylim(60,120) # for LFP
    # ax1.set_ylim(250,360) #for Graphite
    
    # ax1.set_ylim(1.5,2.5) # temp
    
    ax1.set_xlim(1,50) # 50 cycles usually
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    ax2.set_ylabel("Coulombic Efficiency", fontname='Times New Roman', fontsize=12)
    ax2.plot(cycle[a:], coulombic_efficiency[a:], marker='o', color='black', markersize=3, linewidth=0, label="Coulombic efficiency")
    ax2.set_ylim(90,100)
    
    ax2.set_yticks(np.linspace(ax2.get_ybound()[0], ax2.get_ybound()[1], 4))

    
    ax1.legend(loc = 'lower left', frameon=False)
    ax2.legend(loc = 'lower right', frameon=False)

    plt.title(title + name, loc='center', fontsize=18, fontweight=0)
    
    # plt.show()
    plt.savefig(results_dir + name + '_1.png', dpi=300, bbox_inches="tight")
    plt.clf()
    
CapacityVsCycle(data,name)



def CapacityVsVoltage(data,name):
    
    mod_data, charge_step_start, charge_step_end, discharge_step_start, discharge_step_end = get_step_data(data)
    
    cycle = np.arange(1,len(charge_step_start)+1) #All cycles #Assuming no errors in the charge steps; ie every charge step occurs exactly once per cycle
    step = 5 # Plotting every nth cycle
    # step = 1
    
    # color = ['midnightblue', 'navy', 'darkblue', 'mediumblue', 'blue', 'slateblue', 'darkslateblue', 'mediumslateblue', 'mediumpurple', 'rebeccapurple', 'blueviolet']
    color = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan','b','g','r','c','m','y','k']
    
    for i in cycle[4:50:step]:
    # for i in cycle[1::step]:        
        voltage = mod_data.iloc[charge_step_start[i-1] : charge_step_end[i-1],5]
        # voltage = voltage/1000 # if Voltage column is in mV
        
        capacity = mod_data.iloc[charge_step_start[i-1] : charge_step_end[i-1],8]
        capacity = capacity/(active_material_weight/1000)
        
        b = int(i/step)
        plt.plot(capacity,voltage, color=color[b],label="Cycle " + str(i) )
        plt.legend(loc='lower right', frameon=False, prop={'size': 8})
        
        voltage = mod_data.iloc[discharge_step_start[i-1] : discharge_step_end[i-1],5]
        # voltage = voltage/1000 # if Voltage column is in mV
        
        capacity = mod_data.iloc[discharge_step_start[i-1] : discharge_step_end[i-1],8]
        capacity = capacity/(active_material_weight/1000)
        
        plt.plot(capacity,voltage, color=color[b])
        
    plt.title(title + name, loc='center', fontsize=18, fontweight=0)
    plt.xlabel("Capacity (mAh/g)", fontname='Times New Roman', fontsize=12)
    plt.ylabel("Voltage (V)", fontname='Times New Roman', fontsize=12)
    
    # Plot scales for LFP
    plt.xlim(0,170) # for LFP
    plt.ylim(2,4) # for LFP
    
    # plt.xlim(0,4)  #temp
    
    
    # Plot scales for Graphite
    # plt.xlim(0,350) # for Graphite
    # plt.ylim(-0.1,2.25) # for Graphite
    
    # plt.show()
    plt.savefig(results_dir + name + '_2.png', dpi=300, bbox_inches="tight")
    # plt.savefig(name + '_2.png', dpi=300)
    plt.clf()
    
CapacityVsVoltage(data,name)
