import operator
import sys, csv
import random
import math
import time
import pandas as pd
import numpy as np
from numpy import arange
import shutil
from pathlib import Path
import _1_LH_Part2_ByCoordinate as LHP2C
import _1_LH_Part2_ByBox as LHP2B
import _1_LH_2_ByBox as LH2B
import _6_SelectOrders as SO
import _7_LoadingHeuristic_ByBox as LHB
import _7_LoadingHeuristic_ByCoord as LHC
import copy
from itertools import combinations
import os, PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import statistics as st

#################################################################################################################
def LoadCargoes1():
        
    ################### 1. Input Data
    
    # 1.1 Read Input Data File
    File = pd.ExcelFile('CLPData_Parameters.xlsx')
    
    # 1.2 Container Data    
    ContainerData = pd.read_excel(File, 'ContainerData')     
    
    # 1.3 Agg Cargo Data
    CargoData = pd.read_excel(File, 'CargoData')
    
    ################### 2. Find orders from set1 (=Cargodata - Selected order from disCargoData) that can be loaded
    
    # 2.1 Solve a MIP    
    column_names = ["Key", "HeurOption", "CDOption", "Sno", "Wt", "x", "y", "z", "l", "w", "h"]
    FinalSol = pd.DataFrame(columns = column_names)  
                            
    column_names = ["Key", "HeurOption", "CDOption", "TotWt", "TotVol", "TotMargin", "TotSnoLoaded", "FeasibilityFlag", "OrdersInfeasible", "CountInfOrderNbr", "OrdersLoaded", "VolOrdersLoaded", "OrdersNotLoaded"]
    Summary_FinalSol = pd.DataFrame(columns = column_names)
    
    column_names = ['Key', 'HeurOption', 'CDOption', 'b','t','x_b','y_b','z_b','x_t','y_t','z_t','L_b','W_b','H_b','L_t','W_t','H_t','Wt_b','Wt_t','LOf_iOnj','WOf_iOnj','Wt_E']    
    dfOT_Final = pd.DataFrame(columns = column_names)
    
    CalledFrom = 0

    # 2.2 Prepare set1 data: Add  Potential Orientations Set
    CargoData['P'] = ''    
    for i in range(CargoData.shape[0]):
        if CargoData['l_flag'][i] == 1 and CargoData['w_flag'][i] == 1 and CargoData['h_flag'][i] == 1:
            CargoData['P'][i] = [1]
        elif CargoData['l_flag'][i] == 1 and CargoData['w_flag'][i] == 1 and CargoData['h_flag'][i] == 0:
            CargoData['P'][i] = [1]
        elif CargoData['l_flag'][i] == 1 and CargoData['w_flag'][i] == 0 and CargoData['h_flag'][i] == 0:
            CargoData['P'][i] = [1, 3]
        elif CargoData['l_flag'][i] == 0 and CargoData['w_flag'][i] == 1 and CargoData['h_flag'][i] == 1:
            CargoData['P'][i] = [1]
        elif CargoData['l_flag'][i] == 0 and CargoData['w_flag'][i] == 1 and CargoData['h_flag'][i] == 0:
            CargoData['P'][i] = [1, 2]
        elif CargoData['l_flag'][i] == 0 and CargoData['w_flag'][i] == 0 and CargoData['h_flag'][i] == 1:
            CargoData['P'][i] = [6, 1]
        elif CargoData['l_flag'][i] == 1 and CargoData['w_flag'][i] == 0 and CargoData['h_flag'][i] == 1:
            CargoData['P'][i] = [1]
        elif CargoData['l_flag'][i] == 0 and CargoData['w_flag'][i] == 0 and CargoData['h_flag'][i] == 0:
            CargoData['P'][i] = [1, 2, 3, 4, 5, 6]
    
    # 2.3.1 Select Orders using MIP and temporary loading to find out the orders that can be loaded
    ReduceVol = 0
    for MipOption in range(0,6):
        
        IncludeOrders = SO.SolveMIP(CargoData, ContainerData, MipOption, 0, 0)
        ID_Temp = CargoData[CargoData['OrderNbr'].isin(IncludeOrders)]
        Agg_ID_Temp = ID_Temp.groupby(['OrderNbr'], as_index=False).agg({'SkidNbr':'count'})
        Agg_ID_Temp.rename(columns={'SkidNbr':'SkidCount'}, inplace=True)
        ID_Temp = pd.merge(ID_Temp, Agg_ID_Temp, on=['OrderNbr'] , how='inner')
        
        for sm in range(0,2):
            
            if sm == 0:
                ID_Temp = ID_Temp.sort_values(by=['SkidCount', 'Weight'], ascending=[False,False]).reset_index()
            else:
                ID_Temp = ID_Temp.sort_values(by=['h'], ascending=[False]).reset_index()
  
            # This function tries to place cargoes and provides us a solution be it feasible or infeasible
            # Input 'ID_Temp = List of Sno to upload with the order'
            
            FinalSol_LHB, Summary_FinalSol_LHB, IsSolFeasible_LHB, dfOT_LHB = LHB.LoadCargoes(ID_Temp, ContainerData, CalledFrom)
            FinalSol = FinalSol.append(FinalSol_LHB, ignore_index=True)                 
            Summary_FinalSol = Summary_FinalSol.append(Summary_FinalSol_LHB, ignore_index=True)            
            dfOT_Final = dfOT_Final.append(dfOT_LHB, ignore_index=True)                             
     
            FinalSol["Key"].fillna(str(MipOption)+'_'+str(sm), inplace = True)
            Summary_FinalSol["Key"].fillna(str(MipOption)+'_'+str(sm), inplace = True)                  
            
            dfOT_Final["Key"].fillna(str(MipOption)+'_'+str(sm), inplace = True)                  
       
    # 2.3.2 Select Orders from Summary_FinalSol that are fully loaded and Remove duplicates
    FullOrdersLoaded = Summary_FinalSol['OrdersLoaded'].to_list()
    b_set = set(tuple(x) for x in FullOrdersLoaded) # Remove duplicates
    ListOrdersLoaded = [ list(x) for x in b_set ] # convert tuples to list
    #print(ListOrdersLoaded)
  
    # 2.4 Add the orders with must load option here, the way we have done set3UniqueOrders
    # First find mustload orders from set 1
    dfMustLoad = CargoData.groupby(['OrderNbr'], as_index=False).agg({'mustload':'sum'})
    dfMustLoad = dfMustLoad.loc[dfMustLoad['mustload'] >= 1]
    ListMustLoad = dfMustLoad['OrderNbr'].tolist()
    # print(ListMustLoad)
    
    #Convert pandas column to list
    #Extend each list with mustload orders
    for l in range(len(ListOrdersLoaded)):
        ListOrdersLoaded[l].extend(ListMustLoad)
    
    # print(ListOrdersLoaded)
    
    #Remove duplicated from each list in ListOrdersLoaded
    for l in range(len(ListOrdersLoaded)):
        templist = list(dict.fromkeys(ListOrdersLoaded[l]))    
        ListOrdersLoaded[l] = templist
    
    # input("Check ListOrdersLoaded and press enter")
    # print(ListOrdersLoaded)
    # input("press enter")
    # input("stop compilation")
    
    ################### 3. Begin Heuristic to create feasible solution from lists in ListOrdersLoaded
    
    # 3.1.2 Prepare Aggregated InstData from CargoData
    Agg_InstData = CargoData.groupby(['OrderNbr'], as_index=False).agg({'SkidNbr':'count', 'Weight': 'sum', 'Volume': 'sum'})
    Agg_InstData.rename(columns={'SkidNbr':'SkidCount'}, inplace=True)
    Agg_InstData['WtPerSkid'] = Agg_InstData['Weight']/Agg_InstData['SkidCount']
    Agg_InstData['VolPerSkid'] = Agg_InstData['Volume']/Agg_InstData['SkidCount']
    Agg_InstData['VolPerWt'] = Agg_InstData['Volume']/Agg_InstData['Weight']
    Agg_InstData = Agg_InstData.sort_values(by=['WtPerSkid'], ascending=[False])
    Agg_InstData.reset_index(drop=True, inplace=True)
    Agg_InstData['WtRanking'] = 0.0
    for i in range(len(Agg_InstData)):
        Agg_InstData['WtRanking'][i] = i + 1
    
    Agg_InstData = Agg_InstData.sort_values(by=['VolPerSkid'], ascending=[False])
    Agg_InstData.reset_index(drop=True, inplace=True)
    Agg_InstData['VolRanking'] = 0.0
    for i in range(len(Agg_InstData)):
        Agg_InstData['VolRanking'][i] = i + 1

    # 3.2 Begin loadings for each list belonging to ListOrdersLoaded
    column_names = ["Key", "HeurOption", "CDOption", "Sno", "Wt", "x", "y", "z", "l", "w", "h"]
    FeasSols = pd.DataFrame(columns = column_names)

    column_names = ['Key', 'HeurOption', 'CDOption', 'b','t','x_b','y_b','z_b','x_t','y_t','z_t','L_b','W_b','H_b','L_t','W_t','H_t','Wt_b','Wt_t','LOf_iOnj','WOf_iOnj','Wt_E']    
    FeasdfOT = pd.DataFrame(columns = column_names)
    
    FeasCD = {}
    
    CalledFrom = 1    
    BestList = []
    
    # Save every solution obtained after keeping DisAggregated Order out of first loading
    AllSols_AggOrder = {}
    Sol_Counter = 0
    TimeLimit = 3000
    
    ####################################################### Start loading
    for l in range(len(ListOrdersLoaded)):

        # +++++++++++++++++++++++++++++++++++ Sort Option A
        Key = str(l)+'_'+'A'
        CLOL = copy.deepcopy(ListOrdersLoaded[l])
        
        column_names = ["Key", "HeurOption", "CDOption", "Sno", "Wt", "x", "y", "z", "l", "w", "h"]
        BestSol = pd.DataFrame(columns = column_names)
        column_names = ['Key', 'HeurOption', 'CDOption', 'b','t','x_b','y_b','z_b','x_t','y_t','z_t','L_b','W_b','H_b','L_t','W_t','H_t','Wt_b','Wt_t','LOf_iOnj','WOf_iOnj','Wt_E']    
        BestdfOT = pd.DataFrame(columns = column_names)
        BestCD = []
        BestSol_Volume = 0
        
        dfRO = Agg_InstData[~Agg_InstData['OrderNbr'].isin(CLOL)]
        dfRO.sort_values(by=['VolPerSkid'], inplace=True, ascending=False)
        dfRO.reset_index(drop=True, inplace=True)        
        ListRO = dfRO['OrderNbr'].to_list()
        
        time_Elapsed = 0
        start = time.time()
        

        for f in range(len(ListRO)):
            
            if time_Elapsed <= 300:
                column_names = ["HeurOption", "CDOption", "TotWt", "TotVol", "TotMargin", "TotSnoLoaded", "FeasibilityFlag", "OrdersInfeasible", "CountInfOrderNbr", "OrdersLoaded", "VolOrdersLoaded", "OrdersNotLoaded"]
                Summary_TempFS = pd.DataFrame(columns = column_names)
                
                COL = []
                COL.extend(CLOL)
                COL.append(ListRO[f])
                
                #Create input dataframe with required order
                dfIP = CargoData[CargoData['OrderNbr'].isin(COL)]            
                dfIP = pd.merge(dfIP, Agg_InstData[['OrderNbr','WtRanking', 'VolRanking']], on=['OrderNbr'], how='left')  
                
                dfIP['Var'] = 0
                dfIP['SelFlag'] = 0
                # Separate dfIP into two sets: Set 1 consists of boxes with low variance in dimensions and set2 = dfIP - set1
                # Find out variance of each box                
                for i in range(dfIP.shape[0]):
                    TempList = [dfIP['l'][i], dfIP['w'][i], dfIP['h'][i]]
                    dfIP['Var'][i] = st.variance(TempList)                
                    if dfIP['l'][i] >= 3 and dfIP['l'][i] <= 5 and dfIP['w'][i] >= 3 and dfIP['w'][i] <= 4 and dfIP['h'][i] >= 3:
                        dfIP['SelFlag'][i] = 1
                #Create dfIPset1 and dfIPset2
                dfIPset1 = dfIP.loc[dfIP["Var"] <= 1]
                #dfIPset1 = dfIP.loc[dfIP["SelFlag"] == 1]                
                # dfIPset1.to_csv('dfIPset1.csv', sep=',', encoding='utf-8', index = False)
                dfIPset2 = dfIP[~dfIP.Sno.isin(dfIPset1.Sno)]
                
                # First, load cargoes that belongs to dfIPset1
                dfIPset1.sort_values(by=['h'], inplace=True, ascending=[False])
                dfIPset1.reset_index(drop=True, inplace=True)                
                Sol_LHPart1, Summary_Sol_LHPart1, IsFeasible_LHPart1, dfOT_LHPart1, CD_LHPart1 = LHC.LoadCargoes(dfIPset1, ContainerData, CalledFrom)
                Summary_TempFS = Summary_TempFS.append(Summary_Sol_LHPart1, ignore_index=True)             
                Summary_TempFS.sort_values(by=['FeasibilityFlag','TotVol'], inplace=True, ascending=[False, False])
                Summary_TempFS.reset_index(drop=True, inplace=True)
                BestSol_Summary_TempFS = Summary_TempFS.head(1)

                # Second, if the solution from first part is feasible then load cargoes that belongs to dfIPset2
                if IsFeasible_LHPart1 == 1:
                    dfIPset2.sort_values(by=['h'], inplace=True, ascending=[False])
                    dfIPset2.reset_index(drop=True, inplace=True)                
                    Sol_LHPart2, IsFeasible_LHPart2, dfOT_LHPart2, CD_LHPart2 = LHP2B.LoadCargoes(dfIPset2, ContainerData, Sol_LHPart1, dfOT_LHPart1, CD_LHPart1)    
                    #input("Check CD_LHPart2")
                    
                #Save feasible solution
                if IsFeasible_LHPart2 == 1:                    
                   
                   if sum(Sol_LHPart2['Volume']) > BestSol_Volume:               
 
                        # Update Current ListOrdersLoaded
                        CLOL.append(ListRO[f])
                        BestSol_Volume = sum(Sol_LHPart2['Volume'])
                        
                        # Update Best Feasible Solution
                        BestSol = Sol_LHPart2
                        BestdfOT = dfOT_LHPart2
                        BestCD = copy.deepcopy(CD_LHPart2)

                del Summary_TempFS
                del COL      
                end = time.time() 
                time_Elapsed += end - start
        
        if BestSol.shape[0] > 0:
            Sol_Counter += 1
            AllSols_AggOrder[Sol_Counter] = {} 
            AllSols_AggOrder[Sol_Counter][1] = BestSol
            AllSols_AggOrder[Sol_Counter][2] = BestdfOT
            AllSols_AggOrder[Sol_Counter][3] = BestCD
            AllSols_AggOrder[Sol_Counter][4] = BestSol_Volume
            # print("Key:" + str(Key)+"; SolNbr: "+str(Sol_Counter)+'; Vol: '+str(BestSol_Volume))                        
        # else:
            # print("Key:" + str(Key)+": No feasible solution")
            
        del dfRO
       
        # +++++++++++++++++++++++++++++++++++ Sort Option B
        Key = str(l)+'_'+'B'
        CLOL = copy.deepcopy(ListOrdersLoaded[l])
        
        column_names = ["Key", "HeurOption", "CDOption", "Sno", "Wt", "x", "y", "z", "l", "w", "h"]
        BestSol = pd.DataFrame(columns = column_names)
        column_names = ['Key', 'HeurOption', 'CDOption', 'b','t','x_b','y_b','z_b','x_t','y_t','z_t','L_b','W_b','H_b','L_t','W_t','H_t','Wt_b','Wt_t','LOf_iOnj','WOf_iOnj','Wt_E']    
        BestdfOT = pd.DataFrame(columns = column_names)
        BestCD = []
        BestSol_Volume = 0
        
        dfRO = Agg_InstData[~Agg_InstData['OrderNbr'].isin(CLOL)]
        dfRO.sort_values(by=['Weight'], inplace=True, ascending=False)
        dfRO.reset_index(drop=True, inplace=True)        
        ListRO = dfRO['OrderNbr'].to_list()
        
        time_Elapsed = 0
        start = time.time()
        

        for f in range(len(ListRO)):
            
            if time_Elapsed <= 300:
                column_names = ["HeurOption", "CDOption", "TotWt", "TotVol", "TotMargin", "TotSnoLoaded", "FeasibilityFlag", "OrdersInfeasible", "CountInfOrderNbr", "OrdersLoaded", "VolOrdersLoaded", "OrdersNotLoaded"]
                Summary_TempFS = pd.DataFrame(columns = column_names)
                
                COL = []
                COL.extend(CLOL)
                COL.append(ListRO[f])
                
                #Create input dataframe with required order
                dfIP = CargoData[CargoData['OrderNbr'].isin(COL)]            
                dfIP = pd.merge(dfIP, Agg_InstData[['OrderNbr','WtRanking', 'VolRanking']], on=['OrderNbr'], how='left')  
                
                dfIP['Var'] = 0
                dfIP['SelFlag'] = 0
                # Separate dfIP into two sets: Set 1 consists of boxes with low variance in dimensions and set2 = dfIP - set1
                # Find out variance of each box                
                for i in range(dfIP.shape[0]):
                    TempList = [dfIP['l'][i], dfIP['w'][i], dfIP['h'][i]]
                    dfIP['Var'][i] = st.variance(TempList)                
                    if dfIP['l'][i] >= 3 and dfIP['l'][i] <= 5 and dfIP['w'][i] >= 3 and dfIP['w'][i] <= 4 and dfIP['h'][i] >= 3:
                        dfIP['SelFlag'][i] = 1
                #Create dfIPset1 and dfIPset2
                dfIPset1 = dfIP.loc[dfIP["Var"] <= 1]
                #dfIPset1 = dfIP.loc[dfIP["SelFlag"] == 1]                
                # dfIPset1.to_csv('dfIPset1.csv', sep=',', encoding='utf-8', index = False)
                dfIPset2 = dfIP[~dfIP.Sno.isin(dfIPset1.Sno)]
                
                # First, load cargoes that belongs to dfIPset1
                dfIPset1.sort_values(by=['Weight'], inplace=True, ascending=[False])
                dfIPset1.reset_index(drop=True, inplace=True)                
                Sol_LHPart1, Summary_Sol_LHPart1, IsFeasible_LHPart1, dfOT_LHPart1, CD_LHPart1 = LHC.LoadCargoes(dfIPset1, ContainerData, CalledFrom)
                Summary_TempFS = Summary_TempFS.append(Summary_Sol_LHPart1, ignore_index=True)             
                Summary_TempFS.sort_values(by=['FeasibilityFlag','TotVol'], inplace=True, ascending=[False, False])
                Summary_TempFS.reset_index(drop=True, inplace=True)
                BestSol_Summary_TempFS = Summary_TempFS.head(1)

                # Second, if the solution from first part is feasible then load cargoes that belongs to dfIPset2
                if IsFeasible_LHPart1 == 1:
                    dfIPset2.sort_values(by=['Weight'], inplace=True, ascending=[False])
                    dfIPset2.reset_index(drop=True, inplace=True)                
                    Sol_LHPart2, IsFeasible_LHPart2, dfOT_LHPart2, CD_LHPart2 = LHP2B.LoadCargoes(dfIPset2, ContainerData, Sol_LHPart1, dfOT_LHPart1, CD_LHPart1)    
                    #input("Check CD_LHPart2")
                    
                #Save feasible solution
                if IsFeasible_LHPart2 == 1:
                   if sum(Sol_LHPart2['Volume']) > BestSol_Volume:                        
  
                        # Update Current ListOrdersLoaded
                        CLOL.append(ListRO[f])
                        BestSol_Volume = sum(Sol_LHPart2['Volume'])

                        # Update Best Feasible Solution
                        BestSol = Sol_LHPart2
                        BestdfOT = dfOT_LHPart2
                        BestCD = copy.deepcopy(CD_LHPart2)
            
                del Summary_TempFS
                del COL      
                end = time.time() 
                time_Elapsed += end - start
            
        if BestSol.shape[0] > 0:
            Sol_Counter += 1
            AllSols_AggOrder[Sol_Counter] = {} 
            AllSols_AggOrder[Sol_Counter][1] = BestSol
            AllSols_AggOrder[Sol_Counter][2] = BestdfOT
            AllSols_AggOrder[Sol_Counter][3] = BestCD
            AllSols_AggOrder[Sol_Counter][4] = BestSol_Volume
            # print("Key:" + str(Key)+"; SolNbr: "+str(Sol_Counter)+'; Vol: '+str(BestSol_Volume))                        
        # else:
        #     print("Key:" + str(Key)+": No feasible solution")

        del dfRO
 
        # +++++++++++++++++++++++++++++++++++ Sort Option C
        Key = str(l)+'_'+'C'
        CLOL = copy.deepcopy(ListOrdersLoaded[l])
        
        column_names = ["Key", "HeurOption", "CDOption", "Sno", "Wt", "x", "y", "z", "l", "w", "h"]
        BestSol = pd.DataFrame(columns = column_names)
        column_names = ['Key', 'HeurOption', 'CDOption', 'b','t','x_b','y_b','z_b','x_t','y_t','z_t','L_b','W_b','H_b','L_t','W_t','H_t','Wt_b','Wt_t','LOf_iOnj','WOf_iOnj','Wt_E']    
        BestdfOT = pd.DataFrame(columns = column_names)
        BestCD = []
        BestSol_Volume = 0
        
        dfRO = Agg_InstData[~Agg_InstData['OrderNbr'].isin(CLOL)]
        dfRO.sort_values(by=['Weight'], inplace=True, ascending=False)
        dfRO.reset_index(drop=True, inplace=True)        
        ListRO = dfRO['OrderNbr'].to_list()
        
        time_Elapsed = 0
        start = time.time()
        

        for f in range(len(ListRO)):
            
            if time_Elapsed <= 300:
                column_names = ["HeurOption", "CDOption", "TotWt", "TotVol", "TotMargin", "TotSnoLoaded", "FeasibilityFlag", "OrdersInfeasible", "CountInfOrderNbr", "OrdersLoaded", "VolOrdersLoaded", "OrdersNotLoaded"]
                Summary_TempFS = pd.DataFrame(columns = column_names)
                
                COL = []
                COL.extend(CLOL)
                COL.append(ListRO[f])
                
                #Create input dataframe with required order
                dfIP = CargoData[CargoData['OrderNbr'].isin(COL)]            
                dfIP = pd.merge(dfIP, Agg_InstData[['OrderNbr','WtRanking', 'VolRanking']], on=['OrderNbr'], how='left')  
                
                dfIP['SA'] = 0
                dfIP['Var'] = 0
                dfIP['SelFlag'] = 0
                # Separate dfIP into two sets: Set 1 consists of boxes with low variance in dimensions and set2 = dfIP - set1
                # Find out variance of each box                
                for i in range(dfIP.shape[0]):
                    dfIP['SA'][i] = dfIP['l'][i] * dfIP['w'][i]
                    TempList = [dfIP['l'][i], dfIP['w'][i], dfIP['h'][i]]
                    dfIP['Var'][i] = st.variance(TempList)                
                    if dfIP['l'][i] >= 3 and dfIP['l'][i] <= 5 and dfIP['w'][i] >= 3 and dfIP['w'][i] <= 4 and dfIP['h'][i] >= 3:
                        dfIP['SelFlag'][i] = 1
                #Create dfIPset1 and dfIPset2
                dfIPset1 = dfIP.loc[dfIP["Var"] <= 1]
                #dfIPset1 = dfIP.loc[dfIP["SelFlag"] == 1]                
                # dfIPset1.to_csv('dfIPset1.csv', sep=',', encoding='utf-8', index = False)
                dfIPset2 = dfIP[~dfIP.Sno.isin(dfIPset1.Sno)]
                
                # First, load cargoes that belongs to dfIPset1
                dfIPset1.sort_values(by=['SA'], inplace=True, ascending=[False])
                dfIPset1.reset_index(drop=True, inplace=True)                
                Sol_LHPart1, Summary_Sol_LHPart1, IsFeasible_LHPart1, dfOT_LHPart1, CD_LHPart1 = LHC.LoadCargoes(dfIPset1, ContainerData, CalledFrom)
                Summary_TempFS = Summary_TempFS.append(Summary_Sol_LHPart1, ignore_index=True)             
                Summary_TempFS.sort_values(by=['FeasibilityFlag','TotVol'], inplace=True, ascending=[False, False])
                Summary_TempFS.reset_index(drop=True, inplace=True)
                BestSol_Summary_TempFS = Summary_TempFS.head(1)

                # Second, if the solution from first part is feasible then load cargoes that belongs to dfIPset2
                if IsFeasible_LHPart1 == 1:
                    dfIPset2.sort_values(by=['Weight'], inplace=True, ascending=[False])
                    dfIPset2.reset_index(drop=True, inplace=True)                
                    Sol_LHPart2, IsFeasible_LHPart2, dfOT_LHPart2, CD_LHPart2 = LHP2B.LoadCargoes(dfIPset2, ContainerData, Sol_LHPart1, dfOT_LHPart1, CD_LHPart1)    
                    #input("Check CD_LHPart2")
                    
                #Save feasible solution
                if IsFeasible_LHPart2 == 1:
                   if sum(Sol_LHPart2['Volume']) > BestSol_Volume:                        
  
                        # Update Current ListOrdersLoaded
                        CLOL.append(ListRO[f])
                        BestSol_Volume = sum(Sol_LHPart2['Volume'])

                        # Update Best Feasible Solution
                        BestSol = Sol_LHPart2
                        BestdfOT = dfOT_LHPart2
                        BestCD = copy.deepcopy(CD_LHPart2)
    
                del Summary_TempFS
                del COL      
                end = time.time() 
                time_Elapsed += end - start          

        if BestSol.shape[0] > 0:
            Sol_Counter += 1
            AllSols_AggOrder[Sol_Counter] = {} 
            AllSols_AggOrder[Sol_Counter][1] = BestSol
            AllSols_AggOrder[Sol_Counter][2] = BestdfOT
            AllSols_AggOrder[Sol_Counter][3] = BestCD
            AllSols_AggOrder[Sol_Counter][4] = BestSol_Volume
        #     print("Key:" + str(Key)+"; SolNbr: "+str(Sol_Counter)+'; Vol: '+str(BestSol_Volume))                        
        # else:
        #     print("Key:" + str(Key)+": No feasible solution")

        del dfRO
    
    return AllSols_AggOrder