import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import proj3d
import numpy as np
import time
import pandas as pd
from pathlib import Path
import os, PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from fnmatch import fnmatch
import os, glob
import random
import pickle


DotSize = 1.0
FontSize = 2.5

def cuboid_data(o, size=(1,1,1)):
    # code taken from
    # https://stackoverflow.com/a/35978146/4124317
    # suppose axis direction: x: to left; y: to inside; z: to upper
    # get the length, width, and height
    l, w, h = size
    x = [[o[0], o[0] + l, o[0] + l, o[0], o[0]],  
         [o[0], o[0] + l, o[0] + l, o[0], o[0]],  
         [o[0], o[0] + l, o[0] + l, o[0], o[0]],  
         [o[0], o[0] + l, o[0] + l, o[0], o[0]]]  
    y = [[o[1], o[1], o[1] + w, o[1] + w, o[1]],  
         [o[1], o[1], o[1] + w, o[1] + w, o[1]],  
         [o[1], o[1], o[1], o[1], o[1]],          
         [o[1] + w, o[1] + w, o[1] + w, o[1] + w, o[1] + w]]   
    z = [[o[2], o[2], o[2], o[2], o[2]],                       
         [o[2] + h, o[2] + h, o[2] + h, o[2] + h, o[2] + h],   
         [o[2], o[2], o[2] + h, o[2] + h, o[2]],               
         [o[2], o[2], o[2] + h, o[2] + h, o[2]]]               
    return np.array(x), np.array(y), np.array(z)

def plotCubeAt1(pos=(0,0,0), size=(1,1,1), ax=None,**kwargs):
    # Plotting a cube element at position pos
    if ax !=None:
        X, Y, Z = cuboid_data( pos, size )
        ax.plot_surface(X, Y, Z, alpha=0.2, rstride=1, cstride=1, edgecolor ='k', linewidth=0.25, **kwargs)

def Draw_GraphicalSol1(TotalCargoLoaded, positions, sizes, CargoLoaded_Nbr, colors, TruckL, TruckW, TruckH, path, angle):
    # positions = [(0,0,0),(0,1,0),(0,5,0),(2,0,0)]
    # sizes = [(2,1,1), (2,4,1),(5,2,3),(4,10,2)]
    # colors = ["#99CCFF1A","#FF80001A","#0066CC1A", "#0000001A"]
    
    
    fig = plt.figure(figsize=(50,10))
    
    ax = fig.gca(projection='3d')
    ax.set_aspect('auto')
    ax.tick_params(axis='both', which='major', labelsize=5)
    ax.tick_params(axis='both', which='minor', labelsize=2)
    #ax.get_proj = lambda: np.dot(Axes3D.get_proj(ax), np.diag([2, 1, 1, 1]))
    
    """                                                                                                                                                    
    Scaling begin
    """
    x_scale=5
    y_scale=1
    z_scale=1
    
    scale=np.diag([x_scale, y_scale, z_scale, 1.0])    
    scale=scale*(1.0/scale.max())    
    scale[3,3]=1.0
        
    def short_proj():
        return np.dot(Axes3D.get_proj(ax), scale)
    
    ax.get_proj=short_proj
    """                                                                                                                                                    
    Scaling end                                                                                                                                                
    """

       
    """
    Begin: Grid lines settings
    """
    ax.xaxis._axinfo["grid"].update({"linewidth":0.5, "color" : "w"})
    ax.yaxis._axinfo["grid"].update({"linewidth":0.5, "color" : "w"})
    ax.zaxis._axinfo["grid"].update({"linewidth":0.5, "color" : "w"})
    # ax.yaxis._axinfo["grid"]['linewidth'] = 3.
    # ax.zaxis._axinfo["grid"]['color'] = "#ee0009"
    # ax.zaxis._axinfo["grid"]['linestyle'] = ":"
    """
    End: Grid lines settings
    """
    
    '''
    '#0000FF': Blue (>0,0,0)
    
    '''
    # draw picture
    for p,s,c in zip(positions,sizes,colors):
        plotCubeAt1(pos=p, size=s, ax=ax, color=c)
        
    # draw a point
    # for i in range(len(positions)):
    #     ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF0000', s=DotSize, zorder=1000)
        # if positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] == 0:
        #     ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#0000FF', s=DotSize)
        # elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] == 0:
        #     ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF0000', s=DotSize)
        # elif positions[i][0] == 0 and positions[i][1] == 0 and positions[i][2] > 0:
        #     ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#00FF00', s=DotSize)
        # elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] == 0:
        #     ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFFF00', s=DotSize)
        # elif positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] > 0:
        #     ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#008000', s=DotSize)        
        # elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] > 0:
        #     ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF00FF', s=DotSize)        
        # elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] > 0:
        #     ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFA500', s=DotSize)        
        # else:
        #     ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#000000', s=DotSize)        

              
    # Add text
    n = ''
    if len(positions) >= 3:
        for i in range(len(positions)-3, len(positions)):
            # if positions[i][2] > 0:
            #     n=str(str(CargoLoaded_Nbr[i])+'.'+str(1))
            # else:
            #     n=str(CargoLoaded_Nbr[i])
            n=str(CargoLoaded_Nbr[i])
            #ax.text(positions[i][0], positions[i][1], positions[i][2], n, fontsize=FontSize, color = "#FF0000", zorder=100)
            #ax.text(positions[i][0], positions[i][1], positions[i][2], n, fontsize=FontSize, zorder=500)
            ax.text(positions[i][0]+sizes[i][0], positions[i][1]+sizes[i][1]/2, positions[i][2]+sizes[i][2]/2, n, fontsize=FontSize, zorder=500, color = "#FFFFFF")
            #ax.annotate(n, xyz = (positions[i][0], positions[i][1]), fontsize=12)
    else:
        for i in range(len(positions)):
            # if positions[i][2] > 0:
            #     n=str(str(CargoLoaded_Nbr[i])+'.'+str(1))
            # else:
            #     n=str(CargoLoaded_Nbr[i])
            n=str(CargoLoaded_Nbr[i])
            #ax.text(positions[i][0], positions[i][1], positions[i][2], n, fontsize=FontSize, color = "#FF0000", zorder=100)
            #ax.text(positions[i][0], positions[i][1], positions[i][2], n, fontsize=FontSize, zorder=500)
            ax.text(positions[i][0]+sizes[i][0], positions[i][1]+sizes[i][1]/2, positions[i][2]+sizes[i][2]/2, n, fontsize=FontSize, zorder=500, color = "#FFFFFF")
            #ax.annotate(n, xyz = (positions[i][0], positions[i][1]), fontsize=12)
            
    ax.set_xlim([0,TruckL])
    ax.set_ylim([0,TruckW])
    ax.set_zlim([0,TruckH])
    if angle == 1:
        ax.view_init(25, -20)
    if angle == 2:
        ax.view_init(25, 20)
    if angle == 3:
        ax.view_init(25, 0)
    plt.show()
    
    # fig.savefig(path1+'\Plan1_Fig1.svg', transparent=False, bbox_inches='tight') #Save in svg format
    fig.savefig('Or_'+str(TotalCargoLoaded)+'.pdf', bbox_inches='tight', pad_inches=0)
    #fig.savefig(path1+'\plot'+str(TotalCargoLoaded)+'.svg', bbox_inches='tight', pad_inches=0)
    #fig.savefig('plot'+str(TotalCargoLoaded)+'.pdf', bbox_inches='tight', pad_inches=0) 
    return 1


