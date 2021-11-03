import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import proj3d
import numpy as np
import time
from PyPDF2 import PdfFileWriter, PdfFileReader

DotSize = 2.5
FontSize = 5.0

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
        ax.plot_surface(X, Y, Z, alpha=0.1, rstride=1, cstride=1, edgecolor ='k', linewidth=0.5, **kwargs)

def plotCubeAt2(pos=(0,0,0), size=(1,1,1), ax=None, **kwargs):
    # Plotting a cube element at position pos
    if ax !=None:
        X, Y, Z = cuboid_data( pos, size )
        ax.plot_surface(X, Y, Z, alpha=0.5, rstride=1, cstride=1, edgecolor ='w', linewidth=0.1, **kwargs)


def Draw_GraphicalSol1(TotalCargoLoaded, positions, sizes, CargoLoaded_Nbr, colors, TruckL, TruckW, TruckH, path1):
    # positions = [(0,0,0),(0,1,0),(0,5,0),(2,0,0)]
    # sizes = [(2,1,1), (2,4,1),(5,2,3),(4,10,2)]
    # colors = ["#99CCFF1A","#FF80001A","#0066CC1A", "#0000001A"]
    
    
    fig = plt.figure(figsize=(50,10))
    #fig = plt.figure()
    #fig = plt.figure()
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
    # draw a point
    for i in range(len(positions)):
        if positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#0000FF', s=DotSize)
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF0000', s=DotSize)
        elif positions[i][0] == 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#00FF00', s=DotSize)
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFFF00', s=DotSize)
        elif positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#008000', s=DotSize)        
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF00FF', s=DotSize)        
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFA500', s=DotSize)        
        else:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#000000', s=DotSize)        

              
    # Add text
    n = ''
    for i in range(len(positions)):
        # if positions[i][2] > 0:
        #     n=str(str(CargoLoaded_Nbr[i])+'.'+str(1))
        # else:
        #     n=str(CargoLoaded_Nbr[i])
        n=str(CargoLoaded_Nbr[i])
        ax.text(positions[i][0], positions[i][1], positions[i][2], n, fontsize=FontSize, zorder=100)
        #ax.annotate(n, xyz = (positions[i][0], positions[i][1]), fontsize=12)
    
    
    
    for p,s,c in zip(positions,sizes,colors):
        plotCubeAt1(pos=p, size=s, ax=ax, color=c)
        
    ax.set_xlim([0,TruckL])
    ax.set_ylim([0,TruckW])
    ax.set_zlim([0,TruckH])
    ax.view_init(20, -30)
    plt.show()
    
    # fig.savefig(path1+'\Plan1_Fig1.svg', transparent=False, bbox_inches='tight') #Save in svg format
    fig.savefig(path1+'\plot1_1.pdf', bbox_inches='tight', pad_inches=0)
    
    #fig.savefig("Fig_Code2") #Save in svg format

# def Draw_GraphicalSol1(TotalCargoLoaded, positions, sizes, CargoLoaded_Nbr, colors, TruckL, TruckW, TruckH, path1):
#     # positions = [(0,0,0),(0,1,0),(0,5,0),(2,0,0)]
#     # sizes = [(2,1,1), (2,4,1),(5,2,3),(4,10,2)]
#     # colors = ["#99CCFF1A","#FF80001A","#0066CC1A", "#0000001A"]
    
    
#     fig = plt.figure(figsize=(50,10))
#     #fig = plt.figure()
#     #fig = plt.figure()
#     ax = fig.gca(projection='3d')
#     ax.set_aspect('auto')
#     ax.tick_params(axis='both', which='major', labelsize=5)
#     ax.tick_params(axis='both', which='minor', labelsize=2)
#     #ax.get_proj = lambda: np.dot(Axes3D.get_proj(ax), np.diag([2, 1, 1, 1]))
    
#     """                                                                                                                                                    
#     Scaling begin
#     """
#     x_scale=5
#     y_scale=1
#     z_scale=1
    
#     scale=np.diag([x_scale, y_scale, z_scale, 1.0])
#     scale=scale*(1.0/scale.max())
#     scale[3,3]=1.0
    
#     def short_proj():
#       return np.dot(Axes3D.get_proj(ax), scale)
    
#     ax.get_proj=short_proj
#     """                                                                                                                                                    
#     Scaling end                                                                                                                                                
#     """

       
#     """
#     Begin: Grid lines settings
#     """
#     ax.xaxis._axinfo["grid"].update({"linewidth":0.5, "color" : "w"})
#     ax.yaxis._axinfo["grid"].update({"linewidth":0.5, "color" : "w"})
#     ax.zaxis._axinfo["grid"].update({"linewidth":0.5, "color" : "w"})
#     # ax.yaxis._axinfo["grid"]['linewidth'] = 3.
#     # ax.zaxis._axinfo["grid"]['color'] = "#ee0009"
#     # ax.zaxis._axinfo["grid"]['linestyle'] = ":"
#     """
#     End: Grid lines settings
#     """
    
