import operator
import os
import sys, csv
import random
import math
import time
import pandas as pd
import numpy as np
from numpy import arange
import _4_Plots3D2 as Plot2

def WeightCalculations(cargo_number, df1):
    TempWt = 0
    for l in range(df1.shape[0]):
        if df1['b'][l] == cargo_number:
            t = df1['t'][l]
            TempWt = TempWt + df1['Wt_E'][l] + WeightCalculations(t, df1)
    
    return TempWt


#####################################################################################################################    
    

def PF_Func(cargo, j, l_hat, w_hat, h_hat, ca, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H):
    
    CanBePLaced_1 = 0 # Assuming i is not good wrt to j
    CanBePLaced_2 = 0 # Assuming j is not good wrt i
    
    # First check cargo i relative to cargo j
    #Case 1: if i is behind, to the left of and under j
    if ca[0] < CargoLoaded_x[j] and ca[1] < CargoLoaded_y[j] and ca[2] < CargoLoaded_z[j]:
        if (ca[0] + l_hat <= CargoLoaded_x[j] or ca[1] + w_hat <= CargoLoaded_y[j] or ca[2] + h_hat <= CargoLoaded_z[j]):
            CanBePLaced_1 = 1
    #Case 2: if i is behind and to the left of j
    elif ca[0] < CargoLoaded_x[j] and ca[1] < CargoLoaded_y[j]:
        if (ca[0] + l_hat <= CargoLoaded_x[j] or ca[1] + w_hat <= CargoLoaded_y[j]):
            CanBePLaced_1 = 1
    #Case 3: if i is behind and under j
    elif ca[0] < CargoLoaded_x[j] and ca[2] < CargoLoaded_z[j]:
        if (ca[0] + l_hat <= CargoLoaded_x[j] or ca[2] + h_hat <= CargoLoaded_z[j]):
            CanBePLaced_1 = 1
    #Case 4: if i to the left of and under j
    elif ca[1] < CargoLoaded_y[j] and ca[2] < CargoLoaded_z[j]:
        if (ca[1] + w_hat <= CargoLoaded_y[j] or ca[2] + h_hat <= CargoLoaded_z[j]):
            CanBePLaced_1 = 1
    #Case 5: if i is behind j
    elif ca[0] < CargoLoaded_x[j]:
        if (ca[0] + l_hat <= CargoLoaded_x[j]):
            CanBePLaced_1 = 1
    #Case 6: if i is to the left of j
    elif ca[1] < CargoLoaded_y[j]:
        if (ca[1] + w_hat <= CargoLoaded_y[j]):
            CanBePLaced_1 = 1
    #Case 7: if i is under j
    elif ca[2] < CargoLoaded_z[j]:
        if (ca[2] + h_hat <= CargoLoaded_z[j]):
            CanBePLaced_1 = 1
    
    # Next check cargo j relative to cargo i
    #Case 1: if j is behind, to the left of and under i
    if CargoLoaded_x[j] < ca[0] and CargoLoaded_y[j] < ca[1] and CargoLoaded_z[j] < ca[2] :
        if (CargoLoaded_x[j] + CargoLoaded_L[j] <= ca[0] or CargoLoaded_y[j] + CargoLoaded_W[j] <= ca[1] or CargoLoaded_z[j] + CargoLoaded_H[j] <= ca[2]):
            CanBePLaced_2 = 1
    #Case 2: if j is behind and to the left of i
    elif CargoLoaded_x[j] < ca[0] and CargoLoaded_y[j] < ca[1] :
        if (CargoLoaded_x[j] + CargoLoaded_L[j] <= ca[0] or CargoLoaded_y[j] + CargoLoaded_W[j] <= ca[1]):
            CanBePLaced_2 = 1
    #Case 3: if j is behind and under i
    elif CargoLoaded_x[j] < ca[0] and CargoLoaded_z[j] < ca[2] :
        if (CargoLoaded_x[j] + CargoLoaded_L[j] <= ca[0] or CargoLoaded_z[j] + CargoLoaded_H[j] <= ca[2]):
            CanBePLaced_2 = 1
    #Case 4: if j to the left of and under i
    elif CargoLoaded_y[j] < ca[1] and CargoLoaded_z[j] < ca[2] :
        if (CargoLoaded_y[j] + CargoLoaded_W[j] <= ca[1] or CargoLoaded_z[j] + CargoLoaded_H[j] <= ca[2]):
            CanBePLaced_2 = 1
    #Case 5: if j is behind i
    elif CargoLoaded_x[j] < ca[0] :
        if (CargoLoaded_x[j] + CargoLoaded_L[j] <= ca[0]):
            CanBePLaced_2 = 1
    #Case 6: if j is to the left of i
    elif CargoLoaded_y[j] < ca[1] :
        if (CargoLoaded_y[j] + CargoLoaded_W[j] <= ca[1] ):
            CanBePLaced_2 = 1
    #Case 7: if j is under i
    elif CargoLoaded_z[j] < ca[2] :
        if (CargoLoaded_z[j] + CargoLoaded_H[j] <= ca[2]):
            CanBePLaced_2 = 1

    # print('IF: ('+str(cargo)+', '+str(j)+'); Flags: '+str(NotOverlapping_1)+', '+str(NotOverlapping_2))
    return CanBePLaced_1, CanBePLaced_2


