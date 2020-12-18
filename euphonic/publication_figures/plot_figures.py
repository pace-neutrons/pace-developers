# Developed against Euphonic euphonic-0.3.2+67.g193a49c
import matplotlib as mpl
mpl.rcParams['font.family'] = 'serif'


import os
from unittest.mock import patch
from euphonic.cli.dispersion import main as dispersion_main
from euphonic.cli.intensity_map import main as intensity_map_main
from euphonic.cli.dos import main as dos_main
from euphonic import ureg


def save_fig(fname, x_size=10, y_size=6):
    fig = mpl.pyplot.gcf()
    fig.set_size_inches(x_size, y_size)

    out_dir = os.path.join('figures', 'examples')
    mpl.pyplot.savefig(os.path.join(out_dir, fname), dpi=100)


def plot_quartz_disp():
    dispersion_main(['quartz.castep_bin',
                     '--asr', 'reciprocal',
                     '--e-min', '0',
                     '--q-distance', '0.01',
                     '--reorder',
                     '--y-label', 'Energy (meV)'])
    save_fig('quartz_disp.pdf')


def plot_quartz_dos_band():
    intensity_map_main(['quartz.castep_bin',
                        '--asr', 'reciprocal',
                        '--e-min', '0',
                        '--q-distance', '0.0025',
                        '-w' 'dos',
                        '--eb', str(2*ureg('meV').to('THz').magnitude),
                        '--qb', '0.02',
                        '--ebins', '1000',
                        '-u', 'THz',
                        '--y-label', 'Energy (THz)'])
    save_fig('quartz_dos_band.pdf')


def plot_quartz_neutron_band():
    intensity_map_main(['quartz.castep_bin',
                        '--asr', 'reciprocal',
                        '--e-min', '0',
                        '--q-distance', '0.0025',
                        '-w' 'coherent',
                        '--eb', str(2*ureg('meV').to('1/cm').magnitude),
                        '--qb', '0.02',
                        '--ebins', '1000',
                        '-u', '1/cm',
                        '--y-label', 'Energy (cm$^{-1}$)'])
    save_fig('quartz_neutron_band.pdf')


def plot_lzo_dos():
    dos_main(['La2Zr2O7.castep_bin',
              '--e-min', '0',
              '--eb', '1',
              '--ebins', '1000',
              '--grid', '8', '8', '8',
              '--x-label', 'Energy (meV)'])
    save_fig('lzo_dos.pdf', x_size=8, y_size=6)


with patch('matplotlib.pyplot.show'):
    plot_quartz_disp()
    plot_quartz_dos_band()
    plot_quartz_neutron_band()
    plot_lzo_dos()
