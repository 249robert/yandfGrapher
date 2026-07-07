#!/home/robert/249robert-github/yandf-grapher/.venv/bin/python3
import numpy as np
import matplotlib.pyplot as plt  # To plot
import matplotlib.ticker as tkr  # To manage axis tickmark styling
from matplotlib.lines import Line2D #
import processargs
import sys
import os
import random  # For random selection of marker types

# Make sure theres something defined for these lists
# markerList=['.','v','^','H','p']
markerList=list(Line2D.filled_markers)
lineStyleList=['-','--','-.',':']
colorList=[
    '#000fff',"#ff0000","#208000",
    "#9000ff","#000000","#ffaa00",
    "#fe6bb9","#009E99FF","#980081",
    "#00d36d","#626262","#9c9c00"
]

markerList.remove('o') # remove the fat dot
markerList.remove('8') # octagon looks too similar to fat dot

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

def firstItemNoReplacement(set: list) -> str:
    """
    Sample the zeroth indexed string in a list and
    remove it
    """
    val=set[0]
    set.remove(val)
    return val

# Call processing script to read in data and make sense of flags
# showPlot, dataSets, graphTitle = processargs.xsprocess(sys.argv)
flags, dataSets, config = processargs.xsprocess(sys.argv)

# Initialize graph in widescreen if svg or not specified dims
try:
    if (flags['imgType']=='png'):
        fig, ax = plt.subplots(figsize=config['pngDimensions'])
    else:
        fig, ax = plt.subplots(figsize=config['svgDimensions'])
except KeyError:
    print(f"No 'svgDimensions' specified in xsconfig of json")
    fix, ax = plt.subplots(figsize=config['svgDimensions'])

if (flags['zoomBox']==True):
    try:
        zoomDispLoc=np.array([
            [config['zoomBox']['xMin'], config['zoomBox']['width'] ],
            [config['zoomBox']['yMin'], config['zoomBox']['height']]
        ])
        zoomBounds=np.array([
            config['zoomBox']['domain'],
            config['zoomBox']['range']
        ])
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
        axins.yaxis.set_minor_formatter(tkr.EngFormatter(unit='b', places=2))
        axins.xaxis.set_minor_locator(tkr.LogLocator())
        axins.yaxis.set_minor_locator(tkr.LinearLocator(numticks=4))
        axins.xaxis.set_ticks(zoomBounds[0]*1e6)
        axins.yaxis.set_ticks(zoomBounds[1]/1e3)
    except KeyError:
        print(f"Could not process settings in 'zoomBox'")
        pass



lineWidth=1.25 # decrement this for every additional line graphed
for name, Set in dataSets.items():
    data, isLine = Set
    E, dE, xs, dxs = data
    
    # Sample random styling (marker, line)
    if (isLine):
        markerStyle=''
        markerSize=None 
        lineStyle=firstItemNoReplacement(lineStyleList)
        capSize=0
    else:
        markerStyle=firstItemNoReplacement(markerList)
        markerSize=None
        lineStyle=''
        capSize=1.75
    color=firstItemNoReplacement(colorList)
    
    # For zoombox if specified
    if (flags['zoomBox']):
        axins.errorbar(
        x=E*1e6, y=xs/1e3, xerr=dE*1e6, yerr=dxs/1e3,
        label=name, ls=lineStyle, linewidth=lineWidth,
        marker=markerStyle, markersize=markerSize,
        c=color, capsize=capSize
        )

    # For main plot
    ax.errorbar(
        x=E*1e6, y=xs/1e3, xerr=dE*1e6, yerr=dxs/1e3,
        label=name, ls=lineStyle, linewidth=lineWidth,
        marker=markerStyle, markersize=markerSize,
        c=color, capsize=capSize
    )
    # Decrement line width for visibility (counter line overlap)
    if (isLine):
        lineWidth-=0.2

# Load xsConfig params
ELims=np.array(config['domain'])
xsLims=np.array(config['range'])
# EtickSubs=np.array(config['minorETicks'])
# XStickSubs=np.array(config['minorXSTicks'])
legendLocation=config['legendLoc']
graphTitle=config['title']