#####################################################################################################################


def TempDim_Function(p, i, CargoP, CargoL, CargoW, CargoH):
    if   CargoP[i][p] == 1:
        l, w, h = CargoL[i], CargoW[i], CargoH[i]                            
    elif CargoP[i][p] == 2:
        l, w, h = CargoH[i], CargoW[i], CargoL[i]                    
    elif CargoP[i][p] == 3:
        l, w, h = CargoL[i], CargoH[i], CargoW[i]
    elif CargoP[i][p] == 4:
        l, w, h = CargoW[i], CargoH[i], CargoL[i]
    elif CargoP[i][p] == 5:
        l, w, h = CargoH[i], CargoL[i], CargoW[i]
    elif CargoP[i][p] == 6:
        l, w, h = CargoW[i], CargoL[i], CargoH[i]

    return l, w, h


#####################################################################################################################


def SuffDim_Function(l_hat, w_hat, h_hat, ca, TruckL, TruckW, TruckH):
    SuffDim = 0
    if (ca[0] + l_hat <= TruckL and ca[1] + w_hat <= TruckW and ca[2] + h_hat <= TruckH):
            SuffDim = 1
    
    # print('y: '+str(ca[1])+', '+str(w_hat)+', '+str(TruckW)+', SuffFlag: '+str(SuffDim))
    # input('Enter any number: ')
    return SuffDim


#####################################################################################################################


