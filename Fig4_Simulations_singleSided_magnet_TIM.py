#

import scipy.io
import numpy as np
import magpylib as magpy
import matplotlib.pyplot as plt
from multiprocessing.pool import ThreadPool

#%matplotlib auto

GAMMA_KHZ_PER_MTESLA = 42.577  # gyromagnetic ratio in kHz/mT
rf_vs_magnet_distance = 31 #mm. The gap between the RF coil and the barrel magnet.

def plotBPathBarrel(axis, start, stop, count, bLineStartCoordinate, dim):
    
    """
    Parameters:
        axis: str
            The axis along which the B field is to be plotted

        start: float
            The start point of the axis line

        stop: float
            The end point of the axis line

        count: int
            The number of points to be plotted

        bLineStartCoordinate: list
            The starting coordinate of the line along which the B field is to be plotted

        dim: list
            The dimensions of the magnet (diameter, height)
        
        Returns:
            bLine: list
                The x-axis values for the B field plot
            bZ: list
                The B field values for the total B field plot

    Purpose:
        This function plots the B field along the axis specified by the user. 
        The B field is plotted from the start point to the end point with the specified number of points. 
        The starting coordinate of the line is also specified by the user.

    """
    
    temp = ['x','y','z']
    axisIndex = temp.index(axis)
    
    bLine = np.linspace(start, stop, count)
    b1,b2,b3 = [],[],[]
    mag = np.array([(0,0,1150), (0,0,-1150), (0,0,1150)])
    for el in bLine:
        temp = bLineStartCoordinate.copy()
        temp[axisIndex] = el
        obs = np.array([(temp[0],temp[1],temp[2]), (temp[0],temp[1],temp[2]), (temp[0],temp[1],temp[2])])
        B = magpy.core.magnet_cylinder_field('B', obs, mag, dim)
        
        b1.append(B[0])
        b2.append(B[1])
        b3.append(B[2])
    b = np.array(b1) + np.array(b2) + np.array(b3)
    return bLine, b


def runBarrelSim():
    #plt.cla()
    plt.figure()
    postHeights = [45,43,41,39,37]
      
    # This plots the B field along the z axis at various post heights
    for postHeight in postHeights:
        dim = np.array([(102,50.8), (50.8,50.8), (25.4,postHeight)])
        temp = plotBPathBarrel('z', rf_vs_magnet_distance, 60, 1000, [0,0,0],dim)
        temp2 = temp[1] * GAMMA_KHZ_PER_MTESLA
        plt.plot(temp[0] - rf_vs_magnet_distance, temp2[:,2],linewidth=3)
    plt.title('B field along the z axis from 0 to 30mm of various post lengths\nBarrel + Post Magnet')
    plt.legend(['postLength=45mm','postLength=43mm','postLength=41mm','postLength=39mm','postLength=37mm'])
    plt.xlabel('z (mm)')
    plt.ylabel('F nmr (KHz)')
    plt.grid()
    plt.show()

    #plt.cla()
    plt.figure()
    
    # This plots the B field along the x axis at various z heights
    #dim = np.array([(102,50.8), (50.8,50.8), (25.4,39.2)])
    dim = np.array([(102,50.8), (50.8,50.8), (25.4,41)])
    bZs = []
    bLine = []
    z = [37, 39,41,43,45]
    for el in z:
        temp = plotBPathBarrel('x', -15, 15, 1000, [0,0,el],dim)
        temp2 = temp[1] * GAMMA_KHZ_PER_MTESLA
        bZs.append(temp2[:,2])
        bLine.append(temp[0])
        plt.plot(temp[0], temp2[:,2],linewidth = 3, label = "z = " + str(el - rf_vs_magnet_distance))
    plt.title('B field along the x axis from -15 to 15mm at various z heights\nBarrel Magnet')
    plt.legend()
    plt.xlabel('x (mm)')
    plt.ylabel('B (KHz)')
    plt.grid()
    plt.show()


# NEW: continuous colormap of resonance frequencies over (z, r)

