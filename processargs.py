import json
import numpy as np

def flagprocess(args: list) -> dict:
    """
    Read args passed thru script to get dataset list name
    and whether request wants plt.show()
    """
    imgType=''     # Flag for output image format
    showPlot=False # Flag to open interactive plot window
    zoomBox=False  # Flag to render zoom box region

    for arg in args[1:]:
        if ('-file' in arg.lower()):
            eqIndex=arg.index('=')
            fName=arg[eqIndex+1:]
        elif ('-show' in arg.lower()):
            showPlot=True
        elif ('-format' in arg.lower()):
            eqIndex=arg.index('=')
            imgType=arg[eqIndex+1:].lower()
        elif ('-zoombox' in arg.lower()):
            zoomBox=True
    # Check if name was specified
    try:
        type(fName)
    except NameError:
        raise NameError(f'No file name passed thru args\nargs:{args}')
    # Default to svg if image type not specified
    if (imgType==''):
        print('No file type specified, using svg format')
        imgType='svg'
    
    # Put user flags in dict
    flags={
        'showPlot':showPlot,
        'imgType' :imgType,
        'zoomBox' :zoomBox,
        'fName'   :fName
    }
    return flags


def xsprocess(args: list[str]) -> tuple[dict, dict, dict]:
    """
    Read datasets provided in arg file and obtain
    data of interest

    args -> LIST : Resulting list from sys.argv
    """
    # Get file name and bool on showing interactive plot
    flags = flagprocess(args)

    with open(flags['fName'], 'r') as f:
        fData=json.load(f)
    
    # Hold xs-specific args in a dict
    graphConfig=fData['xsGraphConfig']

    # # Get name
    # plotTitle=fData['xsgraphname']

    # Read in datasets
    graphData={}
    for dataset in fData['data']:
        path=dataset['path']
        with open(path, 'r') as f:
            rawData=f.readlines()
        
        cols2grab=[]    # Hold column names to grab
        nMeasurements=0 # For declaring 
        measurements=[] # For holding measurements temp.
        for line in rawData:
            if ('# ' in line[:2]):
                continue
            elif ('##' in line[:2]):
                if ('[' in line):
                    continue
                
                # Get column title names (e, xs, ...)
                # and compare against requests
                colNames=[]
                i=0
                while True:
                    colNames.append(line[i:i+15].strip('#').strip())
                    i+=15
                    if (line[i:i+15]==''):
                        break
                for i, col in enumerate(colNames):
                    for reqVal in dataset['values']:
                        if (col.lower()==reqVal.lower()):
                            cols2grab.append((i, col))
                            break
                

            else:
                nMeasurements+=1
                measurements.append(line.split())
        
        # Store measurements in array and assign values
        # Slight complication in inner loop b/c no gaurentee
        #    that each file has e, de, xs, dxs (some could b missing)
        arr=np.zeros((4,nMeasurements))
        for i, val in enumerate(measurements):
            for j, row in cols2grab:
                if (row.lower()=='e'):
                    arr[0,i]=float(val[j])
                elif (row.lower()=='de'):
                    arr[1,i]=float(val[j])
                elif (row.lower()=='xs'):
                    arr[2,i]=float(val[j])
                elif (row.lower()=='dxs'):
                    arr[3,i]=float(val[j])
        
        # Store name and data in dict
        graphData.update({dataset['name']:(arr, dataset['isLine'])})
        # print(f'{dataset['name']} {arr}')
    
    return flags, graphData, graphConfig


def timeprocess(args: list[str]) -> tuple[dict,dict]:
    """
    Process datasets in provided json

    Returned dict takes the form:
    key-Name of data
    value-Duration (seconds)
    """
    # Get name of file containing data and display query
    fName, flags = flagprocess(args)

    # Get datasets
    with open(fName, 'r') as f:
        fData=json.load(f)
    
    # Iterate over datasets present and add to dict
    graphData={}
    for dataset in fData:
        name=dataset['name']
        try:
            duration_seconds=dataset['duration']
        except KeyError:
            continue
        graphData.update({name:duration_seconds})
    
    return flags, graphData