def WeightConstraints(i, ca, cargo, cargoweight, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr, df, WtLimitFactor, CargoLoaded_WtLF):
    if ca[2] > 0:        
        WtExceeded = 0
        Touching = [0 for t in range(len(CargoLoaded_Nbr))]
    
        WtOf_iOnj = 0
        
        # STEP 1: Check if cargo 'i' is touching which already placed cargoes 'j'
        for j in range(len(CargoLoaded_Nbr)):            
            # 1. Check if 'i' exactly on top of 'j' with surfaces touching
            Touching[j] = 1
            if CargoLoaded_z[j] + CargoLoaded_H[j] == ca[2]:
                # if cargo == 76:
                #     print("Touching: "+str(CargoLoaded_Nbr[j]))
                #     input("enter")
                    
                # if cargo == 5 and CargoLoaded_Nbr[j] == 20:
                    # print('cargo %d is placed over cargo %d'%(cargo, CargoLoaded_Nbr[j]))
                    # print('ca[2]: %.2f'%(ca[2]))
                    # print('j=%d: x: %.2f, y: %.2f, z: %.2f'%(j, CargoLoaded_x[j], CargoLoaded_y[j], CargoLoaded_z[j]))
                    # input('Press Enter')
                # Check if j is completely to the left of, to the right of, in front of or behind i
                if (CargoLoaded_y[j] + CargoLoaded_W[j] <= ca[1]) or (ca[1] + w_hat <= CargoLoaded_y[j]) or (CargoLoaded_x[j] + CargoLoaded_L[j] <= ca[0]) or (ca[0] + l_hat <= CargoLoaded_x[j]):
                    Touching[j] = 0
            else:    
                Touching[j] = 0
            
        # STEP 2: if Touching[j] == 1 for any of the cargo
        if sum(Touching) >= 1:
            for j in range(len(CargoLoaded_Nbr)):            
                if Touching[j] == 1:

                    # Find out how much area of i is on top of j
                    length, width = 0.0, 0.0

                    # 1. Find length
                    if CargoLoaded_x[j] <= ca[0]:
                        length = np.minimum(CargoLoaded_x[j] + CargoLoaded_L[j] - ca[0], l_hat)
                    else:
                        length = np.minimum(ca[0] + l_hat - CargoLoaded_x[j], CargoLoaded_L[j])
                    
                    # 2. Find width
                    if CargoLoaded_y[j] <= ca[1]:
                        width = np.minimum(CargoLoaded_y[j] + CargoLoaded_W[j] - ca[1], w_hat)
                    else:
                        width = np.minimum(ca[1] + w_hat - CargoLoaded_y[j], CargoLoaded_W[j])
                    
                    WtOf_iOnj = length*width*cargoweight/(l_hat*w_hat)                    
                    
                    # 3. if weight exert by 'i' on 'j' is less than weight restriction of 'j then add j-i pair to dataframe dfOT
                    if WtOf_iOnj <= WtLimitFactor*CargoLoaded_Wt[j]:
                        data = [{'b':CargoLoaded_Nbr[j],
                                 't':cargo,
                                 'x_b':CargoLoaded_x[j],
                                 'y_b':CargoLoaded_y[j],
                                 'z_b': CargoLoaded_z[j], 
                                 'x_t': ca[0],
                                 'y_t': ca[1],
                                 'z_t': ca[2],
                                 'L_b': CargoLoaded_L[j],
                                 'W_b': CargoLoaded_W[j],
                                 'H_b': CargoLoaded_H[j],
                                 'L_t': l_hat,
                                 'W_t': w_hat,
                                 'H_t': h_hat,
                                 'Wt_b': CargoLoaded_Wt[j],
                                 'Wt_t': cargoweight,
                                 'LOf_iOnj':length,
                                 'WOf_iOnj':width,
                                 'Wt_E': WtOf_iOnj}]
                        df = df.append(data,ignore_index=True,sort=False)
                        # if cargo == 575:
                        #     print("j: "+str(CargoLoaded_Nbr[j]))
                        #     print("WtOf_iOnj: "+str(WtOf_iOnj))
                        #     print("Wt Limit of j: "+str(WtLimitFactor*CargoLoaded_Wt[j]))
                        #     input("press enter")
                    else:
                        WtExceeded = 1
                        break
        else:
            print("ca[2] > 0 and still no touching for cargo: "+str(cargo))
            print("Coordinates: "+str(ca))
            input("There is an error. Check Code.")
            
        # 4. As addition of 'i' on top of 'j' can affect the weight restiction of box 'k' which
        # is placed below box 'j', therefore, scan over all k \in CargoLoaded_Nbr to check 
        # weight restrictions on box 'k'        
        if WtExceeded == 0:
            for k in range(len(CargoLoaded_Nbr)):
                cargo_number  = CargoLoaded_Nbr[k]
                WtOn_k = WeightCalculations(cargo_number, df)
                if WtOn_k > CargoLoaded_WtLF[k]*CargoLoaded_Wt[k]:   
                    WtExceeded = 1                    
                    break
    else:
        WtExceeded = 0
    
    if WtExceeded == 1:
        # Remove all rows from dfOT whereever dfOT['t'] ==  cargo
        df = df[~(df["t"] == cargo)]
       
    return WtExceeded, df


#####################################################################################################################


