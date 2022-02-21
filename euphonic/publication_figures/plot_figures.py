# Developed against Euphonic euphonic-0.3.2+67.g193a49c
#import matplotlib as mpl
#mpl.rcParams['font.family'] = 'serif'


import os
from typing import Sequence
from unittest.mock import patch

from euphonic.cli.dispersion import main as dispersion_main
from euphonic.cli.intensity_map import main as intensity_map_main
from euphonic.cli.dos import main as dos_main
from euphonic import ureg


def plot_quartz_disp(extra_args: Sequence = []):
    dispersion_main(['quartz.castep_bin',
                     '--asr', 'reciprocal',
                     '--e-min', '0',
                     '--q-spacing', '0.01',
                     '--reorder',
                     '--y-label', 'Energy (meV)'] + extra_args)


def plot_quartz_dos_band(extra_args: Sequence = []):
    intensity_map_main(['quartz.castep_bin',
                        '--asr', 'reciprocal',
                        '--e-min', '0',
                        '--q-spacing', '0.0025',
                        '-w' 'dos',
                        '--eb', str(2*ureg('meV').to('THz').magnitude),
                        '--qb', '0.02',
                        '--ebins', '1000',
                        '-u', 'THz',
                        '--y-label', 'Energy (THz)'] + extra_args)


def plot_quartz_neutron_band(extra_args: Sequence = []):
    intensity_map_main(['quartz.castep_bin',
                        '--asr', 'reciprocal',
                        '--e-min', '0',
                        '--q-spacing', '0.0025',
                        '-w' 'coherent',
                        '--eb', str(2*ureg('meV').to('1/cm').magnitude),
                        '--qb', '0.02',
                        '--ebins', '1000',
                        '-u', '1/cm',
                        '--y-label', 'Energy (cm$^{-1}$)'] + extra_args)


def plot_lzo_pdos(extra_args: Sequence = []):
    dos_main(['La2Zr2O7.castep_bin',
              '--e-min', '0',
              '--eb', '1',
              '--ebins', '1000',
              '--grid', '8', '8', '8',
              '--x-label', 'Energy (meV)',
              '--adaptive',
              '-w', 'coherent-dos',
              '--pdos'] + extra_args)


dirname = 'figures'
fmt = 'png'
styling = ['--style', 'pub.mplstyle']
plot_quartz_disp(['-s', f'{dirname}\quartz_disp.{fmt}'] + styling)
plot_quartz_dos_band(['-s', f'{dirname}\quartz_dos_band.{fmt}'] + styling)
plot_quartz_neutron_band(['-s', f'{dirname}\quartz_neutron_band.{fmt}'] + styling)
plot_lzo_pdos(['-s', f'{dirname}\lzo_pdos.{fmt}'] + styling
              + ['--fig-size', '8.85', '6.5', '--fig-size-unit', 'cm'])
# Size below for creating 1/2 column width figures
#              + ['--fig-size', '4.3', '3.1', '--fig-size-unit', 'cm'])
