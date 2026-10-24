import os
import shutil
from pathlib import Path

import numpy as np
import pytest
from ...rdf_change_in_time import g_rdf_change_during_simulation
from ...rdf_change_in_time import create_image_from_xvg as cig

# RDF files made earlier by gmx rdf, kept in tests/ as input data
data = Path(__file__).parent
rdf_files = sorted(data.glob('RDF_BCL30_B*.xvg'))
# expected time order of the windows
time_order = ['RDF_BCL30_B0_E20.xvg', 'RDF_BCL30_B20_E40.xvg',
              'RDF_BCL30_B40_E60.xvg', 'RDF_BCL30_B60_E80.xvg',
              'RDF_BCL30_B80_E100.xvg']


def copy_rdf_files(folder):
    '''Copies the RDF xvg files into folder and returns the pattern
    that matches them. line_graphs writes PNGs next to the xvg files,
    so working on copies keeps tests/ clean.
    '''
    for f in rdf_files:
        shutil.copy(f, folder)
    return str(Path(folder) / 'RDF_BCL30_B')


def test_positive_remove_xvg():
    assert g_rdf_change_during_simulation.remove_xvg('alama.xvg') == 'alama', 'positive pass'


def test_negative_remove_xvg():
    assert g_rdf_change_during_simulation.remove_xvg('alama.txt') == 'alama.txt'


def test_noextension_remove_xvg():
    assert g_rdf_change_during_simulation.remove_xvg('alama') == 'alama'


def test_onlyextension_remove_xvg():
    assert g_rdf_change_during_simulation.remove_xvg('.xvg') == ''


#### create_image_from_xvg ####

def test_read_file_real_rdf():
    '''Verify that read_file correctly reads a real gmx rdf output: 
    - and @ lines skipped
    - one RDF column indexed by distance
    - values unchanged.
    '''
    path = data / 'RDF_BCL30_B0_E20.xvg'
    raw = np.loadtxt(path, comments=['#', '@'])
    df = cig.read_file(path)
    assert list(df.columns) == ['RDF']
    assert df.index.name == 'distance'
    assert np.allclose(df.index, raw[:, 0])
    assert np.allclose(df['RDF'], raw[:, 1])


def test_list_of_xvg_numbers_sorted_as_numbers(tmp_path):
    # alphabetically _B1000 comes before _B500, but in time it is later
    for name in ['RDF_B1000_E1500.xvg', 'RDF_B500_E1000.xvg', 'RDF_B0_E500.xvg']:
        (tmp_path / name).write_text('0 0\n')
    files = cig.list_of_xvg(str(tmp_path / 'RDF_B'))
    assert [Path(f).name for f in files] == ['RDF_B0_E500.xvg',
                                             'RDF_B500_E1000.xvg',
                                             'RDF_B1000_E1500.xvg']


def test_line_graphs_writes_pngs(tmp_path):
    """ The test checks that the line_graphs function creates PNG files from 
    the copied RDF xvg files, and that the generated PNG files have a non-zero size. 
    That's basically the test to ensure that the function is working correctly 
    and producing output files as expected.
    """
    pattern = copy_rdf_files(tmp_path)
    pngs = cig.line_graphs(pattern)
    assert [Path(p).name for p in pngs] == [n[:-4] + '.png' for n in time_order]
    for p in pngs:
        assert os.path.getsize(p) > 0


def test_line_graphs_no_match_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        cig.line_graphs(str(tmp_path / 'nothing_here'))
