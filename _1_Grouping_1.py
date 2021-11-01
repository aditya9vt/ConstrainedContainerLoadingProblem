import operator
import sys, csv
import random
import math
import time
import pandas as pd
import numpy as np
from numpy import arange
from itertools import combinations
import _1_Grouping_2 as G2

def Group1():    
    
    ########################################################### Read Data
    
    
    # 1 Read Input Data File
    File = pd.ExcelFile('CLPData_Parameters.xlsx')
    
    # Container Data    
    ContainerData = pd.read_excel(File, 'ContainerData')
    DiscargoBoxLimit = ContainerData['DisAggBoxLimit'][0]
    
    # Read Aggregates and Disaggregated Cargo Data
    CargoData = pd.read_excel(File, 'CargoData')
    AggOrders = CargoData['OrderNbr'].unique()
    
    DisCargoData = pd.read_excel(File, 'DisCargoData')
    
    DisOrders = DisCargoData['OrderNbr'].unique()
    TempCombDisOrders = []
    NumCombs = len(DisOrders) + 1
        
    for i in range(1,NumCombs):
        B = combinations(DisOrders,i)
        for j in list(B): 
            TempCombDisOrders.append(j)
    
    #Covert list (AllComb) of tuples to list (AllComb_List) of lists
    CombDisOrders = [list(elem) for elem in TempCombDisOrders]    
    #print(CombDisOrders)           
    
    AllSols = {}
    BestVolLoaded = 0
    BestSolNbr = -1
    
    start = time.time()
    if len(CombDisOrders) > 0:
        for d in range(len(CombDisOrders)):
            Functionality = 1
            set1 = CargoData[~CargoData['OrderNbr'].isin(CombDisOrders[d])]
            set1.reset_index(drop=True, inplace=True) 
            
            set2 = DisCargoData[DisCargoData['OrderNbr'].isin(CombDisOrders[d])]
            set2.reset_index(drop=True, inplace=True) 
            
            #set3 = set2.loc[set2['Weight'] == 20] # List of skids from CombDisOrders[d] that are not broken
            set3 = set2.loc[(set2['l'] >= 3) & (set2['w'] >= 3)] # List of skids from CombDisOrders[d] that are not broken
            set3.reset_index(drop=True, inplace=True) 
            
            set4 = set2[~set2.Sno.isin(set3.Sno)] # Filter set2 such that Sno of set2 are not in Sno of set3 (set2.Sno - set3.Sno)
            set4.reset_index(drop=True, inplace=True) 
            
            set5 = set1.append(set3, ignore_index=True)                
            set5.reset_index(drop=True, inplace=True)             
            
            if len(CombDisOrders[d]) >= 1 and set4.shape[0] <= DiscargoBoxLimit:
            # if len(CombDisOrders[d]) == 1 or set4.shape[0] <= DiscargoBoxLimit:
            # if set4.shape[0] <= 900:
            # if len(CombDisOrders[d]) == 1 and (int(CombDisOrders[d][0]) == 29193):   
            # if len(CombDisOrders[d]) == 2:   
                AllSols[d] = {}                
                FeasibilityFlag, LoadingPattern, LoadingVolume, TotalBoxesLoaded = G2.LoadCargoes1(set1, set2, set3, set4, set5, Functionality, CombDisOrders[d])
                AllSols[d][1] = CombDisOrders[d]
                AllSols[d][2] = FeasibilityFlag                
                AllSols[d][3] = LoadingPattern
                AllSols[d][4] = LoadingVolume
                AllSols[d][5] = TotalBoxesLoaded                
                
                if LoadingVolume > BestVolLoaded:
                    BestVolLoaded = LoadingVolume
                    BestSolNbr = d
    
    # print("Best Solution Series: "+str(CombDisOrders[BestSolNbr]))
    for l in range(len(AllSols)):
        SolNbr = list(AllSols.keys())[l]
        # print("Solution Nbr: "+str(SolNbr)+" with Volume: "+str(AllSols[SolNbr][3]))
    
    # print("Best Solution Nbr: "+str(BestSolNbr)+" with Volume: "+str(AllSols[BestSolNbr][3]))
    
    # input("Stop Compilation")
    return AllSols, BestSolNbr