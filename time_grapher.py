
import matplotlib.pyplot as plt
import processargs
import sys

#
# ============= Graph values to tweak =============
#
# Comment out a variable to assume automatic value assignment

graphTitle='Some run times'
figDimensions=(12,8)

# =================================================

showPlot, dataSets = processargs.timeprocess(sys.argv)

try:
    fix, ax = plt.subplots(figsize=figDimensions)
except NameError:
    fix, ax = plt.subplots()

for setName, duration in dataSets.items():

    a=ax.barh(setName, duration/60)
    ax.bar_label(a, fmt='%.2f', label_type='center', fontsize=14)

ax.set_xlabel('Duration (minutes)', fontsize=14)
try:
    ax.set_title(graphTitle, fontsize=20)
except NameError:
    pass

plt.savefig('timeoutput.svg')
if (showPlot):
    plt.show()