import os
import shutil
import subprocess
from . import create_image_from_xvg
from . import create_movie_from_png


def traj_run(XTC, TPR, index, XVG, begin, end, dt, atom, sel='SOL', gmx='gmx'):
    """(str,str,str,str,int,int,int,str,str,str) -> list
    Function runs subsequent SOLVATATION gmx rdf. The idea is
    to get RDFs OF WATER against some atoms for time evolution
    during some biochemical processess. Example of use:
    traj_run('LUT_BCL60_md_1ps_plus15_50fs.xtc','LUT_BCL60_md_1ps_plus15_50fs.tpr','index_RDF_27022.ndx', 'otuput.xvg',
            '1500', '1550', '5', '10')
    - xtc or trr trajectory: LUT_BCL60_md_1ps_plus15_50fs.xtc
    - tpr file: LUT_BCL60_md_1ps_plus15_50fs.tpr
    - ndx index file containing the indexes for atoms aroud
    which RDF is to be cunted: index_RDF_27022.ndx
    - output name: output.xvg
    - begning for the 1st RDF calculation: 1500 [ps]
    - end of the LAST RDF: 1550 [ps]
    - single RDF time. Also timestep between subsequen RDF
    calcultaions: 5 [ps]
    - group name or number in the ndx index file
    for RDF calcultaion: 10
    - sel: group the RDF is calculated for, default SOL (water)
    - gmx: GROMACS executable, e.g. gmx_mpi on some clusters
    Returns the names of the XVG files written.
    """

    begin = int(begin)
    end = int(end)
    dt = int(dt)
    B = begin
    E = B + dt

    if shutil.which(gmx) is None:
        raise FileNotFoundError("'" + gmx + "' was not found. Load GROMACS "
                                "first (e.g. source GMXRC or module load gromacs).")
    if (end - begin) % dt:
        print('Warning: end - begin is not a multiple of the RDF time, '
              'the last ' + str((end - begin) % dt) + ' ps are skipped.')

    XVG = remove_xvg(next_to_trajectory(XVG, XTC))
    outputs = []
    # old version using subprocess.Popen, which is more complex and less safe
    #     while E <= end:
    #         print(E)
    #         XVG_changed = XVG+"_B"+str(B)+"_E"+str(E)+".xvg"
        
    #         p1 = subprocess.Popen(['echo', atom, '\n', 'SOL'], stdout=subprocess.PIPE)
    #        pdb.set_trace()
    #         grdf = ' '.join(['gmx', 'rdf', '-f', XTC, '-s', TPR, '-n', index, '-b', str(B), '-e', str(E), '-o', XVG_changed])
        
    #         p2 = subprocess.Popen([grdf], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True)
    #         p1.stdout.close()
    #         output = p2.communicate()[1]
        
    while E <= end:
        print(E)
        XVG_changed = XVG+"_B"+str(B)+"_E"+str(E)+".xvg"

        # answers to gmx rdf questions: reference group, then selection
        grdf = [gmx, 'rdf', '-f', XTC, '-s', TPR, '-n', index, '-b', str(B), '-e', str(E), '-o', XVG_changed]
        result = subprocess.run(grdf, input=atom + '\n' + sel + '\n',
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError('gmx rdf failed for ' + str(B) + '-' + str(E)
                               + ' ps:\n' + result.stderr)
        outputs.append(XVG_changed)

        B = E
        E = E + dt

    return outputs


def next_to_trajectory(filename, XTC):
    """(str, str) -> str
    Puts the output file in the folder of the trajectory, unless
    the name already contains a folder.
    """
    if os.path.dirname(filename):
        return filename
    return os.path.join(os.path.dirname(XTC), filename)


def remove_xvg(filename):
    """(str)
    Cut-off the xvg extension for name change:
    - removes xvg at the end of the name
    - any other name is returned unchanged
    """
    if filename.endswith(".xvg"):
        return filename[0:-4]
    else:
        print("wrong extension! program will still try to use the file, \
but errors may show up")
        return filename


def run_rdf_change():
    print('This program calculates solvatation RDF.')
    print('   XTC or TRR trajectory: ')
    XTC = input()

    print('   TPR file: ')
    TPR = input()

    print('   NDX file: ')
    index = input()
    
    print('   output XVG names. Give name for one file with xvg \
extension. Don\'t add numbering: ')
    XVG = input() 

    print('   Begin RDF time: ')
    begin = input()

    print('   End RDF time: ')
    end = input()

    print('   Single RDF time: ')
    dt = input()

    print('   Group to calculate solvatation RDF for: ')
    atom = input() 

    # all output files go to the folder of the trajectory
    XVG = next_to_trajectory(XVG.strip(), XTC.strip())
    traj_run(XTC.strip(), TPR.strip(), index.strip(), XVG, begin, end, dt, atom)

    print('Do you want to create movie covering the RDF change - Y/N? ')
    movie = input().strip().upper()
    if movie == 'Y':
        # pattern base_B matches only the files made by traj_run
        pattern = remove_xvg(XVG) + '_B'
        create_image_from_xvg.line_graphs(pattern)
        vid_name = create_movie_from_png.create_video(pattern, remove_xvg(XVG) + '_film')
        print('Video saved as: ' + vid_name)

    else:
        print('cyu around Spark!')

if __name__ == '__main__':
    run_rdf_change()
