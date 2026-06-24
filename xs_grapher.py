
import numpy as np
import matplotlib.lines  as lns  # To get list of filled markers
import matplotlib.pyplot as plt  # To plot
import matplotlib.ticker as tkr  # To manage axis tickmark styling
import processargs
import sys
import random  # For random selection of marker types

#
# ============= Graph values to tweak =============
#
# Comment out a variable to assume automatic value assignment

ELims=np.array([7.5,20])   # in MeV
xsLims=np.array([0.01,500])  # in mb
graphTitle=r'$^{181}$'+r'Ta'+r'('+r'$\gamma$'+r',x)'+r'$^{180}$'+r'Ta'
legendLocation='upper right'
figDimensions=(12,9)
minorEticks=np.array([])  # in MeV
minorXSticks=np.array([]) # in mb
EtickSubs=np.array([8, 9, 10, 12.5, 15, 20])
XStickSubs=np.array([2.5, 5])

# zoomBounds      Row1=[Emin,Emax] of region to zoom in on [MeV]
# zoomBounds      Row2=[XSmin,XSmax] of region to zoom in on [mb]
#
# zoomDispLoc     Row1=[E,width]; E=energy (MeV) where lower left 
#                                 corner of zoom image will go.
#                                 Width is box width in mb
# zoomDispLoc     Row2=[xs,height]; xs=cross section (mb) where
#                                  lower left corner of zoom image
#                                  goes. Height is box height in mb
zoomBounds= np.array([ [12.2,12.4],[300, 450] ])
zoomDispLoc=np.array([ [12.5,5], [0.25,24.75] ])

# Make sure theres something defined for these lists
markerList=['.','v','^','H','p']
lineStyleList=['-','--','-.',':']
colorList=[
    '#000fff',"#ff0000","#fe6bb9","#165700",
    "#9000ff","#000000","#ffaa00"
]

#
# =================================================
#

def sampleNoReplacement(set: list) -> str:
    """
    Sample a marker type with no replacement
    """
    marker=random.choice(set)
    set.remove(marker)
    return marker


# Call processing script to read in data and make sense of flags
showPlot, dataSets = processargs.xsprocess(sys.argv)

# Initialize graph
try:
    fig, ax = plt.subplots(figsize=figDimensions)
except NameError:
    fix, ax = plt.subplots()

# If zoom box specified, deal with that
zoomBox=False
try:
    zoomDispLoc[0,:]*=1e6
    zoomDispLoc[1,:]/=1e3
    zoomDispLoc=zoomDispLoc.transpose()
    axins=ax.inset_axes(
        bounds=[*zoomDispLoc[0], *zoomDispLoc[1]],
        transform=ax.transData,
        xlim=zoomBounds[0]*1e6, ylim=zoomBounds[1]/1e3
    )
    ax.indicate_inset_zoom(axins, edgecolor='black')
    axins.set_xscale('log')
    axins.set_yscale('log')
    axins.xaxis.grid(which='both', linewidth=0.4)
    axins.yaxis.grid(which='both', linewidth=0.4)
    axins.xaxis.set_major_formatter(tkr.EngFormatter(unit='eV'))
    axins.yaxis.set_major_formatter(tkr.EngFormatter(unit='b'))
    axins.xaxis.set_minor_formatter(tkr.EngFormatter(unit='eV'))
    axins.yaxis.set_minor_formatter(tkr.EngFormatter(unit='b'))
    axins.xaxis.set_minor_locator(tkr.LogLocator())
    axins.yaxis.set_minor_locator(tkr.LinearLocator())
    axins.xaxis.set_ticks(zoomBounds[0]*1e6)
    axins.yaxis.set_ticks(zoomBounds[1]/1e3)
    zoomBox=True
except NameError:
    pass


lineWidth=1.25 # decrement this for every additional line graphed
for name, set in dataSets.items():
    data, isLine = set
    E, dE, xs, dxs = data
    
    # Sample random styling (marker, line)
    if (isLine):
        markerStyle=''
        markerSize=None 
        lineStyle=sampleNoReplacement(lineStyleList)
    else:
        markerStyle=sampleNoReplacement(markerList)
        markerSize=None
        lineStyle=''

    color=sampleNoReplacement(colorList)
    
    # For zoombox if specified
    if (zoomBox):
        axins.errorbar(
        x=E*1e6, y=xs/1e3, xerr=dE*1e6, yerr=dxs/1e3,
        label=name, ls=lineStyle, linewidth=lineWidth,
        marker=markerStyle, markersize=markerSize,
        c=color
        )

    # For main plot
    ax.errorbar(
        x=E*1e6, y=xs/1e3, xerr=dE*1e6, yerr=dxs/1e3,
        label=name, ls=lineStyle, linewidth=lineWidth,
        marker=markerStyle, markersize=markerSize,
        c=color
    )

    
    
    if (isLine):
        lineWidth-=0.1


# Set some fixed settings for all graph scenarios
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Energy', fontsize=14)
ax.set_ylabel('Cross section',fontsize=14)
ax.xaxis.grid(which='both', linewidth=0.4)
ax.yaxis.grid(which='both', linewidth=0.4)
ax.xaxis.set_major_formatter(tkr.EngFormatter(unit='eV'))
ax.yaxis.set_major_formatter(tkr.EngFormatter(unit='b'))
ax.xaxis.set_minor_formatter(tkr.EngFormatter(unit='eV'))
ax.yaxis.set_minor_formatter(tkr.EngFormatter(unit='b'))

# Remove errorbars from showing in the legend
# https://stackoverflow.com/a/15551976
handles, labels = ax.get_legend_handles_labels()
handles = [h[0] for h in handles]

# Deal with script vars that can be varied
try:
    ax.set_xlim(*ELims*1e6)
    ax.set_xticks(ELims*1e6)
except NameError:
    pass
try:
    ax.set_ylim(xsLims/1e3)
    ax.set_yticks(xsLims/1e3)
except NameError:
    pass
try:
    ax.xaxis.set_minor_locator(tkr.LogLocator(subs=EtickSubs))
except NameError:
    pass
try:
    ax.yaxis.set_minor_locator(tkr.LogLocator(subs=XStickSubs))
except NameError:
    pass
try:
    ax.legend(handles, labels, loc=legendLocation)
except NameError:
    ax.legend(handles, labels)
try:
    ax.set_title(f'{graphTitle}', fontsize=20)
except NameError:
    pass

plt.savefig('xsoutput.svg')
if (showPlot):
    plt.show()