'''

ALGORITHM:
    1. CargoData, DisCargoData
    2. AggOrders, Disorders --> create CombDisOrders
    3. for d in CombDisOrders:
    4.  Set1     = CargoData - those cargoes that are in DisOrder 'd'
    5.  Set2     = All cargoes that are in DisOrder d
    6.  Set3     = {i : i in Set2 and Wti >= 20} #Change 20 to 100 later
    7.  Set4     = Set2 - Set3
    8.  Set5     = Set1 + Set3
    9.  Solution = LoadCargoes(Set5)
    10. Let l \in d be the set of orders that are present in Solution. Find cargoes from Set4 that corresponding to 'l', and load them to 'Solution'

'''

import pandas as pd
import numpy as np
import os, time
import sys
import _1_Grouping_1 as G1
import scipy.stats as st
import os.path, PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from pathlib import Path
import shutil
import errno
import _5_BoxbyBox_Plotting as F
import warnings
import pickle
import _1_LH_2_ByBox as LH2B
import _1_Grouping_2Agg as G2Agg
#print ("This is the name of the script: ", sys.argv[0])

###########################################################################################


def del_folder(dir_name):
    
    dir_path = os.getcwd() +  "\{}".format(dir_name)    
    try:
        os.rmdir(dir_path)  # remove the folder
    except:
        print("remove files first")   # couldn't remove the folder because we have files inside it
    finally:
        # now iterate through files in that folder and delete them one by one and delete the folder at the end
        try:
            for filepath in os.listdir(dir_path):
                os.remove(dir_path +  "\{}".format(filepath))
            os.rmdir(dir_path)
            print("folder is deleted")
        except:
            print("folder is not there")
            
            
###########################################################################################

            
if __name__ == '__main__':       

    warnings.filterwarnings('ignore')

    path = os.getcwd()    
  
    File_Outside = pd.ExcelFile('CLPData_Parameters.xlsx')
    CargoData_Temp = pd.read_excel(File_Outside, 'CargoData')    
        
    ContainerData_Temp = pd.read_excel(File_Outside, 'ContainerData')         
    IncludeDisAggFlag = 0               
            
    ######################################################## With Grouping Without Disaggregation        
    
    
    if IncludeDisAggFlag == 0:
        print("Run Algorithm with Aggregated Cargoes")
        RunAlgo = int(input('Aggregation: Enter 0 to print solution or 1 to run algo: '))
        
        if RunAlgo == 0:
            folder = "SolutionsGroupAgg"    
            solpath = Path('%s\\%s' %(path,folder))    
            os. chdir(solpath)
            Nbr = int(input('Enter solution number: '))
            
            # Plot Feasible Solution            
            F.OneByOnePlot(Nbr, ContainerData_Temp, 1, IncludeDisAggFlag) #1: for first angle
            F.OneByOnePlot(Nbr, ContainerData_Temp, 2, IncludeDisAggFlag) #2: for second angle
            F.OneByOnePlot(Nbr, ContainerData_Temp, 3, IncludeDisAggFlag) #3: for third angle
            os.chdir("..")
            
        else:
            start = time.time()
            # 1. Check if folder name solution exists or not
            folder = "SolutionsGroupAgg"    
            solpath = Path('%s\\%s' %(path,folder))    
            #solpath = os.path.join(path, folder)
            print(solpath)
            if os.path.isdir(folder):
                del_folder(folder)      
                os.makedirs(solpath)
            else:
                os.makedirs(solpath)
            
            # 2. First heuristic feasible solution on aggregated orders      
            AllSols = G2Agg.LoadCargoes1()      
            
            # 3. Change path of the working directory to "Solutions... " folder
            os. chdir(solpath)                               
            
            # 4. Save all possible feasible solutions as a dictionary using pickle             
            pickle.dump(AllSols, open( "AllSolutions.p", "wb" ) )           
            
            # 5. Create summary and detailed excel files of feasible solutions
            column_names = ['SolNbr', 'Volume']
            SummaryAllSolutions = pd.DataFrame(columns = column_names)    

            column_names = ['SolNbr', 'Sno', 'Wt', 'x', 'y', 'z', 'l', 'w',	 'h', 'WtLF', 'SAPer', 'OrderNbr']
            DetailsAllSolutions = pd.DataFrame(columns = column_names)
            
            List_AllSols_Keys = list(AllSols.keys())
            BestSolNbr = -1
            BestVol = -1
            for l in range(len(AllSols)):                
                SolNbr = List_AllSols_Keys[l]
                Vol = AllSols[SolNbr][4]
                data = [{'SolNbr':SolNbr, 'Volume':Vol}]
                SummaryAllSolutions = SummaryAllSolutions.append(data,ignore_index=True,sort=False)
                if Vol > BestVol:
                    BestVol = Vol
                    BestSolNbr = SolNbr

                DetailsAllSolutions = DetailsAllSolutions.append(AllSols[SolNbr][1],ignore_index=True)
                DetailsAllSolutions["SolNbr"].fillna(SolNbr, inplace = True) 

            # print(SummaryAllSolutions)
            SummaryAllSolutions.to_csv('SummaryAllSolutions.csv', sep=',', encoding='utf-8', index = False)
            DetailsAllSolutions.to_csv('DetailsAllSolutions.csv', sep=',', encoding='utf-8', index = False)
            
            # 6. Plot Best Solution            
            F.OneByOnePlot(BestSolNbr, ContainerData_Temp, 1, IncludeDisAggFlag) #1: for first angle
            F.OneByOnePlot(BestSolNbr, ContainerData_Temp, 2, IncludeDisAggFlag) #2: for second angle
            F.OneByOnePlot(BestSolNbr, ContainerData_Temp, 3, IncludeDisAggFlag) #3: for third angle

            end = time.time()
            print("Time: "+str(end - start)+"; Best Solution Number: "+str(BestSolNbr))                     
            #input("Press enter to plot the solution or Stop Compilation")

            
    sys.exit()
    