#     '''
#     '#0000FF': Blue (>0,0,0)
    
#     '''
#     # draw a point
#     for i in range(len(positions)):
#         if positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] == 0:
#             ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#0000FF', s=DotSize)
#         elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] == 0:
#             ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF0000', s=DotSize)
#         elif positions[i][0] == 0 and positions[i][1] == 0 and positions[i][2] > 0:
#             ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#00FF00', s=DotSize)
#         elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] == 0:
#             ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFFF00', s=DotSize)
#         elif positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] > 0:
#             ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#008000', s=DotSize)        
#         elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] > 0:
#             ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF00FF', s=DotSize)        
#         elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] > 0:
#             ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFA500', s=DotSize)        
#         else:
#             ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#000000', s=DotSize)        

              
#     # Add text
#     n = ''
#     for i in range(len(positions)):
#         # if positions[i][2] > 0:
#         #     n=str(str(CargoLoaded_Nbr[i])+'.'+str(1))
#         # else:
#         #     n=str(CargoLoaded_Nbr[i])
#         n=str(CargoLoaded_Nbr[i])
#         ax.text(positions[i][0], positions[i][1], positions[i][2], n, fontsize=FontSize, zorder=100)
#         #ax.annotate(n, xyz = (positions[i][0], positions[i][1]), fontsize=12)
    
    
    
#     for p,s,c in zip(positions,sizes,colors):
#         plotCubeAt1(pos=p, size=s, ax=ax, color=c)
        
#     ax.set_xlim([0,TruckL])
#     ax.set_ylim([0,TruckW])
#     ax.set_zlim([0,TruckH])
    
#     plt.show()
    
#     fig.savefig(path1+'\Plan1_Fig1.svg', transparent=False, bbox_inches='tight') #Save in svg format
#     fig.savefig(path1+'\Plan1_Fig1.png', transparent=False, bbox_inches='tight') #Save in svg format
#     #fig.savefig(path1+'\Plan1_Fig1.svg') #Save in svg format
#     fig.savefig(path1+'\plot.pdf', bbox_inches='tight', pad_inches=0)
    
#     #fig.savefig("Fig_Code2") #Save in svg format

##############################################################################
def Draw_GraphicalSol2(TotalCargoLoaded, positions, sizes, CargoLoaded_Nbr, colors, TruckL, TruckW, TruckH, path1):
    # positions = [(0,0,0),(0,1,0),(0,5,0),(2,0,0)]
    # sizes = [(2,1,1), (2,4,1),(5,2,3),(4,10,2)]
    # colors = ["#99CCFF1A","#FF80001A","#0066CC1A", "#0000001A"]
    
    
    fig = plt.figure(figsize=(50,10))
    #fig = plt.figure()
    #fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_aspect('auto')
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
    # draw a point
    for i in range(len(positions)):
        if positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#0000FF', s=DotSize, zorder=1000)
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF0000', s=DotSize, zorder=1000)
        elif positions[i][0] == 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#00FF00', s=DotSize, zorder=1000)
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFFF00', s=DotSize, zorder=1000)
        elif positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#008000', s=DotSize, zorder=1000)        
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF00FF', s=DotSize, zorder=1000)        
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFA500', s=DotSize, zorder=1000)        
        else:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#000000', s=DotSize, zorder=1000)        

              
    # Add text
    n = ''
    for i in range(len(positions)):
        # if positions[i][2] > 0:
        #     n=str(str(CargoLoaded_Nbr[i])+'.'+str(1))
        # else:
        #     n=str(CargoLoaded_Nbr[i])
        n=str(CargoLoaded_Nbr[i])
        ax.text(positions[i][0], positions[i][1], positions[i][2], n, fontsize=FontSize, color = "#FF0000", zorder=100)
        #ax.annotate(n, xyz = (positions[i][0], positions[i][1]), fontsize=12)
    
    
    
    for p,s,c in zip(positions,sizes,colors):
        plotCubeAt2(pos=p, size=s, ax=ax, color=c)
        
    ax.set_xlim([0,TruckL])
    ax.set_ylim([0,TruckW])
    ax.set_zlim([0,TruckH])
    ax.view_init(20, -30)
    plt.show()
    # fig.savefig(path1+"\Plan1_Fig2.svg", transparent=True, bbox_inches='tight') #Save in svg format
    #fig.savefig("Fig_Code2") #Save in svg format
    fig.savefig(path1+'\plot1_2.pdf', bbox_inches='tight', pad_inches=0)
    
