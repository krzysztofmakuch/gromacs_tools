'''
Converts atom positions from a GROMACS .xvg file into the angle between
each molecule's vector (atom 1 - atom 2) and the X axis, using x and y only.

Run as a script and answer the prompts:

    python angle_from_positions_v3.py

or from an interactive session (python -i angle_from_positions_v3.py):

>>> run_scr('file_name.xvg', number_of_dimensions)

Columns: time, then for each molecule x y z of atom 1 followed by
x y z of atom 2. The number of molecules is found from the number
of columns. For example vec_test.xvg in tests: 3 dimensions,
6 molecules, 37 columns (1 + 6x2x3):
run_scr('vec_test.xvg', 3)

For each molecule N it writes <name>_vec_out_N.xvg,
<name>_vec_norm_out_N.xvg and <name>_angle_out_N.xvg.

'''

import numpy as np


def run_scr(file, dim):
    '''(str, int) -> list
    Calculates vectors, normalized vectors and angles for each molecule
    in file and writes them to separate files. Returns angle file names.
    '''
    with open(file, 'r') as f:
        no_o_mol = read_mols(f, dim)
        # read_mols used up the first data line - go back to the start
        # so the first time step is not lost
        f.seek(0)

        vectors = coords_to_vectors(f, dim, no_o_mol)
        normalized_vec = normalize_mol_lib(vectors)

        angles = angle_mol_library(normalized_vec)



    print_vecs_to_files(vectors, file, '_vec_out_')
    print_vecs_to_files(normalized_vec, file, '_vec_norm_out_')
    return print_angles_to_files(angles, file, '_angle_out_')


def read_mols(file, dimensions):
    ''' (file, int) -> int
    returns the number of molecules based on the 1st line with data'''
    for line in file:
        if line.strip() and line[0] not in ['#', '@']:
            n_values = len(line.split()) - 1
            if n_values == 0 or n_values % (2*dimensions):
                raise ValueError(
                    '%d columns after time is not a multiple of 2 atoms x %d '
                    'dimensions. Check the number of dimensions.'
                    % (n_values, dimensions))
            return n_values // (2*dimensions)

def print_vecs_to_files(dict_of_vec, input_name, suffix):
    ''' (dict, str, str)
    prints all vectors from dict to output, each molecule sperate.
    Assumptions:
    - key 0 in libarary are times and are omitted.
    - all vectors start in XY = [0,0], so only their ends are given
    >>> print_vecs_to_files({ ...}, vec_test.xvg, '_norm_')
    vec_test_norm_1.xvg
    vec_test_norm_2.xvg
    ...
    '''
    for key in dict_of_vec:
        if key != 0:
            newname = input_name[:-4] + suffix + str(key) + '.xvg'
            print_lines(dict_of_vec[key], newname)

def print_lines(list_of_vecs, file):
    '''(list, str)
    prints all subsequent sublists to new line each in file
    '''
    with open(file, 'w') as f:
        for vec in list_of_vecs:
            print('%5.3f\t%5.3f' %(vec[0], vec[1]), file = f)


def print_angles_to_files(dict_of_angles, input_name, suffix):
    '''(dict, str, suffix) -> list
    does same as print vecs to files, but for angles.
    Returns the names of the files written.
    '''
    files = []
    for key in dict_of_angles:
        if key != 0:
            newname = input_name[:-4] + suffix + str(key) + '.xvg'
            print_angle_line(dict_of_angles[0], dict_of_angles[key],\
                             newname)
            files.append(newname)
    return files

def print_angle_line(list_of_times, list_of_angles, file):
    '''(list, list, str)
    print angles for seperate molecules
    '''
    with open(file, 'w') as f:
        for t, ang in zip(list_of_times, list_of_angles):
            print('%5.2f\t%5.2f' %(t,ang), file = f)


#### COORDS TO VECTORS ####


