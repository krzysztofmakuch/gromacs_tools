import matplotlib.pyplot as plt
import pandas as pd

def read_file(filename):
    ''' (str) -> df
    reads the file into pandas dataframe
    with first column as index '''

    #how many cols are there?
    with open(filename, 'r') as temp_f:
        read_1st = temp_f.readline()
    firstline = read_1st.split()

    #handling corrupted files:
    len_1st = len(firstline)
    if len_1st == 0:
        raise ValueError(filename + ': empty file!')
    elif len_1st == 1:
        raise ValueError(filename + ': corrupted data! file contains only 1 column!')

    #column names:
    col_names = ['time']  
    name = lambda x: "mol%02d" %(x)
    for count, e in enumerate(firstline[1:]):
        col_names.append(name(count))
    #read data:
    df = pd.read_csv(filename, engine = 'python',
                     sep = r"\s+",names = col_names,
                     index_col=0)

    #return number of columns and thedataframe
    return [len_1st, df]
        
def print_angles(data, filename):
    '''(list, str) -> list
    Takes a list from read_file function and the name of the read file.
    Creates a graph for each column of the dataframe, named after
    the input file, e.g. vec_test_angle_out_1.png.
    Returns the names of the PNG files.
    '''
    col_num = data[0]
    df = data[1]
    col_nam = df.columns
    base = filename[:-4]

    pngs = []
    for col in col_nam:
        png = base + '.png' if col_num == 2 else base + '_' + col + '.png'
        plt.scatter(df.index, df[col])
        plt.title(base)
        plt.xlabel('time')
        plt.ylabel('angle [deg]')
        plt.ylim([-180, 180])
        plt.savefig(png, format = 'png')
        plt.close()
        pngs.append(png)
    return pngs


#print_angles(read_file('angles_example.txt'))

def run_module():
    print('Give a filename to create graphs: ')
    file = input().strip().strip('"')
    pngs = print_angles(read_file(file), file)
    print('You can find crude representations of the angle \
evolution in: ' + ', '.join(pngs))

if __name__ == '__main__':
    run_module()
    
