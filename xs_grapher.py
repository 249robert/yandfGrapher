
import numpy as np
import matplotlib.lines  as lns  # To get list of filled markers
import matplotlib.pyplot as plt  # To plot
import matplotlib.ticker as tkr  # To manage axis tickmark styling
import processargs
import sys
import random  # For random selection of marker types

# Make sure theres something defined for these lists
markerList=['.','v','^','H','p']
lineStyleList=['-','--','-.',':']
colorList=[
    '#000fff',"#ff0000","#165700",
    "#9000ff","#000000","#ffaa00", "#fe6bb9"
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
# showPlot, dataSets, graphTitle = processargs.xsprocess(sys.argv)
flags, dataSets, config = processargs.xsprocess(sys.argv)

# Initialize graph
try:
    fig, ax = plt.subplots(figsize=config['figDimensions'])
except KeyError:
    print(f"No 'figDimensions' specified in xsconfig of json")
    fix, ax = plt.subplots()

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
for name, set in dataSets.items():
    data, isLine = set
    E, dE, xs, dxs = data
    
    # Sample random styling (marker, line)
    if (isLine):
        markerStyle=''
        markerSize=None 
        # lineStyle=sampleNoReplacement(lineStyleList)
        lineStyle=lineStyleList[0]
        lineStyleList.remove(lineStyle)
    else:
        markerStyle=sampleNoReplacement(markerList)
        markerSize=None
        lineStyle=''

    # color=sampleNoReplacement(colorList)
    color=colorList[0]
    colorList.remove(color)
    
    # For zoombox if specified
    if (flags['zoomBox']):
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
    # Decrement line width for visibility (counter line overlap)
    if (isLine):
        lineWidth-=0.2


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
ELims=np.array(config['domain'])
xsLims=np.array(config['range'])
EtickSubs=np.array(config['minorETicks'])
XStickSubs=np.array(config['minorXSTicks'])
legendLocation=config['legendLoc']
graphTitle=config['title']
try:
    ax.set_xlim(*ELims*1e6)
    ax.set_xticks(ELims*1e6)
except KeyError:
    pass
try:
    ax.set_ylim(xsLims/1e3)
    ax.set_yticks(xsLims/1e3)
except KeyError:
    pass
try:
    ax.xaxis.set_minor_locator(tkr.LogLocator(subs=EtickSubs))
except KeyError:
    pass
try:
    ax.yaxis.set_minor_locator(tkr.LogLocator(subs=XStickSubs))
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

plt.savefig(f'xsoutput.{flags['imgType']}')
if (flags['showPlot']):
    plt.show()