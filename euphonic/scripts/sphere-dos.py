#! /usr/bin/env python3
# euphonic 0.3.0+18.g0df2217

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np

from euphonic import ureg
from euphonic.force_constants import ForceConstants
from euphonic.plot import plot_1d
from euphonic.powder import sample_sphere_dos, sample_sphere_structure_factor


def get_parser() -> argparse.ArgumentParser:
    sampling_choices = {'golden', 'sphere-from-square-grid',
                        'spherical-polar-grid', 'spherical-polar-improved',
                        'random-sphere'}
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str,
                        help='Path to Phonopy YAML file')
    parser.add_argument('--npts', '-n', nargs='+', type=int, default=[1000])
    parser.add_argument('--sampling', type=str, default='golden',
                        choices=sampling_choices)
    parser.add_argument('--jitter', action='store_true', default=False)
    parser.add_argument('-q', type=float, default=0.1,
                        help="mod(q) radius of sampled sphere")
    parser.add_argument('--bin-width', '-b', type=float, default=0.1,
                        help="width of DOS bins in meV")
    parser.add_argument('--smear-width', '-s', type=float, default=1.,
                        help="width of DOS smearing in meV")
    parser.add_argument('--neutron', action='store_true',
                        help='Calculate structure factor instead of DOS')
    parser.add_argument('--temperature', type=float, default=273.,
                        help='Temperature (K) used for structure factors')
    return parser


def main():
    args = get_parser().parse_args()
    filename = args.file

    temperature = args.temperature * ureg['K']

    summary_name = os.path.basename(filename)
    path = os.path.dirname(filename)

    force_constants = ForceConstants.from_phonopy(
        path=path, summary_name=summary_name)

    dos_collection = {}

    for npts in args.npts:
        if args.neutron:
            dos = sample_sphere_structure_factor(force_constants, args.q,
                                                 sampling=args.sampling,
                                                 temperature=temperature,
                                                 npts=npts, jitter=args.jitter)
        else:
            dos = sample_sphere_dos(force_constants, args.q,
                                    sampling=args.sampling,
                                    npts=npts, jitter=args.jitter)
        broad_dos = dos.broaden(1 * ureg('meV'), shape='lorentz')

        dos_collection.update({npts: broad_dos})

    label_list, dos_list = map(list, zip(*dos_collection.items()))
    fig = plot_1d(dos_list, y_min=0, labels=label_list, title=summary_name)

    plt.show()


if __name__ == '__main__':
    main()


def main():
    args = get_parser().parse_args()
