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
def LoadCargoes1(set1, set2, set3, set4, set5, Functionality, ListDisOrders):
    print("Disaggregated Orders: "+str(ListDisOrders))
        
    ################### 1. Input Data
    
    # 1.1 Read Input Data File
    File = pd.ExcelFile('CLPData_Parameters.xlsx')
    
    # 1.2 Container Data    
    ContainerData = pd.read_excel(File, 'ContainerData')     
    DiscargoBoxLimit = ContainerData['DisAggBoxLimit'][0]
    VolLimit = ContainerData["VolLimit"][0]
    tryOptionA = ContainerData["LP_A"][0]
    tryOptionB = ContainerData["LP_B"][0]
    tryOptionC = ContainerData["LP_C"][0]

    # 1.3 Agg Cargo Data
    AggLevelCargoData = pd.read_excel(File, 'CargoData')
    
    ################### 2. Find orders from set1 (=Cargodata - Selected order from disCargoData) that can be loaded
    
    # 2.1 Solve a MIP    
    column_names = ["Key", "HeurOption", "CDOption", "Sno", "Wt", "x", "y", "z", "l", "w", "h"]
    FinalSol = pd.DataFrame(columns = column_names)  
                            
    column_names = ["Key", "HeurOption", "CDOption", "TotWt", "TotVol", "TotMargin", "TotSnoLoaded", "FeasibilityFlag", "OrdersInfeasible", "CountInfOrderNbr", "OrdersLoaded", "VolOrdersLoaded", "OrdersNotLoaded"]
    Summary_FinalSol = pd.DataFrame(columns = column_names)
    
    column_names = ['Key', 'HeurOption', 'CDOption', 'b','t','x_b','y_b','z_b','x_t','y_t','z_t','L_b','W_b','H_b','L_t','W_t','H_t','Wt_b','Wt_t','LOf_iOnj','WOf_iOnj','Wt_E']    
    dfOT_Final = pd.DataFrame(columns = column_names)
    
    CalledFrom = 0
    ReduceVol = sum(set2['Volume'])

    # 2.2 Prepare set1 data: Add  Potential Orientations Set
    set1['P'] = ''    
    for i in range(set1.shape[0]):
        if set1['l_flag'][i] == 1 and set1['w_flag'][i] == 1 and set1['h_flag'][i] == 1:
            set1['P'][i] = [1]
        elif set1['l_flag'][i] == 1 and set1['w_flag'][i] == 1 and set1['h_flag'][i] == 0:
            set1['P'][i] = [1]
        elif set1['l_flag'][i] == 1 and set1['w_flag'][i] == 0 and set1['h_flag'][i] == 0:
            set1['P'][i] = [1, 3]
        elif set1['l_flag'][i] == 0 and set1['w_flag'][i] == 1 and set1['h_flag'][i] == 1:
            set1['P'][i] = [1]
        elif set1['l_flag'][i] == 0 and set1['w_flag'][i] == 1 and set1['h_flag'][i] == 0:
            set1['P'][i] = [1, 2]
        elif set1['l_flag'][i] == 0 and set1['w_flag'][i] == 0 and set1['h_flag'][i] == 1:
            set1['P'][i] = [6, 1]
        elif set1['l_flag'][i] == 1 and set1['w_flag'][i] == 0 and set1['h_flag'][i] == 1:
            set1['P'][i] = [1]
        elif set1['l_flag'][i] == 0 and set1['w_flag'][i] == 0 and set1['h_flag'][i] == 0:
            set1['P'][i] = [1, 2, 3, 4, 5, 6]
    
    # 2.3.1 Select Orders using MIP and temporary loading to find out the orders that can be loaded
    for MipOption in range(0,6):
        
        IncludeOrders = SO.SolveMIP(set1, ContainerData, MipOption, ReduceVol, ListDisOrders)
        ID_Temp = set1[set1['OrderNbr'].isin(IncludeOrders)]
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
    
    # 2.4 Extend every list of ListOrdersLoaded only those skids from selected order from DisCargo that are not broken
    #     (These ar unique orders from set3)
    set3UniqueOrders = set3['OrderNbr'].unique()
    
    # 2.5 Append ListOrdersLoaded and set3Uniqueorders for every list obtained in step 2.3.1 and 2.3.2
    for l in range(len(ListOrdersLoaded)):
        ListOrdersLoaded[l].extend(set3UniqueOrders)
    
    # 2.6 Add the orders with must load option here, the way we have done set3UniqueOrders
    # First find mustload orders from set 1
    dfMustLoad = set1.groupby(['OrderNbr'], as_index=False).agg({'mustload':'sum'})
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
    #input("press enter")
    # input("stop compilation")
    
    ################### 3. Begin Heuristic to create feasible solution from lists in ListOrdersLoaded
    ################### The input data set for this step set5 (= set1 + list of Sno that corresponds to unbroken skids for selected disorders)
    
    # 3.1 Prepare set5 in correct input form
    # 3.1.1 Add Orientations
    set5['P'] = ''    
    for i in range(set5.shape[0]):
        if set5['l_flag'][i] == 1 and set5['w_flag'][i] == 1 and set5['h_flag'][i] == 1:
            set5['P'][i] = [1]
        elif set5['l_flag'][i] == 1 and set5['w_flag'][i] == 1 and set5['h_flag'][i] == 0:
            set5['P'][i] = [1]
        elif set5['l_flag'][i] == 1 and set5['w_flag'][i] == 0 and set5['h_flag'][i] == 0:
            set5['P'][i] = [1, 3]
        elif set5['l_flag'][i] == 0 and set5['w_flag'][i] == 1 and set5['h_flag'][i] == 1:
            set5['P'][i] = [1]
        elif set5['l_flag'][i] == 0 and set5['w_flag'][i] == 1 and set5['h_flag'][i] == 0:
            set5['P'][i] = [1, 2]
        elif set5['l_flag'][i] == 0 and set5['w_flag'][i] == 0 and set5['h_flag'][i] == 1:
            set5['P'][i] = [6, 1]
        elif set5['l_flag'][i] == 1 and set5['w_flag'][i] == 0 and set5['h_flag'][i] == 1:
            set5['P'][i] = [1]
        elif set5['l_flag'][i] == 0 and set5['w_flag'][i] == 0 and set5['h_flag'][i] == 0:
            set5['P'][i] = [6, 1, 2, 3, 4, 5]
    
    # 3.1.2 Prepare Aggregated InstData from set5
    Agg_InstData = set5.groupby(['OrderNbr'], as_index=False).agg({'SkidNbr':'count', 'Weight': 'sum', 'Volume': 'sum'})
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
    AllSols_DisOrder = {}
    AllSols_DisOrder_OrderNbrsOnly = {}
    Sol_Counter = 0
    TimeLimit = 3000
    column_names = ["DictSolKey", "Volume"]
    AllSols_DisOrder_Key = pd.DataFrame(columns = column_names)
    
    ####################################################### Start loading
    for l in range(len(ListOrdersLoaded)):

        if tryOptionA == 1:
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
                    dfIP = set5[set5['OrderNbr'].isin(COL)]            
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
                            BestSol_Volume = BestSol_Summary_TempFS['TotVol'][0]
    
                            Sol_Counter += 1
                            AllSols_DisOrder[Sol_Counter] = {} 
                            AllSols_DisOrder[Sol_Counter][1] = Sol_LHPart2
                            AllSols_DisOrder[Sol_Counter][2] = dfOT_LHPart2
                            AllSols_DisOrder[Sol_Counter][3] = CD_LHPart2
                            AllSols_DisOrder[Sol_Counter][4] = sum(Sol_LHPart2['Volume'])
                            UniqueOrderNbrs = Sol_LHPart2["OrderNbr"].unique()
                            UniqueOrderNbrs.sort()
                            AllSols_DisOrder_OrderNbrsOnly[Sol_Counter] = list(UniqueOrderNbrs)
                            # print(AllSols_DisOrder_OrderNbrsOnly)
                            # input("Stop")
                            data=[{"DictSolKey": Sol_Counter,'Volume': sum(Sol_LHPart2['Volume'])}]     
                            AllSols_DisOrder_Key = AllSols_DisOrder_Key.append(data,ignore_index=True)                        
                            # print("Key:" + str(Key)+"; SolNbr: "+str(Sol_Counter)+'; Vol: '+str(sum(Sol_LHPart2['Volume'])))                        
        
                    del Summary_TempFS
                    del COL      
                    end = time.time() 
                    time_Elapsed += end - start
                
            del dfRO
 
        if tryOptionB == 1:
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
                    dfIP = set5[set5['OrderNbr'].isin(COL)]            
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
                            BestSol_Volume = BestSol_Summary_TempFS['TotVol'][0]
    
                            Sol_Counter += 1
                            AllSols_DisOrder[Sol_Counter] = {} 
                            AllSols_DisOrder[Sol_Counter][1] = Sol_LHPart2
                            AllSols_DisOrder[Sol_Counter][2] = dfOT_LHPart2
                            AllSols_DisOrder[Sol_Counter][3] = CD_LHPart2
                            AllSols_DisOrder[Sol_Counter][4] = sum(Sol_LHPart2['Volume'])
                            UniqueOrderNbrs = Sol_LHPart2["OrderNbr"].unique()
                            UniqueOrderNbrs.sort()
                            AllSols_DisOrder_OrderNbrsOnly[Sol_Counter] = list(UniqueOrderNbrs)
                            
                            data=[{"DictSolKey": Sol_Counter,'Volume': sum(Sol_LHPart2['Volume'])}]     
                            AllSols_DisOrder_Key = AllSols_DisOrder_Key.append(data,ignore_index=True)                     
                            # print("Key:" + str(Key)+"; SolNbr: "+str(Sol_Counter)+'; Vol: '+str(sum(Sol_LHPart2['Volume'])))
    
                
                    del Summary_TempFS
                    del COL      
                    end = time.time() 
                    time_Elapsed += end - start
                
            del dfRO

        if tryOptionC == 1:
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
                    dfIP = set5[set5['OrderNbr'].isin(COL)]            
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
                            BestSol_Volume = BestSol_Summary_TempFS['TotVol'][0]
    
                            Sol_Counter += 1
                            AllSols_DisOrder[Sol_Counter] = {} 
                            AllSols_DisOrder[Sol_Counter][1] = Sol_LHPart2
                            AllSols_DisOrder[Sol_Counter][2] = dfOT_LHPart2
                            AllSols_DisOrder[Sol_Counter][3] = CD_LHPart2
                            AllSols_DisOrder[Sol_Counter][4] = sum(Sol_LHPart2['Volume'])
                            UniqueOrderNbrs = Sol_LHPart2["OrderNbr"].unique()
                            UniqueOrderNbrs.sort()
                            AllSols_DisOrder_OrderNbrsOnly[Sol_Counter] = list(UniqueOrderNbrs)
                            
                            data=[{"DictSolKey": Sol_Counter,'Volume': sum(Sol_LHPart2['Volume'])}]     
                            AllSols_DisOrder_Key = AllSols_DisOrder_Key.append(data,ignore_index=True)                     
                            # print("Key:" + str(Key)+"; SolNbr: "+str(Sol_Counter)+'; Vol: '+str(sum(Sol_LHPart2['Volume'])))
    
        
                    del Summary_TempFS
                    del COL      
                    end = time.time() 
                    time_Elapsed += end - start          
    
            del dfRO
    # print("All Keys")
    # print(AllSols_DisOrder_OrderNbrsOnly)
    
    # 4. For every feasible solution obtained so far, upload disaggregated cargoes
    # 4.1 Remove all duplicates solutions from 'AllSols_DisOrder_Key'
    # print("Sol Nbrs before removing duplicates: "+str(len(AllSols_DisOrder_OrderNbrsOnly)))
    Dict_UniqeusSolNbrs = {}
    
    for key,value in AllSols_DisOrder_OrderNbrsOnly.items():
        if value not in Dict_UniqeusSolNbrs.values():
            Dict_UniqeusSolNbrs[key] = value

    # print("Unique Keys")
    # print(list(Dict_UniqeusSolNbrs.keys()))
    
    List_UniqueSolNbr = list(Dict_UniqeusSolNbrs.keys())
    # input("Stop Compilation")
    
    # print("Sol Nbrs after removing duplicates: "+str(len(Dict_UniqeusSolNbrs)))
    
    # 4.2 Remove duplicate keys from AllSols_DisOrder_Key and arrange in decreasing order of Volume Loaded
    # print("Before removing duplicate keys")    
    AllSols_DisOrder_Key = AllSols_DisOrder_Key.sort_values(by=['Volume'], ascending=[False])
    AllSols_DisOrder_Key.reset_index(drop=True, inplace=True)    
    
    # print(AllSols_DisOrder_Key)
    # Remove duplicate solution nbrs
    AllSols_DisOrder_Key = AllSols_DisOrder_Key[AllSols_DisOrder_Key["DictSolKey"].isin(List_UniqueSolNbr)]
    # print(AllSols_DisOrder_Key)
    AllSols_DisOrder_Key = AllSols_DisOrder_Key.sort_values(by=['Volume'], ascending=[False])
    AllSols_DisOrder_Key.reset_index(drop=True, inplace=True)    
    
    # print("After removing duplicate keys")
    # print(AllSols_DisOrder_Key)

    # 4.3 Load Disaggregated Cargoes    
    column_names = ["Sno" "Wt" "x" "y" "z" "l" "w" "h" "WtLF	" "SAPer" "OrderNbr"]
    FinalFeasibleLoading = pd.DataFrame(columns = column_names)
    isFinalLoadingFeasible = 0
    LoadOnSolNbr = 0
    counter = 0
    TotalCargoesLoaded = 0
    counter_limit = AllSols_DisOrder_Key.shape[0]
    VolSet4 = sum(set4["Volume"])
    while isFinalLoadingFeasible == 0 and counter < counter_limit:
        
        TotalCargoesLoaded = 0
        LoadOnSolNbr = AllSols_DisOrder_Key["DictSolKey"][counter]        
        if AllSols_DisOrder[LoadOnSolNbr][4] + VolSet4 <= VolLimit:    
            # print("Checking SolNbr: "+str(LoadOnSolNbr)+" with initial volumne: "+str(AllSols_DisOrder[LoadOnSolNbr][4]))
            isFinalLoadingFeasible, FinalFeasibleLoading, dfCargoNotLoaded, TotalCargoesLoaded = LH2B.LoadCargoes(AllSols_DisOrder[LoadOnSolNbr][1], AllSols_DisOrder[LoadOnSolNbr][2], AllSols_DisOrder[LoadOnSolNbr][3], set4, ContainerData)
            # FinalFeasibleLoading.to_csv('FinalLoading_SolNbr='+str(LoadOnSolNbr)+'.csv', sep=',', encoding='utf-8', index = False)
            # if isFinalLoadingFeasible == 1:
                # print("Feasible Loading Obtained. End loading on lower vol solutions.")
                # print("bestSolNbr: "+str(LoadOnSolNbr))
                # print(FinalSol)
        
        counter += 1
        
    if isFinalLoadingFeasible == 1:        
        # 4.3 For the best solution obtained, find the total volume loaded
        # 4.3.1 Find Unique order nbrs in FinalSol
        OrdersFeasibleLoading = FinalFeasibleLoading.OrderNbr.unique()
        
        # 4.3.2 Find Volume for every order in AggCargoData
        All_Orders = AggLevelCargoData.groupby(['OrderNbr'], as_index=False).agg({'Volume':'sum'})
        Final_Orders = All_Orders[All_Orders['OrderNbr'].isin(OrdersFeasibleLoading)]
        VolumeFeasibleLoading = sum(Final_Orders["Volume"])
        print("Final Vol Loaded: "+str(VolumeFeasibleLoading))
    
    #input("Stop Compilation")
    
    return isFinalLoadingFeasible, FinalFeasibleLoading, VolumeFeasibleLoading, TotalCargoesLoaded