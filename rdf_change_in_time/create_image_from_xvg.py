import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import os


def read_file(filename):
    ''' (str) -> df
    reads the file into numpy array and converts to dataframe
    with first column as index '''

    '''
    #how many cols are there?
    with open(filename, 'r') as temp_f:
        read_1st = temp_f.readline()
    firstline = read_1st.split()

    #handling corrupted files:
    len_1st = len(firstline)
    if len_1st == 0:
        print('empty file!')
        return 0
    elif len_1st == 1:
        print('corrupted data! file contains only 1 column!')
        return 0
    '''

    #column names:
     
    '''
    name = lambda x: "rdf%02d" %(x)
    for count, e in enumerate(firstline[1:]):
        col_names.append(name(count))
    '''
    #read data:
    np_data = np.loadtxt(filename, comments = ['#','@'])
    np_data = np_data.astype(float)

    #numpy because pandas can't use multiple camments
    #change to pandas for consistency when available

    num_of_cols = np_data.shape[1]

    col_names = ['distance']
    if num_of_cols > 2:
        for i in range(1,num_of_cols):
            col_names.append('RDF_'+str(i))
    else:
        col_names.append('RDF')

    #print(np_data)
    #print(np_data.shape)
    #print(col_names)
    #print(np_data[0:,0])
    '''
    df = pd.read_csv(filename, engine = 'python',
                     sep = "\t|\s",comment = ['#','@'],
                     names = col_names,
                     index_col=0)
    '''

    df = pd.DataFrame(data = np_data,
                      columns = col_names)
    #print(df.head())
    df = df.set_index(col_names[0])
    #print(df.head())

    return df

        
def print_line_graph(df, filename, col_title = None,
                     xlabel = 'Distance', ylabel = 'RDF',
                     title = 'RDF', maxrdf = 3.0):
    '''(DataFrame, str, str, str, str, str, float)
    Takes data from read_file function.
    Creates a graph from a dataframe.
    - df - dataframe
    - filename - output
    - col_title - column to plot; None plots all RDF columns
    '''
    cols = df.columns if col_title is None else [col_title]
    for col in cols:
        plt.plot(df.index, df.loc[:, col], label = col)
    if len(cols) > 1:
        plt.legend()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.ylim(0, maxrdf)
    plt.savefig(filename, format = 'png')
    plt.close()


def list_of_xvg(pattern):
    '''(str) -> list
    The function will attempt to create a list based on
    the provided pattern. It is expected that a pattern will
    be 'ready to use'. However if it is found to end with
    .xvg the funtion will attemp to cut off the end with
    number. Assumption that the final number is separated.
    If no number is present, only .xvg will be removed.
    For example:
    - RDF_POPC_01.xvg will be cut to RDF_POPC
    - RDF_POPC.xvg will be cut to RDF_POPC
    Be aware, that it is not a goal to remove number from
    final PNG files - this function is only used to clean
    pattern and find all matching files.
    Files are sorted by the numbers in their names, so _B500 comes
    before _B1000 (time order for the movie).
    '''
    pattern = re.sub(r'_?[0-9]*(\.xvg)?$','',pattern)
    print('I\'m using pattern for XVG files: ', pattern)
    allfiles = os.listdir()
    rdf_files = list(filter(lambda fn: fn.startswith(pattern) and fn.endswith('.xvg'),
                            allfiles))
    rdf_files.sort(key = lambda fn: [int(part) if part.isdigit() else part
                                     for part in re.split(r'(\d+)', fn)])

    return rdf_files



def line_graphs(xvg, xtit = 'distance', ytit = 'RDF', maxrdf = None,
                col_title = None):
    '''(str, str, str, float, str) -> list
    Creates all line-graphs from xvg files matching the pattern. You can
    change axis titles, the y-axis limit and the column used (None = all).
    If maxrdf is None, the highest RDF value of all files is used, so
    every graph (movie frame) has the same scale.
    Returns the names of the PNG files.
    '''
    xvg_files = list_of_xvg(xvg)
    if not xvg_files:
        raise FileNotFoundError('No XVG files match the pattern: ' + xvg)

    #no need to add number, it's assumed that xvg are already
    #numbered in previous steps
    name_png = lambda name_xvg: (name_xvg[:-4] +'.png')

    all_data = [read_file(file) for file in xvg_files]
    if maxrdf is None:
        maxrdf = 1.05 * max(df.values.max() for df in all_data)

    pngs = []
    for file, data in zip(xvg_files, all_data):
        print_line_graph(data, name_png(file), col_title = col_title,
                         xlabel = xtit, ylabel = ytit,
                         title = file[:-4], maxrdf = maxrdf)
        pngs.append(name_png(file))
    return pngs


if __name__ == '__main__':
    print('Give a filename to create graphs: ')
    file = input()
    line_graphs(file)
    print('You can find crude representations of the RDF \
change in subsequent PNG files.')


    

