import numpy as np
import pandas as pd
from mip import Model, xsum, maximize, BINARY
from collections import OrderedDict

DotSize = 2.5
FontSize = 4.0

##########################################################################################

def SolveMIP(dfCargo, dfContainer, MipOption, ReduceVol, ListDisOrders):
    
    #First solve a MIP only to identify which orders need to be loaded
    Agg_dfCargo = dfCargo.groupby(['OrderNbr'], as_index=False).agg({'Weight': 'sum', 'Volume': 'sum', 'Margin': 'sum', 'SkidNbr':'count'})
    Agg_dfCargo.rename(columns={'SkidNbr': 'SkidCount'}, inplace=True)
    W = Agg_dfCargo['Weight'].to_list()
    P = Agg_dfCargo['Volume'].to_list()
    M = Agg_dfCargo['Margin'].to_list()
    S = Agg_dfCargo['SkidCount'].to_list()
    J = Agg_dfCargo.shape[0]
    
    # Create model
    mAgg = Model("Selection")
    
    # Define variables
    z = [mAgg.add_var(var_type=BINARY) for j in range(J)]
    
    #Objective function
    # if MipOption == 0:
    #     mAgg.objective = maximize(xsum(M[j]/S[j]*z[j] for j in range(J)))
    #     mAgg += xsum(P[j]*z[j] for j in range(J)) <= 3500 #dfContainer['L'][0]*dfContainer['W'][0]*dfContainer['H'][0]
    # elif MipOption == 1:
    #     mAgg.objective = maximize(xsum(M[j]/S[j]*z[j] for j in range(J)))
    #     mAgg += xsum(P[j]*z[j] for j in range(J)) <= dfContainer['L'][0]*dfContainer['W'][0]*dfContainer['H'][0]*0.75 
    # elif MipOption == 2:
    #     mAgg.objective = maximize(xsum(P[j]*z[j] for j in range(J)))
    #     mAgg += xsum(P[j]*z[j] for j in range(J)) <= 3500 #dfContainer['L'][0]*dfContainer['W'][0]*dfContainer['H'][0]
    # elif MipOption == 3:             
    #     mAgg.objective = maximize(xsum(P[j]*z[j] for j in range(J)))
    #     mAgg += xsum(P[j]*z[j] for j in range(J)) <= dfContainer['L'][0]*dfContainer['W'][0]*dfContainer['H'][0]*0.75
    
    if MipOption == 0:
        mAgg.objective = maximize(xsum(P[j]*z[j] for j in range(J)))
        mAgg += xsum(P[j]*z[j] for j in range(J)) <= 3500 #dfContainer['L'][0]*dfContainer['W'][0]*dfContainer['H'][0]
        mAgg += xsum(W[j]*z[j] for j in range(J)) <= 38000 #dfContainer['Wt'][0]   

    elif MipOption == 1:
        mAgg.objective = maximize(xsum(P[j]*z[j] for j in range(J)))
        mAgg += xsum(P[j]*z[j] for j in range(J)) <= 3250
        mAgg += xsum(W[j]*z[j] for j in range(J)) <= 38000 #dfContainer['Wt'][0]   
    elif MipOption == 2:
        mAgg.objective = maximize(xsum(P[j]*z[j] for j in range(J)))
        mAgg += xsum(P[j]*z[j] for j in range(J)) <= 3000
        mAgg += xsum(W[j]*z[j] for j in range(J)) <= 38000 #dfContainer['Wt'][0]   
    elif MipOption == 3:             
        mAgg.objective = maximize(xsum(P[j]*z[j] for j in range(J)))
        mAgg += xsum(P[j]*z[j] for j in range(J)) <= 2750
        mAgg += xsum(W[j]*z[j] for j in range(J)) <= 38000 #dfContainer['Wt'][0]       
    elif MipOption == 4:                     
        mAgg.objective = maximize(xsum(M[j]/S[j]*z[j] for j in range(J)))
        mAgg += xsum(P[j]*z[j] for j in range(J)) <= 3500
        mAgg += xsum(W[j]*z[j] for j in range(J)) <= 43000 #dfContainer['Wt'][0]          
    elif MipOption == 5:                     
        mAgg.objective = maximize(xsum(M[j]/S[j]*z[j] for j in range(J)))
        mAgg += xsum(P[j]*z[j] for j in range(J)) <= 3250
        mAgg += xsum(W[j]*z[j] for j in range(J)) <= 43000 #dfContainer['Wt'][0]   
        
    # Solve
    mAgg.optimize(max_seconds=600)
    
    
    # Extract solution
    OrdersLoadedAgg = []
    for j in range(J):
        if z[j].x >= 0.99:
            OrdersLoadedAgg.append(Agg_dfCargo['OrderNbr'][j])
    
    # print("Orders Loaded from MIP: ")
    # print(str(OrdersLoadedAgg))
    # input('Press Enter')
    return OrdersLoadedAgg


##########################################################################################


