#! /usr/bin/env python3
# euphonic 0.3.2+94.g92306dd

import argparse
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np

from euphonic import ureg, Quantity
from euphonic import ForceConstants
from euphonic.cli.utils import force_constants_from_file

from euphonic.plot import _plot_1d_core, _plot_2d_core
from euphonic.powder import sample_sphere_dos, sample_sphere_structure_factor

from compare_spectra import diff_1d, diff_1d_avg


def get_parser() -> argparse.ArgumentParser:
    sampling_choices = {'golden', 'sphere-projected-grid',
                        'spherical-polar-grid', 'spherical-polar-improved',
                        'random-sphere'}

    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', type=str)
    parser.add_argument('--dos', action='store_true',
                        help="Compute phonon DOS instead of coherent S")
    parser.add_argument('--npts', '-n', type=int, default=1000)
    parser.add_argument('--sampling', type=str, default='golden',
                        choices=sampling_choices)
    parser.add_argument('--jitter', action='store_true')
    parser.add_argument('-q', type=float, nargs='+', default=[0.1],
                        help=("mod(q) radius of sampled sphere in reciprocal "
                              "angstrom"))
    parser.add_argument('--bin-width', '-b', type=float, default=0.1,
                        dest='bin_width',
                        help="width of DOS bins in meV")
    parser.add_argument('--smear-width', '-s', dest='smear_width',
                        type=float, default=1.,
                        help="width of DOS smearing in meV")
    parser.add_argument('--ref-npts', default=int(1e4), type=int,
                        dest='ref_npts',
                        help="Number of qpoints for reference data")
    parser.add_argument('--title', type=str, default=None)
    return parser


def get_spectrum(force_constants: ForceConstants,
                 *,
                 energy_bins: Quantity,
                 q: Quantity = (0.1 * ureg('1/angstrom')),
                 npts: int = 1000,
                 sampling: str = 'golden',
                 jitter: bool = True,
                 dos: bool = False,
                 smear_width: Optional[Quantity] = (1 * ureg('meV'))):

    assert isinstance(q, Quantity)

    if dos:
        sampling_function = sample_sphere_dos
    else:
        sampling_function = sample_sphere_structure_factor

    spectrum = sampling_function(force_constants, mod_q=q, npts=npts,
                                 sampling=sampling, jitter=jitter,
                                 energy_bins=energy_bins)

    if smear_width is None:
        return spectrum
    else:
        return spectrum.broaden(smear_width, shape='gauss')


def _label_print(value: Union[str, Quantity, int, float]) -> str:
    if isinstance(value, Quantity):
        return str(value.magnitude)
    else:
        return str(value)


def plot(spectrum, ax, **mplargs):
    x_unit = spectrum.x_data_unit
    y_unit = spectrum.y_data_unit
    x_vals = spectrum._get_bin_centres('x').to(x_unit).magnitude
    y_vals = spectrum.y_data.to(y_unit).magnitude

    ax.plot(x_vals, y_vals, linewidth=0.5, **mplargs)

    ax.set_xlabel(f'Energy / {x_unit}')
    ax.set_ylabel(f'Intensity / {y_unit}')


def get_ref_spectrum(force_constants, *, q, energy_bins, npts,
                     dos, smear_width=None):
    print("Calculating reference spectrum: "
          f"q = {q}, npts = {npts}")

    return get_spectrum(force_constants,
                        energy_bins=energy_bins,
                        npts=npts, q=q, dos=dos,
                        sampling='golden', jitter=False,
                        smear_width=smear_width)


spacing_data = {1: {'legend_bbox': (1.8, -0.2),
                    'subplots_kwargs': {'bottom': 0.4, 'hspace': 0.2,
                                        'top': 0.85}},
                2: {'legend_bbox': (1.8, -0.3),
                    'subplots_kwargs': {'bottom': 0.4, 'hspace': 0.5,
                                        'top': 0.94}},
                3: {'legend_bbox': (2, -0.45),
                    'subplots_kwargs': {'bottom': 0.3, 'hspace': 0.7,
                                        'top': 0.95}}}