def frequency_map_barrel(postHeight, z_min=rf_vs_magnet_distance, z_max=60, z_pts=601, r_min=-25, r_max=25, r_pts=201, centerFreq=5360, bandwidth=50):
    """
    Compute resonance frequency (kHz) at each (z, r) and render a colormap.
    Also overlay the in-band contour for the given center frequency and bandwidth.
    """
    # Grid
    zs = np.linspace(z_min, z_max, z_pts)
    rs = np.linspace(r_min, r_max, r_pts)
    Z, R = np.meshgrid(zs, rs, indexing='xy')


    #Position the magnet: A ring magnet is equivalent to two magnet bars where one of them has "negative" magnetization
    #Example: barrel and inner magnets stay at origin
    barrel = magpy.magnet.Cylinder(magnetization=(0,0,1150), dimension=(102.0, 50.8), position=(0,0,0))
    inner  = magpy.magnet.Cylinder(magnetization=(0,0,-1150), dimension=(50.8, 50.8), position=(0,0,0))
    
    # Rod magnet shifted UP by +10 mm along z
    rod_offset_z = 0  # mm. put 10 mm to reproduce Utsuzawa
    bar = magpy.magnet.Cylinder(magnetization=(0,0,1150), dimension=(25.4, postHeight), position=(0,0,rod_offset_z))
    
    assembly = magpy.Collection(barrel, inner, bar)
    #HBU: end of reproducing Utsuzawa positioning


    # --- Your original grid loop, edited to use assembly.getB() ---
    # Compute Bz (sum from all sources via the collection); shape (r_pts, z_pts)
    F = np.empty((r_pts, z_pts))
    for j in range(z_pts):
        for i in range(r_pts):
            x, y, z = rs[i], 0.0, zs[j]
            B_vec = assembly.getB((x, y, z))     # (Bx, By, Bz) in mT
            F[i, j] = GAMMA_KHZ_PER_MTESLA * B_vec[2]  # frequency (kHz) from Bz

    print('Median freq in ROI', np.median(F))


    # Plot colormap
    plt.figure(figsize=(6,12))
    # Use pcolormesh for faster rendering; need 2D arrays of the same shape
    pcm = plt.pcolormesh(Z - rf_vs_magnet_distance, R, F, shading='auto', cmap='viridis', vmin=np.median(F)-2*bandwidth, vmax=np.median(F)+2*bandwidth)
    cbar = plt.colorbar(pcm)
    cbar.set_label('Resonance frequency (kHz)')

    # Overlay in-band contour
    lower, upper = centerFreq - bandwidth/2, centerFreq + bandwidth/2
    
    
    levels = [lower, upper]
    cs = plt.contour(Z - rf_vs_magnet_distance, R, F, levels=levels, colors=['white','white'], linestyles=['--','--'], linewidths=3)

    plt.xlabel('z (mm)')
    plt.ylabel('r (mm)')
    plt.title(f'Resonance frequency map (kHz) for Barrel + Post Magnet\nPost length {postHeight} mm; center {centerFreq} kHz')

    # Axis ticks similar to original
    plot_z_min = z_min - rf_vs_magnet_distance
    plot_z_max = z_max - rf_vs_magnet_distance
    major_ticks_z = np.arange(plot_z_min, plot_z_max+0.1, 5)
    minor_ticks_z = np.arange(plot_z_min, plot_z_max+0.1, 2.5)
    plt.xticks(major_ticks_z)
    plt.minorticks_on()
    plt.grid(which='both', alpha=0.3)

    plt.show()


def runZVsRBarrelMagSims():
    pool = ThreadPool(processes=8)
    # Render the colormap instead of binary scatter
    postHeights = [41]
    centerFreq = 5360  # change to your operating frequency as needed
    bandwidth = 50
    for ph in postHeights:
        frequency_map_barrel(postHeight=ph, centerFreq=centerFreq, bandwidth=bandwidth)


if __name__ == '__main__':
    runBarrelSim()
    runZVsRBarrelMagSims()