##############################################################################
def Draw_GraphicalSol3(TotalCargoLoaded, positions, sizes, CargoLoaded_Nbr, colors, TruckL, TruckW, TruckH, path1):
    # positions = [(0,0,0),(0,1,0),(0,5,0),(2,0,0)]
    # sizes = [(2,1,1), (2,4,1),(5,2,3),(4,10,2)]
    # colors = ["#99CCFF1A","#FF80001A","#0066CC1A", "#0000001A"]
    
    
    fig = plt.figure(figsize=(50,10))
    #fig = plt.figure()
    #fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_aspect('auto')
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
    # draw a point
    for i in range(len(positions)):
        if positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#0000FF', s=DotSize)
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF0000', s=DotSize)
        elif positions[i][0] == 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#00FF00', s=DotSize)
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFFF00', s=DotSize)
        elif positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#008000', s=DotSize)        
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF00FF', s=DotSize)        
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFA500', s=DotSize)        
        else:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#000000', s=DotSize)        

              
    # Add text
    n = ''
    for i in range(len(positions)):
        # if positions[i][2] > 0:
        #     n=str(str(CargoLoaded_Nbr[i])+'.'+str(1))
        # else:
        #     n=str(CargoLoaded_Nbr[i])
        n=str(CargoLoaded_Nbr[i])
        ax.text(positions[i][0], positions[i][1], positions[i][2], n, fontsize=FontSize, zorder=100)
        #ax.annotate(n, xyz = (positions[i][0], positions[i][1]), fontsize=12)
    
    
    
    for p,s,c in zip(positions,sizes,colors):
        plotCubeAt1(pos=p, size=s, ax=ax, color=c)
        
    ax.set_xlim([0,TruckL])
    ax.set_ylim([0,TruckW])
    ax.set_zlim([0,TruckH])
    ax.view_init(30, 45)
    plt.show()
    # fig.savefig(path1+"\Plan1_Fig3.svg", transparent=True, bbox_inches='tight') #Save in svg format
    #fig.savefig("Fig_Code2") #Save in svg format
    fig.savefig(path1+'\plot2_1.pdf', bbox_inches='tight', pad_inches=0)

##############################################################################
def Draw_GraphicalSol4(TotalCargoLoaded, positions, sizes, CargoLoaded_Nbr, colors, TruckL, TruckW, TruckH, path1):
    # positions = [(0,0,0),(0,1,0),(0,5,0),(2,0,0)]
    # sizes = [(2,1,1), (2,4,1),(5,2,3),(4,10,2)]
    # colors = ["#99CCFF1A","#FF80001A","#0066CC1A", "#0000001A"]
    
    
    fig = plt.figure(figsize=(50,10))
    #fig = plt.figure()
    #fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_aspect('auto')
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
    # draw a point
    for i in range(len(positions)):
        if positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#0000FF', s=DotSize, zorder=100)
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF0000', s=DotSize, zorder=100)
        elif positions[i][0] == 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#00FF00', s=DotSize, zorder=100)
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFFF00', s=DotSize, zorder=100)
        elif positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#008000', s=DotSize, zorder=100)        
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF00FF', s=DotSize, zorder=100)        
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFA500', s=DotSize, zorder=100)        
        else:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#000000', s=DotSize, zorder=100)        

              
    # Add text
    n = ''
    for i in range(len(positions)):
        # if positions[i][2] > 0:
        #     n=str(str(CargoLoaded_Nbr[i])+'.'+str(1))
        # else:
        #     n=str(CargoLoaded_Nbr[i])
        n=str(CargoLoaded_Nbr[i])
        ax.text(positions[i][0], positions[i][1], positions[i][2], n, fontsize=FontSize, color = "#FF0000", zorder=100)
        #ax.annotate(n, xyz = (positions[i][0], positions[i][1]), fontsize=12)
    
    
    
    for p,s,c in zip(positions,sizes,colors):
        plotCubeAt2(pos=p, size=s, ax=ax, color=c)
        
    ax.set_xlim([0,TruckL])
    ax.set_ylim([0,TruckW])
    ax.set_zlim([0,TruckH])
    ax.view_init(30, 45)
    plt.show()
    # fig.savefig(path1+"\Plan1_Fig4.svg", transparent=True, bbox_inches='tight') #Save in svg format
    #fig.savefig("Fig_Code2") #Save in svg format
    fig.savefig(path1+'\plot2_2.pdf', bbox_inches='tight', pad_inches=0)
    
