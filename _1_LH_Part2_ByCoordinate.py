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
import copy

def LoadCargoes(dfIPset2, ContainerData, Sol_P1, dfOT_P1, CDAvail_P1):    
    
    ##################################### INITIALIZATIONS
    
    ########### Create ID_Reduced
    ID_Reduced = copy.deepcopy(dfIPset2)
    ID_Reduced.reset_index(drop=True, inplace=True)    
    # ID_Reduced.to_csv('dfIPset2.csv', sep=',', encoding='utf-8', index = False)
    input("Entered Part 2 of first loading; Check dfIPset2")        
    
    ########### Generate Container Related Data
    ContainerWeight = ContainerData['Wt'][0]        
    ContainerL = ContainerData['L'][0]
    ContainerW = ContainerData['W'][0]
    ContainerH = ContainerData['H'][0]
    L1, L2, L3 = ContainerData['Len_Axle1'][0], ContainerData['Len_Axle2'][0], ContainerData['Len_Axle3'][0]
    ContainerVolume = ContainerL*ContainerW*ContainerH
    ExtWtP1, ExtWtP2, ExtWtP3 = AF.AxleWtCal(Sol_P1, L1, L2, L3)  
    WtLimitP1, WtLimitP2, WtLimitP3 = ContainerData['Wt_Axle1'][0], ContainerData['Wt_Axle2'][0], ContainerData['Wt_Axle3'][0]
    GapFactor_Container, GapFactor_Cargo = 0.25, 0.10

    ########### Create empty dataframes and lists
    column_names = ["Sno", "Wt", "x", "y", "z", "l", "w", "h", "WtLF", "SAPer"]
    FinalSol = pd.DataFrame(columns = column_names)    

    dfOT = copy.deepcopy(dfOT_P1)
    
    CargoLoaded_Nbr   = Sol_P1["Sno"].to_list() # List of the cargoes that are already loaded
    CargoLoaded_L     = Sol_P1["l"].to_list() # List of the length of each cargo inside the container
    CargoLoaded_W     = Sol_P1["w"].to_list() # List of the width of each cargo inside the container
    CargoLoaded_H     = Sol_P1["h"].to_list() # List of the height of each cargo inside the container
    CargoLoaded_x     = Sol_P1["x"].to_list() # List of the x-coordinate of each cargo inside the container
    CargoLoaded_y     = Sol_P1["y"].to_list() # List of the y-coordinate of each cargo inside the container
    CargoLoaded_z     = Sol_P1["z"].to_list() # List of the z-coordinate of each cargo inside the container
    CargoLoaded_Wt    = Sol_P1["Wt"].to_list() # List of the weight of each cargo inside the container
    WeightLoaded      = sum(CargoLoaded_Wt) # It will tell how much is loaded so far   
    CargoLoaded_WtLF  = Sol_P1["WtLF"].to_list()
    CargoLoaded_SAPer = Sol_P1["SAPer"].to_list()
    
    # Initialize CDAvail = Coordinates from Sol_P1
    
    CDAvail = copy.deepcopy(CDAvail_P1)    
    CDRemoved     = []
    CDAvail_Final = []
    
    # Create Initial Lists from ID_Reduced
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
    IsCDRemoved = 1
    WeightLoaded = 0.0
    FeasibilityFlag = 0
    
    ########################################################### BEGIN EVALUATION             
    
    while IsCargoPlaced == 1 or IsCDRemoved == 1:
        
        IsCargoPlaced, IsCDRemoved = 0, 0
        
        if len(CDAvail) > 0:
            # Next scan over each coordinate to find the right placement for cargo i but before that sort the coordinates according to CDOption
            CDAvail = sorted(CDAvail, key=lambda element: (element[0], element[1], element[2]))
           
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
                                        # dfOT.to_csv('dfOTImmAfterWtExceedFlag.csv', sep=',', encoding='utf-8', index = False)
                                        
                                        #print("WtLimitExceedFlag ByCoordinateCode: "+str(WtLimitExceedFlag))
                                        # input("press enter")
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
                                                # print("WtExceededFlag: "+str(WtLimitExceedFlag))
                                                # print("SuffSupportAreaFlag: "+str(SuffSupportAreaFlag))
                                                # dfOT.to_csv('dfOTBeforeRowsRemoved.csv', sep=',', encoding='utf-8', index = False)
                                                # print("ca: "+str(ca))
                                                # print("Cargo Nbr: "+str(cargo)+"; Or: "+str(l_hat)+", "+str(w_hat)+", "+str(h_hat))
                                                dfOT = dfOT[~(dfOT["t"] == cargo)]
                                                # dfOT.to_csv('dfOTAterRowsRemoved.csv', sep=',', encoding='utf-8', index = False)
                                                #input("Remove Last dfOT")                                                
                                        # else:
                                        #     print("Wt limit exceeded for cargo: "+str(cargo))
                                        #     # input("press enter")
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
    #print(dfOT)
    FinalSol['Sno']      = CargoLoaded_Nbr
    FinalSol['Wt']       = CargoLoaded_Wt
    FinalSol['x']        = CargoLoaded_x
    FinalSol['y']        = CargoLoaded_y
    FinalSol['z']        = CargoLoaded_z
    FinalSol['l']        = CargoLoaded_L
    FinalSol['w']        = CargoLoaded_W
    FinalSol['h']        = CargoLoaded_H        
    FinalSol['WtLF']     = CargoLoaded_WtLF
    FinalSol['SAPer']    = CargoLoaded_SAPer
    FinalSol = pd.merge(FinalSol, ID_Reduced[['Sno','OrderNbr','Volume', 'Margin']], on=['Sno'], how='left')        
    # print("Vol Loaded: "+str(sum(FinalSol["Volume"])))
    if len(CDAvail) > 0:
        for c in range(len(CDAvail)):
            CDAvail_Final.append(CDAvail[c])
    
    if len(CDRemoved) > 0:
        for c in range(len(CDRemoved)):
            CDAvail_Final.append(CDRemoved[c])
    
    if len(CargoRem) == 0:
        # print("All cargoes of ID_Reduced Loaded")
        FeasibilityFlag = 1
        # FinalSol.to_csv('FirstFeasiblePlacement.csv', sep=',', encoding='utf-8', index = False)
        # input("Stop Compilation")
        # dfOT.to_csv('FeasibledfOT.csv', sep=',', encoding='utf-8', index = False)
    # else:
    #     # print("Sol Not Feasible")
    #     FinalSol.to_csv('InfeasiblePlacement.csv', sep=',', encoding='utf-8', index = False)
    #     # input("Stop Compilation")
                
    return  FinalSol, FeasibilityFlag, dfOT, CDAvail_Final
        