def coords_to_vectors(infile, dimensions, no_of_mols):
    '''(str,int,int)
    read input file line by line and change coordinates to vectors
    '''
    database_of_mols = {x:[] for x in range(0,no_of_mols+1)}

    
    for line in infile:
        if line.strip() and line[0] not in ['#', '@']:
            #move vectors to seperate molecules:
            newline = compose_newline(line, dimensions)
            update_database(database_of_mols, newline)

    return database_of_mols

def update_database(database, newline):
    '''(dict,list)
    adds items from a line to list of vectors for each dictionary
    '''
    for i in range(0,len(newline)):
        database[i].append(newline[i]) 


def compose_newline(line, dimensions):
    '''(str) -> str
    given a line with data makes newline with time and vecotrs
    '''
    oldline = list(map(float, line.split()))
    newline = [oldline[0]]
    coord = 1
    while coord < len(oldline):
        xyz1 = oldline[coord : coord+dimensions]
        coord += dimensions
        xyz2 = oldline[coord : coord+dimensions]
        coord += dimensions
        vec = calculate_vector(xyz1, xyz2)
        newline.append(vec)

    return newline


def calculate_vector(xyz1, xyz2):
    '''(list, list) -> list
    returns a vector from two sets of coordinates
    '''
    return [round(coord1-coord2 , 3) for coord1, coord2 in zip(xyz1, xyz2)]


#### VECTORS OPERATIONS #####

def normalize_mol_lib(mol_vectors_library):
    '''(dict) -> dict
    Takes a dictionary with all molecules and returns dict
    of mols normalized to x and y - 1st and 2nd coordinate of each
    vector
    '''
    normalized_lib = {}
    for key in mol_vectors_library:
        if isinstance(mol_vectors_library[key][0], list):
            normalized_lib[key] = normalize_1molecule(mol_vectors_library[key])
        else:
            normalized_lib[key] = mol_vectors_library[key]

    return normalized_lib


def normalize_1molecule(list_of_vec):
    '''(list) -> list
    Takes list of lists (1st list is time, next lists are vecotrs) 
    and returns a list of normalized vectors. Works under the
    assumption that vectors should be normlaized to xy plane
    ortogonal to z axis - first two coorinates.
    '''
    normalized = []
    for ele in list_of_vec:
        normalized.append(normalize_vector(ele[0:2]))

    return normalized


def normalize_vector(vec):
    '''(list) -> list
    '''
    vec_norm = np.linalg.norm(vec)
    return (vec/vec_norm).tolist()



##### AGNLES ####

def angle_mol_library(norm_mol_lib):
    '''(dict) -> dict
    takes a dict of list of vectors for each molecule,
                            where key 0 is a time and
    return dict of lists of angles, where key 0 is a time
    '''
    angle_lib = {}
    
    for key in norm_mol_lib:
        if isinstance(norm_mol_lib[key][0], list):
            angle_lib[key] = angle_evolution(norm_mol_lib[key])
        else:
            angle_lib[key] = norm_mol_lib[key]
    return angle_lib
    

def angle_evolution(list_of_vec):
    '''(list)->list
    takes lists of lists (vectors) -> returns list of floats (angles)
    '''
    return [angle_vectors(v) for v in list_of_vec]

def angle_vectors(v1):
    '''(list) -> list
    calculates angle between 2 vecotrs given by xy list and unit v
    '''
    #reference unit vector in x axis:
    ref_vec = [1,0]
    
    if v1[1] >=0:
        return np.degrees( np.arccos( np.clip( np.dot(v1, ref_vec),\
                                               -1.0, 1.0 )) )
    else:
        return -(np.degrees( np.arccos( np.clip( np.dot(v1, ref_vec),\
                                                 -1.0, 1.0 )) ))
    
#### if main ####

def run_module():
    """ Execute module asking for parameters """
    print('This program converts positions of atoms into angles \
between a vector and 0X axis.\
\n Provide the program with a filename and number of dimensions \
in your xvg file.')
    print('   filename: ')
    file = input().strip().strip('"')
    print('   dimensions: ')
    dim = int(input())
    angle_files = run_scr(file, dim)
    print('Angles written to %s ... %s' % (angle_files[0], angle_files[-1]))
    return angle_files

if __name__ == '__main__':
    run_module()