############################################################################################################



def OneByOnePlot(PlotSolNbr, ContainerData, angle, CalledFrom):       
    
    # Delete all pdf files starting with OR_* generated so far
    for filename in glob.glob("Or_*"):
        os.remove(filename) 
    
    # # 1 Read Input Data File Based on the version of the algorithm (CalledFrom value)
    
    # # 1.2 When both grouping and only aggcargo are considered
    # if CalledFrom == 0:
    #     File = pd.ExcelFile('AllFeasibleSolutions.xlsx')
    
    #     # Solution
    #     AllSol = pd.read_excel(File, 'AllFeasSols')
    #     FinalSol = AllSol[AllSol['SolutionNbr'] == PlotSolNbr]
    #     FinalSol = FinalSol.sort_values(by=['LoadingOrder'], ascending=[True])
    #     FinalSol.reset_index(drop=True, inplace=True)
    #     FinalSol.rename(columns={'Sno':'CargoNbr'}, inplace=True)
    
    # # 1.3 When both grouping and discargo are considered
    # if CalledFrom == 1:
        # Load saved dictionary
    File = 'DetailsAllSolutions.csv'
    AllFeasibleSolutions = pd.read_csv(File)  
    FinalSol = AllFeasibleSolutions.loc[AllFeasibleSolutions['SolNbr'] == PlotSolNbr]
    FinalSol = FinalSol.sort_values(by=['x', 'z', 'y'], ascending=[True, True, True])
    FinalSol.reset_index(drop=True, inplace=True)
    FinalSol.rename(columns={'Sno':'CargoNbr'}, inplace=True)
    
    
    #print(FinalSol)
    #input('Press Enter')
    
    # colors_All = [  "#B0171F",	"#DC143C",	"#8B5F65",	"#CD3278",	"#8B2252",	"#872657",	"#FF1493",	"#CD1076",	"#8B0A50",	"#C71585",
    #             "#4B0082",	"#8A2BE2",	"#473C8B",	"#0000FF",	"#000080",	"#1E90FF",	"#104E8B",	"#00688B",	"#00E5EE",	"#2F4F4F",
    #             "#79CDCD",	"#008B8B",	"#20B2AA",	"#00C78C",	"#00FA9A",	"#00FF7F",	"#008B45",	"#00C957",	"#32CD32",	"#228B22",
    #             "#00FF00",	"#006400",	"#308014",	"#66CD00",	"#458B00",	"#698B22",	"#FFFF00",	"#8B8B00",	"#808069",	"#808000",
    #             "#BDB76B",	"#F0E68C",	"#FFD700",	"#CDAD00",	"#8B7500",	"#DAA520",	"#EEB422",	"#8B6914",	"#FFB90F",	"#CD950C",
    #             "#8B6508",	"#CD8500",	"#8B5A00",	"#FF9912",	"#8B4500",	"#FF8000",	"#292421",	"#FF7D40",	"#FF6103",	"#8A360F",
    #             "#FF4500",	"#CD5B45",	"#8B3A3A",	"#CD5555",	"#A52A2A",	"#8B2323",	"#B22222",	"#FF0000",	"#8B0000",	"#8E388E",
    #             "#7171C6",	"#7D9EC0",	"#388E8E",	"#71C671",	"#8E8E38",	"#C67171",	"#8B008B",	"#9400D3",	"#551A8B",	"#6A5ACD",
    #             "#0000EE",	"#191970",	"#27408B",	"#1874CD",	"#4682B4",	"#5CACEE",	"#36648B",	"#87CEEB",	"#00BFFF",	"#009ACD",
    #             "#53868B",	"#00C5CD",	"#00868B",	"#668B8B",	"#008080",	"#00CD66",	"#2E8B57",	"#8B8878",	"#FFC125",	"#CD9B1D",
    #             "#B8860B",	"#8B795E",	"#9C661F",	"#CD6600",	"#8B7765",	"#C76114",	"#8B4513",	"#EE4000",	"#8B4C39",	"#8B3626",
    #             "#CD5C5C",	"#CD3333",	"#800000",	"#525252"]    

    number_of_colors = FinalSol.shape[0]
    colors_All = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                  for i in range(number_of_colors)]
    
    TruckL, TruckW, TruckH = ContainerData['L'][0], ContainerData['W'][0], ContainerData['H'][0]
    
    source_dir = os.getcwd()
    
    path = os.getcwd()
    
    j = -1
    for k in range(FinalSol.shape[0]):    
        positions = []
        sizes = []
        colors = []
        CargoLoaded_Nbr = []
        
        # random_number = random.randint(0,16777215)
        # hex_number = str(hex(random_number))
        # hex_number ='#'+ hex_number[2:]
        # #TempColor = f'"{hex_number.upper()}"'
        # TempColor = hex_number      
        
        for i in range(k+1):
            colors.append(colors_All[i])
            
        for i in range(k+1):
            positions.append(tuple((FinalSol['x'][i], FinalSol['y'][i], FinalSol['z'][i])))            
            sizes.append(tuple((FinalSol['l'][i], FinalSol['w'][i], FinalSol['h'][i])))            
            CargoLoaded_Nbr.append(FinalSol['CargoNbr'][i]) 
        
        done = Draw_GraphicalSol1(k+1, positions, sizes, CargoLoaded_Nbr, colors, TruckL, TruckW, TruckH, path, angle)
        #print('Till Boxes: %d'%(k+1))
    
    for j in range(FinalSol.shape[0]):
        filename = "Or_"+str(j+1)+".pdf"

        with open(filename, "rb") as in_f:
            input1 = PdfFileReader(in_f)
            output = PdfFileWriter()
        
            numPages = input1.getNumPages()
        
            for i in range(numPages):
                page = input1.getPage(i)
                if angle == 1:
                    page.cropBox.lowerLeft = (50, 40)
                    page.cropBox.lowerRight = (275, 40)
                    page.cropBox.upperLeft = (50, 270)
                    page.cropBox.upperRight = (275, 270)

                if angle == 2:
                    page.cropBox.lowerLeft = (40, 90)
                    page.cropBox.lowerRight = (260, 90)
                    page.cropBox.upperLeft = (40, 310)
                    page.cropBox.upperRight = (260, 310)

                if angle == 3:
                    page.cropBox.lowerLeft = (80, 60)
                    page.cropBox.lowerRight = (200, 60)
                    page.cropBox.upperLeft = (80, 295)
                    page.cropBox.upperRight = (200, 295)                    
                    
                output.addPage(page)
            
            outfile = "Or_"+str(j+1)+"_f.pdf"
            with open(outfile, "wb") as out_f:
                output.write(out_f)
                    
    merger = PdfFileMerger()
    
    item = os.listdir(source_dir)
    for j in range(FinalSol.shape[0]+1):
        for k in range(len(item)):
            if item[k] == str("Or_"+str(j)+"_f.pdf"):
                # print('Yes')
                merger.append(item[k])

            
    # for item in os.listdir(source_dir):
    #     if item.endswith('_f.pdf'):
    #         merger.append(item)
    
    merger.write("Plot "+str(angle)+"_SolNbr = "+str(PlotSolNbr)+".pdf")    
    merger.close()   
    # if CalledFrom == 0 or CalledFrom ==1:
    #     File.close()
    
    for filename in glob.glob("Or_*"):
        os.remove(filename) 
    #path = 'G:\My Drive\11_Internship Project_Freight Consolidation and Bin Packing\ConstSet2\Algo1'
    
        