def Practical_zCoord(i, ca, cargo, cargoweight, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr):
    
    z_Front, z_Side, Below = 0.0, 0.0, 0
    FrontRange = []
    SideRange = []
    FrontHt = []
    SideHt = []
    if ca[2] == 0:
        z_Front, z_Side = 0.0, 0.0
    else:
        for j in range(len(CargoLoaded_Nbr)):
            # Find out if 'i' and 'j' are within range of each other
            if CargoLoaded_z[j] + CargoLoaded_H[j] <= ca[2]:
                # Check if j is completely to the left of i
                if CargoLoaded_y[j] + CargoLoaded_W[j] <= ca[1] or ca[1] + w_hat <= CargoLoaded_y[j] or CargoLoaded_x[j] + CargoLoaded_L[j] <= ca[0] or ca[0] + l_hat <= CargoLoaded_x[j]:
                    Below = Below + 0
                    # print('i is completely behind j')            
                else:
                    Below = Below + 1
                    if CargoLoaded_x[j] <= ca[0] + l_hat and ca[0] + l_hat < CargoLoaded_x[j] + CargoLoaded_L[j] and ca[1] >= CargoLoaded_y[j]:
                        FrontRange.append(j)
                    if CargoLoaded_y[j] <= ca[1] + w_hat and ca[1] + w_hat < CargoLoaded_y[j] + CargoLoaded_W[j] and ca[0] >= CargoLoaded_x[j]:
                        SideRange.append(j)
        # Find front coordinate
        if len(FrontRange) == 0:
            z_Front= 0.0
        else:
            for k in range(len(FrontRange)):
                FrontHt.append(CargoLoaded_z[FrontRange[k]] + CargoLoaded_H[FrontRange[k]])
            
            z_Front = max(FrontHt)
        
        # Find side coordinate
        if len(SideRange) == 0:
            z_Side= 0.0
        else:
            for k in range(len(SideRange)):
                SideHt.append(CargoLoaded_z[SideRange[k]] + CargoLoaded_H[SideRange[k]])
            
            z_Side = max(SideHt)

    return z_Front, z_Side


#####################################################################################################################


def WtDistribution(i, ca, cargo, l_hat, w_hat, h_hat, L1, L2, L3, ExtWtP1, ExtWtP2, ExtWtP3, WtLimitP1, WtLimitP2, WtLimitP3, cargoweight):
    WtRestSat, l1_T, l2_T, l3_T = 0, 0.0, 0.0, 0.0
    case = 0
    # 1. Find the placement case
    if ca[0] + l_hat <= L1:
        case = 1
    elif ca[0] <= L1 and L1 <= ca[0] + l_hat and ca[0] + l_hat <= L1 + L2:
        case = 2
    elif ca[0] <= L1 and ca[0] + l_hat >= L1+L2:
        case = 3
    elif ca[0] >= L1 and ca[0] + l_hat <= L1 + L2:
        case = 4
    elif ca[0] >= L1 and ca[0] <= L1 + L2 and ca[0] + l_hat >= L1 + L2:
        case = 5
    else:
        case = 6
        
    # 2. Find dimensions in each part
    if case == 1:
        l1_T, l2_T, l3_T = l_hat, 0.0, 0.0
    elif case == 2:
        l1_T, l2_T, l3_T = L1 - ca[0], ca[0] + l_hat - L1, 0.0
    elif case == 3:
        l1_T, l2_T, l3_T = L1 - ca[0], L2, ca[0] + l_hat - L1 - L2
    elif case == 4:
        l1_T, l2_T, l3_T = 0, l_hat, 0
    elif case == 5:
        l1_T, l2_T, l3_T = 0, L1 + L2 - ca[0], ca[0] + l_hat - L1 - L2
    else:
        l1_T, l2_T, l3_T = 0, 0, l_hat
    
    # 3. Check weight
    if (ExtWtP1 + l1_T*cargoweight/l_hat <=  WtLimitP1) and (ExtWtP2 + l2_T*cargoweight/l_hat <= WtLimitP2) and (ExtWtP3 + l3_T*cargoweight/l_hat <= WtLimitP3):
        WtRestSat = 1
    
    return WtRestSat, l1_T*cargoweight/l_hat, l2_T*cargoweight/l_hat, l3_T*cargoweight/l_hat


#####################################################################################################################


