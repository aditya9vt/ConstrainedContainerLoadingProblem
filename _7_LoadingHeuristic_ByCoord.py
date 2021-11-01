import operator
import sys, csv
import random
import math
import time
import pandas as pd
import numpy as np
from numpy import arange
import _3_AdditionalFunctions as AF
import _4_Plots3D2 as Plot2
import shutil
from pathlib import Path
import _5_BoxbyBox_Plotting as CP
#Requires the “PyPDF2” and “OS” modules to be imported
import os, PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger

def LoadCargoes(ID_Reduced, ContainerData, CalledFrom):    
    
    ########################################################### INITIALIZATIONS COMMON FOR ALL CDOptions
    
    
    if CalledFrom == 0:
        CDOption_LL = 3
        CDOption_UL = 5
    else:
        CDOption_LL = 3
        CDOption_UL = 4
        
    ConstHeurSolFeasibile = 1
    
    column_names = ["HeurOption", "CDOption", "Sno", "Wt", "x", "y", "z", "l", "w", "h"]
    FinalSol = pd.DataFrame(columns = column_names)    
        
    column_names = ["HeurOption", "CDOption", "TotWt", "TotVol", "TotMargin", "TotSnoLoaded", "FeasibilityFlag", "OrdersInfeasible", "CountInfOrderNbr", "OrdersLoaded", "VolOrdersLoaded","OrdersNotLoaded"]
    Summary_FinalSol = pd.DataFrame(columns = column_names)
    
    column_names = ['HeurOption', 'CDOption', 'b','t','x_b','y_b','z_b','x_t','y_t','z_t','L_b','W_b','H_b','L_t','W_t','H_t','Wt_b','Wt_t','LOf_iOnj','WOf_iOnj','Wt_E']    
    dfOT_Final = pd.DataFrame(columns = column_names)

    Agg_ID_Reduced = ID_Reduced.groupby(['OrderNbr'], as_index=False).agg({'SkidNbr':'count'})
    
    CDRemoved = []
    CDAvail_Final = []
    
    for CDOption in range(CDOption_LL,CDOption_UL):
        
        ########################################################### INITIALIZATIONS for every CDOption
        
        
        column_names = ["HeurOption", "CDOption", "Sno", "Wt", "x", "y", "z", "l", "w", "h"]        
        FinalSol_Temp = pd.DataFrame(columns = column_names)   

        CargoLoaded_Nbr = [] # List of the cargoes that are already loaded
        CargoLoaded_L = [] # List of the length of each cargo inside the container
        CargoLoaded_W = [] # List of the width of each cargo inside the container
        CargoLoaded_H = [] # List of the height of each cargo inside the container
        CargoLoaded_x = [] # List of the x-coordinate of each cargo inside the container
        CargoLoaded_y = [] # List of the y-coordinate of each cargo inside the container
        CargoLoaded_z = [] # List of the z-coordinate of each cargo inside the container
        CargoLoaded_Wt = [] # List of the weight of each cargo inside the container
        CargoLoaded_Or = [] # List of the orientation of each cargo inside the container
        WeightLoaded = 0 # It will tell how much is loaded so far   
        CargoLoaded_WtLF  = []
        CargoLoaded_SAPer = []
        
        # Extract container data
        ContainerWeight = ContainerData['Wt'][0]        
        ContainerL = ContainerData['L'][0]
        ContainerW = ContainerData['W'][0]
        ContainerH = ContainerData['H'][0]
        L1, L2, L3 = ContainerData['Len_Axle1'][0], ContainerData['Len_Axle2'][0], ContainerData['Len_Axle3'][0]
        ContainerVolume = ContainerL*ContainerW*ContainerH
        ExtWtP1, ExtWtP2, ExtWtP3 = 0.0, 0.0, 0.0
        WtLimitP1, WtLimitP2, WtLimitP3 = ContainerData['Wt_Axle1'][0], ContainerData['Wt_Axle2'][0], ContainerData['Wt_Axle3'][0]
        GapFactor_Container, GapFactor_Cargo = 0.25, 0.10
        
        # Initialize CDAvail = origin and starting coordinates of Axle 2 and 3
        CDAvail = [(0,0,0),(L1,0,0),(L1+L2,0,0)]        
        FeasibilityFlag = 0      
        
        
        ########################################################### BEGIN EVALUATION   
    
        
        column_names = ['HeurOption', 'CDOption', 'b','t','x_b','y_b','z_b','x_t','y_t','z_t','L_b','W_b','H_b','L_t','W_t','H_t','Wt_b','Wt_t','LOf_iOnj','WOf_iOnj','Wt_E']    
        dfOT = pd.DataFrame(columns = column_names)
    
        # Initialize of list of available cargoes
        CargoRem = []
        CargoWt  = []
        CargoL   = []
        CargoW   = []
        CargoH   = []
        CargoP   = []
        CargoWtLimitFactor = []
        CargoSA_perc = []
        
        CargoRem = ID_Reduced['Sno'].to_list()
        CargoWt  = ID_Reduced['Weight'].to_list()
        CargoVol = ID_Reduced['Volume'].to_list()
        CargoL   = ID_Reduced['l'].to_list()
        CargoW   = ID_Reduced['w'].to_list()
        CargoH   = ID_Reduced['h'].to_list()
        CargoP   = ID_Reduced['P'].to_list()
        CargoWtLimitFactor = ID_Reduced['WtLF'].to_list()
        CargoSA_perc = ID_Reduced['SA_perc'].to_list()
        
        # Declare and define required constants and lists
        IsCargoPlaced = 1 # 1: yes a cargo is placed in this iteration
        WeightLoaded = 0.0
        TotalRecords = len(CargoRem)
        IsCDRemoved = 1
        
        while IsCargoPlaced == 1 or IsCDRemoved == 1:         
            
            IsCargoPlaced, IsCDRemoved = 0, 0

            # Next scan over each coordinate to find the right placement for cargo i but before that sort the coordinates according to CDOption
            if CDOption == 1:
                CDAvail = sorted(CDAvail, key=lambda element: (element[2], element[0], element[1]))                        
            elif CDOption == 2:
                CDAvail = sorted(CDAvail, key=lambda element: (element[2], element[1], element[0]))                         
            elif CDOption == 3:
                CDAvail = sorted(CDAvail, key=lambda element: (element[0], element[1], element[2]))
            elif CDOption == 4:
                CDAvail = sorted(CDAvail, key=lambda element: (element[0], element[2], element[1]))
            elif CDOption == 5:
                CDAvail = sorted(CDAvail, key=lambda element: (element[1], element[0], element[2]))
            elif CDOption == 6:
                CDAvail = sorted(CDAvail, key=lambda element: (element[1], element[2], element[0]))
            elif CDOption == 7:
                CDAvail = sorted(CDAvail, key=lambda element: (-element[0], element[1], element[2]))
            elif CDOption == 8:
                CDAvail = sorted(CDAvail, key=lambda element: (-element[0], element[2], element[1]))  
            
            for c in range(len(CDAvail)):
                ca = CDAvail[c]                            
                
                for i in range(len(CargoRem)):        
                    SkipRemainingItems = 0
                    cargo = CargoRem[i]                    
                    cargoweight = CargoWt[i]
                    if WeightLoaded + cargoweight <= ContainerWeight:            
         
                        l_hat, w_hat, h_hat = 0.0, 0.0, 0.0
                        for p in range(len(CargoP[i])):
                            l_hat, w_hat, h_hat = AF.TempDim_Function(p, i, CargoP, CargoL, CargoW, CargoH)                    
                            SkipRemainingOrientations = 0 
                        
                            
                            NoOverlapFlag = 1 
                            NoOverlapFlag_1 = 1 # For testing i wrt j
                            NoOverlapFlag_2 = 1 # For testing j wrt i

                            for j in range(len(CargoLoaded_Nbr)):
                                NoOverlapFlag_1, NoOverlapFlag_2 = AF.PF_Func(cargo, j, l_hat, w_hat, h_hat, ca, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H)                        
                                if NoOverlapFlag_1 == 0 and NoOverlapFlag_2 == 0:
                                    NoOverlapFlag = 0
                                    break                                        
                            
                            if NoOverlapFlag == 1:
                                SufficientDimFlag = 0 
                                SufficientDimFlag = AF.SuffDim_Function(l_hat, w_hat, h_hat, ca, ContainerL, ContainerW, ContainerH)                            
                                
                                if SufficientDimFlag == 1:
                                    
                                    WtDistMetFlag, WtP1, WtP2, WtP3 = 1, 0.0, 0.0, 0.0
                                    WtDistMetFlag, WtP1, WtP2, WtP3 = AF.WtDistribution(i, ca, cargo, l_hat, w_hat, h_hat, L1, L2, L3, ExtWtP1, ExtWtP2, ExtWtP3, WtLimitP1, WtLimitP2, WtLimitP3, cargoweight)
                                    
                                    if WtDistMetFlag == 1:
                                        
                                        WtLimitExceedFlag = 0
                                        WtLimitExceedFlag, dfOT = AF.WeightConstraints(i, ca, cargo, cargoweight, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr, dfOT, CargoWtLimitFactor[i], CargoLoaded_WtLF)
                                        
                                        if WtLimitExceedFlag == 0:
                                            
                                            SuffSupportAreaFlag = 1
                                            SuffSupportAreaFlag = AF.SupArea_Function(i, ca, cargo, cargoweight, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr, CargoSA_perc[i])
                                        
                                            if SuffSupportAreaFlag == 1:
                                                
                                                # CARGO i IS PLACED
                                                
                                                #Update weight on truck
                                                WeightLoaded = WeightLoaded + cargoweight
                                            
                                                # Update Weight on each axle
                                                ExtWtP1 = ExtWtP1 + WtP1
                                                ExtWtP2 = ExtWtP2 + WtP2
                                                ExtWtP3 = ExtWtP3 + WtP3
                                                
                                                # Set flags to move to next cargo
                                                IsCargoPlaced = 1
                                                SkipRemainingItems = 1 # Skip further explorations of items
                                                SkipRemainingOrientations = 1 # Skip further explorations of orientations
                                                
                                                #Create practical z-coordinate so that a package does not hang in the air
                                                z_Front, z_Side = 0.0, 0.0
                                                z_Front, z_Side = AF.Practical_zCoord(i, ca, cargo, cargoweight, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr)
                                                # 7 Create new positions as per the placement of recent cargo and add them to CDAvail
                                                # CDAvail.append(tuple((ca[0] + l_hat, ca[1], ca[2]))) # Create point with x-axis update
                                                # CDAvail.append(tuple((ca[0], ca[1] + w_hat, ca[2]))) # Create point with x-axis update
                                                # CDAvail.append(tuple((ca[0], ca[1], ca[2] + h_hat))) # Create point with x-axis update
                                                CDAvail.append(tuple((ca[0] + l_hat, ca[1], z_Front))) # Create point with x-axis update
                                                CDAvail.append(tuple((ca[0], ca[1] + w_hat, z_Side))) # Create point with x-axis update
                                                CDAvail.append(tuple((ca[0], ca[1], ca[2] + h_hat))) # Create point with x-axis update
                                                if ca[2] == 0 and ca[1] > 0:
                                                    Additional_y = AF.AdditionalYCoord(ca, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr)
                                                    CDAvail.append(tuple((ca[0] + l_hat, Additional_y, 0))) # Create point with x-axis update
                                                if ca[2] == 0 and ca[0] > 0:
                                                    Additional_x = AF.AdditionalXCoord(ca, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr)
                                                    CDAvail.append(tuple((Additional_x, ca[1] + w_hat, 0))) # Create point with x-axis update
                                                
                                                Additional_z = AF.AdditionalZCoord(ca, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr)
                                                CDAvail.extend(Additional_z)
                                                CDAvail = list(dict.fromkeys(CDAvail))
                                                    
                                                # Append to the following:
                                                CargoLoaded_Nbr.append(cargo)
                                                CargoLoaded_x.append(ca[0])
                                                CargoLoaded_y.append(ca[1])
                                                CargoLoaded_z.append(ca[2])
                                                CargoLoaded_L.append(l_hat)
                                                CargoLoaded_W.append(w_hat)
                                                CargoLoaded_H.append(h_hat)
                                                CargoLoaded_Wt.append(CargoWt[i])
                                                CargoLoaded_WtLF.append(CargoWtLimitFactor[i])
                                                CargoLoaded_SAPer.append(CargoSA_perc[i])
                     
                                                # Delete from the following:
                                                del CDAvail[c]
                                                del CargoRem[i]
                                                del CargoWt[i]
                                                del CargoVol[i]
                                                del CargoL[i]
                                                del CargoW[i]
                                                del CargoH[i]
                                                del CargoP[i]                                
                                                del CargoWtLimitFactor[i]
                                                del CargoSA_perc[i]     
                                            
                                            else:
                                                # dfOT.to_csv('dfOTBefore2.csv', sep=',', encoding='utf-8', index = False)
                                                # print("ca: "+str(ca))
                                                # print("Cargo Nbr: "+str(cargo)+"; Or: "+str(l_hat)+", "+str(w_hat)+", "+str(h_hat))
                                                dfOT = dfOT[~(dfOT["t"] == cargo)]
                                                # dfOT.to_csv('dfOTAfter.csv', sep=',', encoding='utf-8', index = False)
                                                # input("Remove Last dfOT")                                                

                            if SkipRemainingOrientations == 1:
                                break                                        
                    if SkipRemainingItems == 1:
                        break       
                # If any cargo is placed from CargoRem then stop inner while loop by setting i > limit 
                if IsCargoPlaced == 1:
                    break
                else:
                    CDRemoved.append(CDAvail[c])
                    del CDAvail[c]
                    IsCDRemoved = 1
                    break
                
        #Prepare CDAvail_Final
        if len(CDAvail) > 0:
            for l in range(len(CDAvail)):
                CDAvail_Final.append(CDAvail[l])
        if len(CDRemoved) > 0:
            for l in range(len(CDRemoved)):
                CDAvail_Final.append(CDRemoved[l])
                
                
        #Prepare dfOT_Final
        dfOT["CDOption"].fillna(CDOption, inplace = True) 
        dfOT["HeurOption"].fillna("LHC", inplace = True) 
        dfOT_Final = dfOT_Final.append(dfOT, ignore_index=True)                 

         # Prepare FinalSol
        FinalSol_Temp['Sno']      = CargoLoaded_Nbr
        FinalSol_Temp['Wt']       = CargoLoaded_Wt
        FinalSol_Temp['x']        = CargoLoaded_x
        FinalSol_Temp['y']        = CargoLoaded_y
        FinalSol_Temp['z']        = CargoLoaded_z
        FinalSol_Temp['l']        = CargoLoaded_L
        FinalSol_Temp['w']        = CargoLoaded_W
        FinalSol_Temp['h']        = CargoLoaded_H        
        FinalSol_Temp = pd.merge(FinalSol_Temp, ID_Reduced[['Sno','OrderNbr','Volume', 'Margin', 'WtLF', 'SA_perc']], on=['Sno'], how='left')        
        FinalSol_Temp.rename(columns={'SA_perc':'SAPer'}, inplace=True)
        FinalSol_Temp["CDOption"].fillna(CDOption, inplace = True) 
        FinalSol_Temp["HeurOption"].fillna("LHC", inplace = True) 
        FinalSol = FinalSol.append(FinalSol_Temp, ignore_index=True)                         
                                  
        # Prepare Summary_FinalSol
        VolOrdersLoaded = 0.0
        OrdersInfeasible, OrdersNotLoaded, OrdersLoaded = [], [], []
        Agg_FinalSol_Temp = FinalSol_Temp.groupby(['OrderNbr'], as_index=False).agg({'Sno':'count', 'Volume':'sum'})
        Agg_FinalSol_Temp.rename(columns={'Sno':'SkidCount'}, inplace=True)
        Agg_FinalSol_Temp = pd.merge(Agg_ID_Reduced, Agg_FinalSol_Temp[['OrderNbr','SkidCount', 'Volume']], on=['OrderNbr'], how='left')
        
        for i in range(Agg_FinalSol_Temp.shape[0]):
            if math.isnan(Agg_FinalSol_Temp['SkidCount'][i]):
                OrdersNotLoaded.append(Agg_FinalSol_Temp['OrderNbr'][i])
            else:
                if(Agg_FinalSol_Temp['SkidNbr'][i] != Agg_FinalSol_Temp['SkidCount'][i]):
                    OrdersInfeasible.append(Agg_FinalSol_Temp['OrderNbr'][i])
                else:
                    OrdersLoaded.append(Agg_FinalSol_Temp['OrderNbr'][i])
                    VolOrdersLoaded += Agg_FinalSol_Temp['Volume'][i]
                    
        if len(OrdersInfeasible) > 0:
            FeasibilityFlag = 0
        else:
            FeasibilityFlag = 1
            
        TotWt        = sum(FinalSol_Temp['Wt'])
        TotVol       = sum(FinalSol_Temp['Volume'])
        TotMargin    = sum(FinalSol_Temp['Margin'])
        TotSnoLoaded = FinalSol_Temp.shape[0]               
        data=[
              {
                'HeurOption': 'LHC',
                'CDOption':CDOption,
                'TotWt':TotWt,
                'TotVol':TotVol,
                'TotVol':TotVol,
                'TotMargin':TotMargin,
                'TotSnoLoaded': TotSnoLoaded, 
                'FeasibilityFlag': FeasibilityFlag,     
                'OrdersInfeasible': OrdersInfeasible,
                'CountInfOrderNbr': len(OrdersInfeasible),
                'OrdersLoaded': OrdersLoaded,
                'VolOrdersLoaded':VolOrdersLoaded,
                'OrdersNotLoaded': OrdersNotLoaded
              }
             ]        
        Summary_FinalSol = Summary_FinalSol.append(data,ignore_index=True)
        
        
        # if at least one feasible solution is obtained then update this flag
        ConstHeurSolFeasibile = 0
        if sum(Summary_FinalSol["FeasibilityFlag"]) >= 1:
            ConstHeurSolFeasibile = 1
                
        # Free the memory
        del CargoLoaded_Nbr
        del CargoLoaded_L
        del CargoLoaded_W
        del CargoLoaded_H
        del CargoLoaded_x
        del CargoLoaded_y
        del CargoLoaded_z
        del CargoLoaded_Wt
        del CargoLoaded_Or
        
        del CargoRem
        del CargoWt 
        del CargoL   
        del CargoW   
        del CargoH 
        del CargoP 
        del CargoWtLimitFactor
        del CargoSA_perc
        
        del dfOT
        del FinalSol_Temp
        
    return FinalSol, Summary_FinalSol, ConstHeurSolFeasibile, dfOT_Final, CDAvail_Final
        