# Set some fixed settings for all graph scenarios
ax.set_xscale('log')
ax.set_xlabel('Energy', fontsize=14)
ax.set_ylabel('Cross section',fontsize=14)
ax.xaxis.grid(which='major')
ax.xaxis.grid(which='minor', linewidth=0.4, linestyle="-.")
ax.yaxis.grid(which='major')
ax.yaxis.grid(which='minor', linewidth=0.4, linestyle='-.')
ax.xaxis.set_major_formatter(tkr.EngFormatter(unit='eV'))


# Set y grid and tickmarks based on requested scale
# else block adds custom gridlines and tickmarks for xs
# try except blocks are for different ylims depending on
# linscale vs logscale
if (flags['linscale']==True):
    try:
        ax.set_ylim(0, xsLims[1]/1e3)
    except KeyError:
        pass
else:
    ax.set_yscale('log')
    xsLowExp, xsUppExp = [int(np.log10(a)) for a in xsLims]
    xsoOMs=range(xsLowExp, xsUppExp+1)
    minorXSticks=[]
    for i in xsoOMs:
        for j in range(2,10):
            minorXSticks.append(j*10**(i-3))
    ax.yaxis.set_minor_locator(tkr.FixedLocator(minorXSticks))
    ax.yaxis.set_minor_formatter(tkr.NullFormatter())
    majorYoOMs=np.logspace(xsLowExp-3,xsUppExp-3, len(xsoOMs),endpoint=True)
    majorYticks=[]
    for tick in majorYoOMs:
        majorYticks.append(tick)
        majorYticks.append(5*tick)
    majorYticks=majorYticks+list(xsLims/1e3)
    majorYticks=list(set(majorYticks))
    ax.yaxis.set_major_locator(tkr.FixedLocator(majorYticks))
    try:
        ax.set_ylim(*xsLims/1e3)
    except KeyError:
        pass
ax.yaxis.set_major_formatter(tkr.EngFormatter(unit='b'))

# Add custom gridlines and tickmarks for energies
ELowExp, EUppExp = [int(np.log10(a)) for a in ELims]
EoOMs=range(ELowExp, EUppExp+1)
minorEticks=[]
for i in EoOMs:
    for j in range(2,10):
        minorEticks.append(j*10**(i+6))
ax.xaxis.set_minor_locator(tkr.FixedLocator(locs=minorEticks))
ax.xaxis.set_minor_formatter(tkr.NullFormatter())
majorXoOMs=np.logspace(ELowExp+6,EUppExp+6, len(EoOMs), endpoint=True)
majorXticks=[]
for tick in majorXoOMs:
    majorXticks.append(tick)
    majorXticks.append(5*tick)
majorXticks=majorXticks+list(ELims*1e6)
majorXticks=list(set(majorXticks))
ax.xaxis.set_major_locator(tkr.FixedLocator(majorXticks))

# Remove errorbars from showing in the legend
# https://stackoverflow.com/a/15551976
handles, labels = ax.get_legend_handles_labels()
handles = [h[0] for h in handles]

# Deal with script vars that can be varied
try:
    ax.set_xlim(*ELims*1e6)
except KeyError:
    pass
try:
    ax.legend(handles, labels, loc=legendLocation)
except KeyError:
    ax.legend(handles, labels)
try:
    ax.set_title(f'{graphTitle}', fontsize=20)
except KeyError:
    pass

# For custom commands to take place
try:
    for command in config['customCommands']:
        exec(command)
except KeyError:
    pass

# Save to folder containing config file
if (flags['linscale']==True):
    graphName=os.path.join(
        os.path.dirname(flags['fName']),f'xsoutput-linscale.{flags['imgType']}'
    )
else:
    graphName=os.path.join(
        os.path.dirname(flags['fName']),f'xsoutput.{flags['imgType']}'
    )
plt.savefig(graphName)

if (flags['showPlot']):
    plt.show()