def AxleWtCal(Sol_LH, L1, L2, L3):

    l1_T, l2_T, l3_T = 0.0, 0.0, 0.0
    W1, W2, W3 = 0.0, 0.0, 0.0
    
    ca = Sol_LH['x'].to_list()
    l_hat = Sol_LH['l'].to_list()
    cargoweight = Sol_LH['Wt'].to_list()
    
    for j in range(Sol_LH.shape[0]):
        case = 0
        # 1. Find the placement case
        if ca[j] + l_hat[j] <= L1:
            case = 1
        elif ca[j] <= L1 and L1 <= ca[j] + l_hat[j] and ca[j] + l_hat[j] <= L1 + L2:
            case = 2
        elif ca[j] <= L1 and ca[j] + l_hat[j] >= L1+L2:
            case = 3
        elif ca[j] >= L1 and ca[j] + l_hat[j] <= L1 + L2:
            case = 4
        elif ca[j] >= L1 and ca[j] <= L1 + L2 and ca[j] + l_hat[j] >= L1 + L2:
            case = 5
        else:
            case = 6
            
        # 2. Find dimensions in each part
        if case == 1:
            l1_T, l2_T, l3_T = l_hat[j], 0.0, 0.0
        elif case == 2:
            l1_T, l2_T, l3_T = L1 - ca[j], ca[j] + l_hat[j] - L1, 0.0
        elif case == 3:
            l1_T, l2_T, l3_T = L1 - ca[j], L2, ca[j] + l_hat[j] - L1 - L2
        elif case == 4:
            l1_T, l2_T, l3_T = 0, l_hat[j], 0
        elif case == 5:
            l1_T, l2_T, l3_T = 0, L1 + L2 - ca[j], ca[j] + l_hat[j] - L1 - L2
        else:
            l1_T, l2_T, l3_T = 0, 0, l_hat[j]
    
        # 3. Check weight
        W1 += l1_T*cargoweight[j]/l_hat[j]
        W2 += l2_T*cargoweight[j]/l_hat[j]
        W3 += l3_T*cargoweight[j]/l_hat[j]
    
    return W1, W2, W3


#####################################################################################################################


def SupArea_Function(i, ca, cargo, cargoweight, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr, SAPercentage):
    EnoughSupport, SA = 0, 0.0
    BoxesTouching = 0
    ListBoxesTouching = []
    # print('SupArea_Function Cargo i: '+str(cargo))
    
    # if cargo == 5:
        # print(CargoLoaded_Nbr)
        # print('ca[2]: '+str(ca[2]))
        # input('Press Enter')
        
    if ca[2] > 0:     
        # Find the list of boxes touching i
        for j in range(len(CargoLoaded_Nbr)):
            # 1. Check if 'i' exactly on top of 'j' with surfaces touching
            if CargoLoaded_z[j] + CargoLoaded_H[j] == ca[2]:
                # Check if j is completely to the left of i
                if (CargoLoaded_y[j] + CargoLoaded_W[j] <= ca[1]) or (ca[1] + w_hat <= CargoLoaded_y[j]) or (CargoLoaded_x[j] + CargoLoaded_L[j] <= ca[0]) or (ca[0] + l_hat <= CargoLoaded_x[j]):
                    BoxesTouching = BoxesTouching + 0
                else:
                    BoxesTouching = BoxesTouching + 1
                    ListBoxesTouching.append(j)
                    # print('Boxes Touching: '+str(BoxesTouching)+' and List of boxes touching cargo: '+str(cargo))
                    # print(ListBoxesTouching)
                    # input('Press Enter')
                                     
        # 2. Find out the amount of support i receives from boxes in ListBoxesTouching
        for k in range(len(ListBoxesTouching)):
            # if cargo == 5:
                # print('j: %d'%(CargoLoaded_Nbr[ListBoxesTouching[k]]))
                # input('Press Enter')       
            # Find out how much area of i is on top of j
            length, width = 0.0, 0.0
            # 1. Find length
            if CargoLoaded_x[ListBoxesTouching[k]] <= ca[0]:
                length = np.minimum(CargoLoaded_x[ListBoxesTouching[k]] + CargoLoaded_L[ListBoxesTouching[k]] - ca[0], l_hat)
            else:
                length = np.minimum(ca[0] + l_hat - CargoLoaded_x[ListBoxesTouching[k]], CargoLoaded_L[ListBoxesTouching[k]])
            
            # 2. Find width
            if CargoLoaded_y[ListBoxesTouching[k]] <= ca[1]:
                width = np.minimum(CargoLoaded_y[ListBoxesTouching[k]] + CargoLoaded_W[ListBoxesTouching[k]] - ca[1], w_hat)
            else:
                width = np.minimum(ca[1] + w_hat - CargoLoaded_y[ListBoxesTouching[k]], CargoLoaded_W[ListBoxesTouching[k]])
            
            # print('cargo: '+str(CargoLoaded_Nbr[ListBoxesTouching[k]])+' touch cargo '+str(cargo)+' with area: '+str(length*width))
            SA = SA + length*width
            # if cargo == 5 and CargoLoaded_Nbr[ListBoxesTouching[k]] == 20:
                # print("j: %d, i: %d, SA: %.2f"%(CargoLoaded_Nbr[ListBoxesTouching[k]], cargo, SA))
                # print("length: %.2f, width: %.2f"%(length, width))
                # print("l_hat: %.2f, w_hat: %.2f"%(l_hat, w_hat))
                # input('Press Enter')
                
        # 3. Check flag
        if SA/(l_hat*w_hat)*100 < SAPercentage-0.000001:
            EnoughSupport = 0
        else:
            EnoughSupport = 1
    else:
        EnoughSupport = 1
    
   
    return EnoughSupport