def main():
    args = get_parser().parse_args()
    bin_width = args.bin_width * ureg('meV')
    smear_width = args.smear_width * ureg('meV')

    fig = plt.figure(constrained_layout=True, figsize=(10, 10))
    gs = fig.add_gridspec(len(args.files), 4)

    rel_err_ax = fig.add_subplot(gs[:, 2:])

    abs_q_series = np.array(args.q) * ureg('1/angstrom')

    for row_index, filename in enumerate(args.files):
        spectrum_ax = fig.add_subplot(gs[row_index, 0])
        error_ax = fig.add_subplot(gs[row_index, 1])

        force_constants = force_constants_from_file(filename)

        # Use geometric mean for a representative reciprocal lattice distance
        recip_cell = force_constants.crystal.reciprocal_cell()
        recip_lattice_constant = np.power(np.product(
            np.linalg.norm(recip_cell.magnitude, axis=1)),
                                          1/3) * recip_cell.units
        rel_q_series = abs_q_series / recip_lattice_constant

        # Energy range: Gamma-point maximum + 20%
        max_energy = np.max(force_constants
                            .calculate_qpoint_phonon_modes(np.array([[0, 0, 0]]))
                            .frequencies.to('meV').magnitude) * 1.2 * ureg('meV')
        energy_bins = np.arange(0,
                                (max_energy.to('meV').magnitude),
                                bin_width.to('meV').magnitude) * max_energy.units

        from euphonic.spectra import Spectrum2D
        ref_spectrum_2d = None

        box_data = []
        abs_rms_err = []
        rel_rms_err = []
        z_data = []

        for q_index, q in enumerate(abs_q_series):
            options = dict(q=q, energy_bins=energy_bins, dos=args.dos, smear_width=smear_width)

            ref_spectrum = get_ref_spectrum(force_constants,
                                            npts=args.ref_npts,
                                            **options)

            print(f"Calculating spectrum: q={q.magnitude}")
            spectrum = get_spectrum(force_constants, npts=args.npts, **options)

            diff = diff_1d(spectrum, ref_spectrum)
            box_data.append(diff.magnitude)

            # rms = diff_1d_avg(spectrum, ref_spectrum, rms=True, fractional=True)
            # rms_data.append(rms.magnitude)
            rel_rms_err.append(diff_1d_avg(spectrum, ref_spectrum,
                                           rms=True, fractional=True))
            abs_rms_err.append(diff_1d_avg(spectrum, ref_spectrum,
                                           rms=True, fractional=False).magnitude)

            z_data.append(ref_spectrum.y_data.magnitude)
        ref_spectrum_2d = Spectrum2D(abs_q_series, energy_bins,
                                     np.array(z_data) * ureg(ref_spectrum.y_data_unit))
        _plot_2d_core(ref_spectrum_2d, spectrum_ax)

        spectrum_ax.set_xlabel('|q| / recip. angstom')
        spectrum_ax.set_ylim(0, None)

        error_ax.boxplot(box_data, positions=abs_q_series, showmeans=False)
        error_ax.set_xlabel('|q| / recip. angstom')
        error_ax.set_ylabel('Residuals')

        error_ax.plot(abs_q_series.magnitude, abs_rms_err, color=f'C{row_index}')

        rel_err_ax.plot(rel_q_series.magnitude, rel_rms_err, color=f'C{row_index}')
    rel_err_ax.set_xlabel('|q| / normalised')
    rel_err_ax.set_ylabel('Relative error')
    rel_err_ax.set_yscale('log')

    rel_err_ax.legend(labels=args.files)

    if args.title:
        fig.suptitle(args.title)

    plt.show()


if __name__ == '__main__':
    main()
