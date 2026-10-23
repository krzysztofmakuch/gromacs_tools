from . import angle_from_positions_v3
from . import graphs_from_angles

def run_module():
    """ As name says - runs all module parts in order """

    angle_files = angle_from_positions_v3.run_module()

    # plot every molecule's angle file, no need to ask for names again
    for file in angle_files:
        graphs_from_angles.print_angles(graphs_from_angles.read_file(file),
                                        file)
    print('Graphs saved as PNG files next to the angle files.')


if __name__ == '__main__':
    run_module()