#####################################################################################################################


def AdditionalYCoord(ca, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr):
    
    SideCoordinates, SideCargoes = [], []
    Additional_y, Ignore_j = 0, 0
    
    for j in range(len(CargoLoaded_Nbr)):
        if ca[0] + l_hat <= CargoLoaded_x[j] or CargoLoaded_x[j] + CargoLoaded_L[j] or ca[2] + h_hat <= CargoLoaded_z[j] or CargoLoaded_z[j] + CargoLoaded_H[j] <= ca[2]:
            Ignore_j += 1
        else:
            if CargoLoaded_x[j] <= ca[0] + l_hat and ca[0] + l_hat <= CargoLoaded_x[j] + CargoLoaded_L[j]:
                SideCargoes.append(j)
                
        
    if len(SideCargoes) >= 1:
        for k in range(len(SideCargoes)):
            SideCoordinates.append(CargoLoaded_y[SideCargoes[k]] + CargoLoaded_W[SideCargoes[k]])
        
        Additional_y = max(SideCoordinates)
            
    
    return Additional_y


#####################################################################################################################


def AdditionalXCoord(ca, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr):
    
    BackCoordinates, BackCargoes = [], []
    Additional_x, Ignore_j = 0, 0
              
    for j in range(len(CargoLoaded_Nbr)):
        if ca[1] + w_hat <= CargoLoaded_y[j] or CargoLoaded_y[j] + CargoLoaded_W[j] or ca[2] + h_hat <= CargoLoaded_z[j] or CargoLoaded_z[j] + CargoLoaded_H[j] <= ca[2]:
            Ignore_j += 1
        else:
            if CargoLoaded_y[j] <= ca[1] + w_hat and ca[1] + w_hat <= CargoLoaded_y[j] + CargoLoaded_W[j]:
                BackCargoes.append(j)
                
        
    if len(BackCargoes) >= 1:
        for k in range(len(BackCargoes)):
            BackCoordinates.append(CargoLoaded_x[BackCargoes[k]] + CargoLoaded_L[BackCargoes[k]])
        
        Additional_x = max(BackCoordinates)
            
    
    return Additional_x


#####################################################################################################################