##############################################################################
def Draw_GraphicalSol5(TotalCargoLoaded, positions, sizes, CargoLoaded_Nbr, colors, TruckL, TruckW, TruckH, path1):
    # positions = [(0,0,0),(0,1,0),(0,5,0),(2,0,0)]
    # sizes = [(2,1,1), (2,4,1),(5,2,3),(4,10,2)]
    # colors = ["#99CCFF1A","#FF80001A","#0066CC1A", "#0000001A"]
    
    
    fig = plt.figure(figsize=(50,10))
    #fig = plt.figure()
    #fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_aspect('auto')
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
    # draw a point
    for i in range(len(positions)):
        if positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#0000FF', s=DotSize)
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF0000', s=DotSize)
        elif positions[i][0] == 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#00FF00', s=DotSize)
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFFF00', s=DotSize)
        elif positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#008000', s=DotSize)        
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF00FF', s=DotSize)        
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFA500', s=DotSize)        
        else:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#000000', s=DotSize)        

              
    # Add text
    n = ''
    for i in range(len(positions)):
        # if positions[i][2] > 0:
        #     n=str(str(CargoLoaded_Nbr[i])+'.'+str(1))
        # else:
        #     n=str(CargoLoaded_Nbr[i])
        n=str(CargoLoaded_Nbr[i])
        ax.text(positions[i][0], positions[i][1], positions[i][2], n, fontsize=FontSize, zorder=100)
        #ax.annotate(n, xyz = (positions[i][0], positions[i][1]), fontsize=12)
    
    
    
    for p,s,c in zip(positions,sizes,colors):
        plotCubeAt1(pos=p, size=s, ax=ax, color=c)
        
    ax.set_xlim([0,TruckL])
    ax.set_ylim([0,TruckW])
    ax.set_zlim([0,TruckH])
    ax.view_init(90, 0)
    plt.show()
    # fig.savefig(path1+"\Plan1_Fig5.svg", transparent=True, bbox_inches='tight') #Save in svg format
    #fig.savefig("Fig_Code2") #Save in svg format
    fig.savefig(path1+'\plot3_1.pdf', bbox_inches='tight', pad_inches=0)

##############################################################################
def Draw_GraphicalSol6(TotalCargoLoaded, positions, sizes, CargoLoaded_Nbr, colors, TruckL, TruckW, TruckH, path1):
    # positions = [(0,0,0),(0,1,0),(0,5,0),(2,0,0)]
    # sizes = [(2,1,1), (2,4,1),(5,2,3),(4,10,2)]
    # colors = ["#99CCFF1A","#FF80001A","#0066CC1A", "#0000001A"]
    
    
    fig = plt.figure(figsize=(50,10))
    #fig = plt.figure()
    #fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_aspect('auto')
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
    # draw a point
    for i in range(len(positions)):
        if positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#0000FF', s=DotSize, zorder=100)
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF0000', s=DotSize, zorder=100)
        elif positions[i][0] == 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#00FF00', s=DotSize, zorder=100)
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] == 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFFF00', s=DotSize, zorder=100)
        elif positions[i][0] > 0 and positions[i][1] == 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#008000', s=DotSize, zorder=100)        
        elif positions[i][0] == 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FF00FF', s=DotSize, zorder=100)        
        elif positions[i][0] > 0 and positions[i][1] > 0 and positions[i][2] > 0:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#FFA500', s=DotSize, zorder=100)        
        else:
            ax.scatter([positions[i][0]], [positions[i][1]], [positions[i][2]], color='#000000', s=DotSize, zorder=100)        

              
    # Add text
    n = ''
    for i in range(len(positions)):
        # if positions[i][2] > 0:
        #     n=str(str(CargoLoaded_Nbr[i])+'.'+str(1))
        # else:
        #     n=str(CargoLoaded_Nbr[i])
        n=str(CargoLoaded_Nbr[i])
        ax.text(positions[i][0], positions[i][1], positions[i][2], n, fontsize=FontSize, color = "#FF0000", zorder=100)
        #ax.annotate(n, xyz = (positions[i][0], positions[i][1]), fontsize=12)
    
    
    
    for p,s,c in zip(positions,sizes,colors):
        plotCubeAt2(pos=p, size=s, ax=ax, color=c)
        
    ax.set_xlim([0,TruckL])
    ax.set_ylim([0,TruckW])
    ax.set_zlim([0,TruckH])
    ax.view_init(90, 0)
    plt.show()
    # fig.savefig(path1+"\Plan1_Fig6.svg", transparent=True, bbox_inches='tight') #Save in svg format
    #fig.savefig("Fig_Code2") #Save in svg format
    fig.savefig(path1+'\plot3_2.pdf', bbox_inches='tight', pad_inches=0)