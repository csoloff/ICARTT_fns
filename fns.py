# Basic Python functions for reading and processing ICARTT data

# packages required for all functions
import pandas as pd
from datetime import datetime as dt
import numpy as np

# additional package required for read_instr
import glob

def ict_read(path):
    '''
    Reads .ict files to a Pandas DataFrame
    :param path: path to the .ict data
    :return: Pandas DataFrame with .ict data
    '''
    with open(path) as f:
        # find the value in the file which tells you how many lines to skip to get to the table
        first_line = f.readline()
        header_line = int(first_line[0:-2].split(",")[0])-1
    data = pd.read_csv(path, sep=',', skiprows=header_line)

    # finds the location in the path containing the date
    # note this function requires the date of data acquisition to be in the file name in the format 20YYMMDD
    acc = 0
    boo = False
    for letter in path:
        if letter == '2':
            boo = True
        elif boo and letter == '0':
            acc -= 1
            break
        acc += 1
        
    # creates datetime object with the date the data was collected
    day = dt(int(path[acc:acc+4]), int(path[acc+4:acc+6]), int(path[acc+6:acc+8])) 
    
    for column in data.keys():
        if 'Time' in column:
            # converts seconds after midnight columns to datetime
            data[column] = day + pd.to_timedelta(data[column], unit='seconds')
    data.columns = data.columns.str.replace(' ', '')
    return data.replace(-9999, np.nan) # Converts -9999 values to NaN


def instr_read(instr, subset = None, dir='./inputs/ict/'):
    '''
    Reads group of .ict files with shared instrument code in pathname into a single Pandas DataFrame
    :param instr: instrument code shared across .ict file names
    :param subset: list of columns to exclude if there are any nan values
    :param dir: directory containing the ict data
    :return: Pandas DataFrame with .ict data
    '''
    paths = sorted(glob.glob(dir+'*'+instr+'*'))
    d_list = []
    for i in range(0, len(paths)):
        d_list.append(ict_read(paths[i]))
    d = pd.concat(d_list).reset_index(drop=True)
    if subset:
        d = d.dropna(subset = subset, how='all').reset_index(drop=True)
    return d