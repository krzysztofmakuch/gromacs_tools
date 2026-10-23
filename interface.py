#import previously done files

from .rdf_change_in_time import g_rdf_change_during_simulation
from .angles_from_positions import run_angles_from_positions

HELP = '''
 1. RDF change in time - runs gmx rdf in consecutive time windows
    (e.g. 1500-1505, 1505-1510 ps ...) and can make a movie of the RDFs.
    Needs: trajectory, tpr, index file, and gmx available in the terminal.
 3. angle vs axis - reads an xvg with positions of atom pairs
    (e.g. from gmx traj -ox) and calculates, for each molecule, the angle
    between the pair vector and the X axis in the XY plane (-180 to 180 deg).
    Writes one file and one graph per molecule.
'''


def interf():
    '''
    Shows the menu and runs the chosen tool. Asks again
    until a valid choice is given.
    '''

    actions = {
               1: g_rdf_change_during_simulation.run_rdf_change,
               3: run_angles_from_positions.run_module,
               }

    while True:
        print('What do you want to do?:\
              \n 0. HELP \
              \n 1. RDF change in time \
              \n 2. MSD & diffusion - work in progress\
              \n 3. angle vs axis \
              \n 4. xyz to volume  - work in progress\
              \n 5. average number of H-bonds  - work in progress\
              \n 6. H-bond lifetime - work in progress\
              \n q. quit')
        choice = input().strip().lower()

        if choice == 'q':
            return
        if choice == '0':
            print(HELP)
            continue
        if choice.isdigit() and int(choice) in actions:
            actions[int(choice)]()
            return
        print('Choose one of: 0, 1, 3 or q (2, 4, 5, 6 are not ready yet).\n')


if __name__ == '__main__':
    interf()