def AdditionalZCoord(ca, l_hat, w_hat, h_hat, CargoLoaded_x, CargoLoaded_y, CargoLoaded_z, CargoLoaded_L, CargoLoaded_W, CargoLoaded_H, CargoLoaded_Wt, CargoLoaded_Nbr):
    
    AddCoord = []
    Ignore = 0
    Fx, Fy, Fz = 0, 0, 0
    Sx, Sy, Sz = 0, 0, 0
    
    # for j in range(len(CargoLoaded_Nbr)):
    #     if CargoLoaded_z[j] >= ca[2] + h_hat:
    #         if CargoLoaded_x[j] + CargoLoaded_L[j] <= ca[0] or ca[0] + l_hat <= CargoLoaded_x[j] or CargoLoaded_y[j] + CargoLoaded_W[j] <= ca[1] or ca[1] + w_hat <= CargoLoaded_y[j]:
    #           Ignore += 0
    #         else:
    #             if ca[0] <= CargoLoaded_x[j] + CargoLoaded_L[j] and CargoLoaded_x[j] + CargoLoaded_L[j] < ca[0] + l_hat:
    #                 if CargoLoaded_y[j] < ca[1]:
    #                     Fx = CargoLoaded_x[j] + CargoLoaded_L[j]
    #                     Fy = ca[1]
    #                     Fz = ca[2] + h_hat
    #                 elif ca[1] < CargoLoaded_y[j]:
    #                     Fx = CargoLoaded_x[j] + CargoLoaded_L[j]
    #                     Fy = CargoLoaded_y[j]
    #                     Fz = ca[2] + h_hat
                
    #             if ca[1] <= CargoLoaded_y[j] + CargoLoaded_W[j] and CargoLoaded_y[j] + CargoLoaded_W[j] < ca[1] + w_hat:
    #                 if CargoLoaded_x[j] < ca[0]:
    #                     Sx = ca[0]
    #                     Sy = CargoLoaded_y[j] + CargoLoaded_W[j]
    #                     Sz = ca[2] + h_hat
    #                 elif ca[0] < CargoLoaded_x[j]:
    #                     Sx = CargoLoaded_x[0]
    #                     Sy = CargoLoaded_y[j] + CargoLoaded_W[j]
    #                     Sz = ca[2] + h_hat
                
    #             AddCoord.append(tuple((Fx, Fy, Fz)))
    #             AddCoord.append(tuple((Sx, Sy, Sz)))
                
    AddCoord = []
    Ignore = 0
    Fx, Fy, Fz = 0, 0, 0
    Sx, Sy, Sz = 0, 0, 0
    
    for j in range(len(CargoLoaded_Nbr)):
        if CargoLoaded_z[j] >= ca[2] + h_hat:
            if CargoLoaded_x[j] + CargoLoaded_L[j] <= ca[0] or ca[0] + l_hat <= CargoLoaded_x[j] or CargoLoaded_y[j] + CargoLoaded_W[j] <= ca[1] or ca[1] + w_hat <= CargoLoaded_y[j]:
              Ignore += 0
            else:
                if ca[0] <= CargoLoaded_x[j] + CargoLoaded_L[j] and CargoLoaded_x[j] + CargoLoaded_L[j] < ca[0] + l_hat:
                    Fx = CargoLoaded_x[j] + CargoLoaded_L[j]
                    Fy = ca[1]
                    Fz = ca[2] + h_hat
                
                if ca[1] <= CargoLoaded_y[j] + CargoLoaded_W[j] and CargoLoaded_y[j] + CargoLoaded_W[j] < ca[1] + w_hat:
                    Sx = ca[0]
                    Sy = CargoLoaded_y[j] + CargoLoaded_W[j]
                    Sz = ca[2] + h_hat
                    # if Sx == 3.375 and Sy == 4.0 and Sz >= 7.54 and Sz <= 7.542:
                    #     print(ca)
                    #     print("%.2f %.2f %.2f"%(l_hat, w_hat, h_hat))
                    #     print("%.2f %.2f %.2f"%(CargoLoaded_x[j], CargoLoaded_y[j], CargoLoaded_z[j]))
                    #     print("%.2f %.2f %.2f"%(CargoLoaded_L[j], CargoLoaded_W[j], CargoLoaded_H[j]))
                    #     input("Debug Logic; press enter")
                AddCoord.append(tuple((Fx, Fy, Fz)))
                AddCoord.append(tuple((Sx, Sy, Sz)))
                
    return AddCoord


#####################################################################################################################