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

def LoadCargoes(dfIPset2, ContainerData, Sol_LHPart1, dfOT_LHPart1, CD_LHPart1):        
    #Sol_LHPart1.to_csv('Sol_LH1_Part1.csv', sep=',', encoding='utf-8', index = False)            
       
    dfVolume1 = Sol_LHPart1[['Sno', 'Volume', 'OrderNbr']]
    dfVolume2 = dfIPset2[['Sno', 'Volume', 'OrderNbr']]
    dfVolume1 = dfVolume1.append(dfVolume2, ignore_index=True)

    ##################################### INITIALIZATIONS
    FeasibilityFlag = 0
    column_names = ["Sno", "Wt", "x", "y", "z", "l", "w", "h", "WtLF", "SAPer"]
    FinalSol = pd.DataFrame(columns = column_names)    
    
    ########### Create ID_Reduced
    ID_Reduced = copy.deepcopy(dfIPset2) 
    ID_Reduced.reset_index(drop=True, inplace=True)    
    
    # Potential Orientations Set
    ID_Reduced['P'] = ''    
    for i in range(ID_Reduced.shape[0]):
        if ID_Reduced['l_flag'][i] == 1 and ID_Reduced['w_flag'][i] == 1 and ID_Reduced['h_flag'][i] == 1:
            ID_Reduced['P'][i] = [1]
        elif ID_Reduced['l_flag'][i] == 1 and ID_Reduced['w_flag'][i] == 1 and ID_Reduced['h_flag'][i] == 0:
            ID_Reduced['P'][i] = [1]
        elif ID_Reduced['l_flag'][i] == 1 and ID_Reduced['w_flag'][i] == 0 and ID_Reduced['h_flag'][i] == 0:
            ID_Reduced['P'][i] = [1, 3]
        elif ID_Reduced['l_flag'][i] == 0 and ID_Reduced['w_flag'][i] == 1 and ID_Reduced['h_flag'][i] == 1:
            ID_Reduced['P'][i] = [1]
        elif ID_Reduced['l_flag'][i] == 0 and ID_Reduced['w_flag'][i] == 1 and ID_Reduced['h_flag'][i] == 0:
            ID_Reduced['P'][i] = [1, 2]
        elif ID_Reduced['l_flag'][i] == 0 and ID_Reduced['w_flag'][i] == 0 and ID_Reduced['h_flag'][i] == 1:
            ID_Reduced['P'][i] = [6, 1]
        elif ID_Reduced['l_flag'][i] == 1 and ID_Reduced['w_flag'][i] == 0 and ID_Reduced['h_flag'][i] == 1:
            ID_Reduced['P'][i] = [1]
        elif ID_Reduced['l_flag'][i] == 0 and ID_Reduced['w_flag'][i] == 0 and ID_Reduced['h_flag'][i] == 0:
            ID_Reduced['P'][i] = [6, 1, 2, 3, 4, 5]
    ID_Reduced.reset_index(drop=True, inplace=True)    
    #ID_Reduced.to_csv('CargoID_ReducedSet4.csv', sep=',', encoding='utf-8', index = False)       
    #input("Check ID_Reduced and press enter")        
    
    ########### Generate Container Related Data
    ContainerWeight = ContainerData['Wt'][0]        
    ContainerL = ContainerData['L'][0]
    ContainerW = ContainerData['W'][0]
    ContainerH = ContainerData['H'][0]
    L1, L2, L3 = ContainerData['Len_Axle1'][0], ContainerData['Len_Axle2'][0], ContainerData['Len_Axle3'][0]
    ContainerVolume = ContainerL*ContainerW*ContainerH
    ExtWtP1, ExtWtP2, ExtWtP3 = AF.AxleWtCal(Sol_LHPart1, L1, L2, L3)   
    WtLimitP1, WtLimitP2, WtLimitP3 = ContainerData['Wt_Axle1'][0], ContainerData['Wt_Axle2'][0], ContainerData['Wt_Axle3'][0]
    GapFactor_Container, GapFactor_Cargo = 0.25, 0.10           
    
    #### Initial dfOT
    dfOT = copy.deepcopy(dfOT_LHPart1)    

    #### Initial Loadings            
    CargoLoaded_Nbr   = Sol_LHPart1["Sno"].to_list() # List of the cargoes that are already loaded
    CargoLoaded_L     = Sol_LHPart1["l"].to_list() # List of the length of each cargo inside the container
    CargoLoaded_W     = Sol_LHPart1["w"].to_list() # List of the width of each cargo inside the container
    CargoLoaded_H     = Sol_LHPart1["h"].to_list() # List of the height of each cargo inside the container
    CargoLoaded_x     = Sol_LHPart1["x"].to_list() # List of the x-coordinate of each cargo inside the container
    CargoLoaded_y     = Sol_LHPart1["y"].to_list() # List of the y-coordinate of each cargo inside the container
    CargoLoaded_z     = Sol_LHPart1["z"].to_list() # List of the z-coordinate of each cargo inside the container
    CargoLoaded_Wt    = Sol_LHPart1["Wt"].to_list() # List of the weight of each cargo inside the container
    WeightLoaded      = sum(CargoLoaded_Wt) # It will tell how much is loaded so far   
    CargoLoaded_WtLF  = Sol_LHPart1["WtLF"].to_list()
    CargoLoaded_SAPer = Sol_LHPart1["SAPer"].to_list()
            
    # Initialize CDAvail = Coordinates from Sol_P1
    CDAvail = copy.deepcopy(CD_LHPart1)
    #print(CDAvail)
            
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

    ########################################################### BEGIN EVALUATION         
    IsCargoPlaced = 1 # 1: yes a cargo is placed in this iteration    
    while IsCargoPlaced == 1:         
                
        IsCargoPlaced = 0
        i = 0
        #print("Num cargoes remaining: "+str(len(CargoRem)))
        while i < len(CargoRem):
            cargo = CargoRem[i] # current cargo number
            # print('Check cargo '+str(cargo))
            cargoweight = CargoWt[i] # current cargo weight
            if WeightLoaded + cargoweight <= ContainerWeight:            

                CDAvail = list(dict.fromkeys(CDAvail))
                CDAvail = sorted(CDAvail, key=lambda element: (element[0], element[1], element[2]))
                
                for c in range(len(CDAvail)):
                    ca = CDAvail[c]
                    SkipRemainingCoordinates = 0
                        
                    l_hat, w_hat, h_hat = 0.0, 0.0, 0.0
                    for p in range(len(CargoP[i])):
                        l_hat, w_hat, h_hat = AF.TempDim_Function(p, i, CargoP, CargoL, CargoW, CargoH)                    
                        # Begin with assuming that current orientation 'p' is not good, and if cargo i is placed change this flag to 1
                        SkipRemainingOrientations = 0 

                        # Next scan over each coordinate to find the right placement for cargo i but before that sort the coordinates according to CDOption   
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
                                            SkipRemainingCoordinates = 1 # Skip further explorations of items
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
                                            dfOT = dfOT[~(dfOT["t"] == cargo)]
                        if SkipRemainingOrientations == 1:
                            break                                        
                    if SkipRemainingCoordinates == 1:
                        break       
            # If any cargo is placed from CargoRem then stop inner while loop by setting i > limit 
            if IsCargoPlaced == 1:
                i = 10000000
            else:
                i = 10000000                
    
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
    FinalSol = pd.merge(FinalSol, dfVolume1[['Sno','Volume', 'OrderNbr']], on=['Sno'], how='left')    
    FinalSol.reset_index(drop=True, inplace=True)
    #FinalSol.to_csv('Sol_LH1_Part2.csv', sep=',', encoding='utf-8', index = False)                        
            
    if len(CargoRem) == 0:
        FeasibilityFlag = 1                    
    # print('Sol Second Part: '+str(FeasibilityFlag))
    # input("press enter")
    
    return FinalSol, FeasibilityFlag, dfOT, CDAvail
        
