import io
import math
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest

from ...angles_from_positions import angle_from_positions_v3 as afp
from ...angles_from_positions import graphs_from_angles as gfa

# many tests require vec_test.xvg file, so define its path once
data = Path(__file__).parent
vector_testfile = data / 'vec_test.xvg'


def data_lines(path):
    '''Lines of an .xvg file that hold numbers (no #, @ or blank lines).'''
    with open(path) as f:
        return [l for l in f if l.strip() and l[0] not in '#@']


def copy_vec_test(folder):
    '''Copies vec_test.xvg into folder and returns the path of the copy.
    run_scr writes its outputs next to the input file, so working on
    a copy in a temporary folder keeps tests/ clean.
    '''
    dst = Path(folder) / 'vec_test.xvg'
    shutil.copy(vector_testfile, dst)
    return dst


#### single functions ####

def test_read_mols_only_time_column_raises():
    with pytest.raises(ValueError):
        afp.read_mols(io.StringIO('0\n'), 3)


def test_angle_vectors():
    # (unit vector, its angle to the X axis in degrees)
    d = math.sqrt(0.5)  # x and y of a unit vector on a diagonal
    cases = [
        ([1, 0], 0),        # right
        ([0, 1], 90),       # up
        ([-1, 0], 180),     # left
        ([0, -1], -90),     # down
        ([d, d], 45),
        ([d, -d], -45),
        ([-d, -d], -135),
    ]
    for vec, expected in cases:
        # the text after the comma is shown if this case fails
        assert afp.angle_vectors(vec) == pytest.approx(expected), vec


def test_angle_vectors_clips_rounding_overshoot():
    # a 'unit' vector slightly longer than 1 must not give NaN
    assert afp.angle_vectors([1.0000001, 0]) == pytest.approx(0)


#### run_scr (whole pipeline) ####
# Each test makes a temporary folder; it is deleted at the end of 'with'.

def test_run_scr_angles_match_atan2():
    '''Times and angles agree with an independent calculation from the
    raw coordinates. Also catches a lost first time step (t = 0).'''
    raw = np.loadtxt(data_lines(vector_testfile))
    with tempfile.TemporaryDirectory() as tmp:
        files = afp.run_scr(str(copy_vec_test(tmp)), 3)
        for mol, name in enumerate(files):
            c = 1 + mol * 6  # first column of this molecule
            dx = raw[:, c] - raw[:, c + 3]
            dy = raw[:, c + 1] - raw[:, c + 4]
            expected = np.degrees(np.arctan2(dy, dx))
            got = np.loadtxt(name)
            assert got.shape == (len(raw), 2)
            assert np.allclose(got[:, 0], raw[:, 0])
            # output is rounded to 2 decimals, and vectors to 3 before that
            assert np.allclose(got[:, 1], expected, atol=0.1)


def test_run_scr_returns_one_file_per_mol():
    with tempfile.TemporaryDirectory() as tmp:
        files = afp.run_scr(str(copy_vec_test(tmp)), 3)
        assert len(files) == 6
        for i, name in enumerate(files, start=1):
            assert name.endswith('vec_test_angle_out_%d.xvg' % i)
            assert Path(name).exists()


def test_run_scr_writes_vec_and_norm_files():
    with tempfile.TemporaryDirectory() as tmp:
        afp.run_scr(str(copy_vec_test(tmp)), 3)
        for i in range(1, 7):
            assert (Path(tmp) / ('vec_test_vec_out_%d.xvg' % i)).exists()
            assert (Path(tmp) / ('vec_test_vec_norm_out_%d.xvg' % i)).exists()


def test_run_scr_2d_input():
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / 'flat.xvg'
        f.write_text('@ title "2D"\n'
                     '0   1 1  0 0   0 0  1 0\n'
                     '10  0 1  0 0   0 0  0 1\n')
        files = afp.run_scr(str(f), 2)
        assert len(files) == 2
        assert np.allclose(np.loadtxt(files[0]), [[0, 45], [10, 90]])
        assert np.allclose(np.loadtxt(files[1]), [[0, 180], [10, -90]])


def test_run_scr_wrong_dimensions_raises():
    # 36 values per line are not a multiple of 2 x 5
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(ValueError):
            afp.run_scr(str(copy_vec_test(tmp)), 5)


#### graphs_from_angles ####

def test_print_angles_one_png_per_angle_file():
    with tempfile.TemporaryDirectory() as tmp:
        for name in afp.run_scr(str(copy_vec_test(tmp)), 3):
            pngs = gfa.print_angles(gfa.read_file(name), name)
            assert pngs == [name[:-4] + '.png']
            assert Path(pngs[0]).stat().st_size > 0
