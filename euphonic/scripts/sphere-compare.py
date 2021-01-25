#! /usr/bin/env python3
# euphonic 0.3.2+94.g92306dd

import argparse
import functools
import os
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np

from euphonic import ureg, Quantity
from euphonic.force_constants import ForceConstants
from euphonic.plot import _plot_1d_core
from euphonic.powder import sample_sphere_dos, sample_sphere_structure_factor

from compare_spectra import diff_1d, diff_1d_avg


def get_parser() -> argparse.ArgumentParser:
    sampling_choices = {'golden', 'sphere-projected-grid',
                        'spherical-polar-grid', 'spherical-polar-improved',
                        'random-sphere'}

    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    parser.add_argument('--dos', action='store_true',
                        help="Compute phonon DOS instead of coherent S")
    parser.add_argument('--npts', '-n', nargs='+', type=int, default=[1000])
    parser.add_argument('--sampling', type=str, nargs='+',
                        default=['golden'], choices=sampling_choices)
    parser.add_argument('--jitter', type=str, nargs='+', default=['y'],
                        help="Sequence of 'y', 'n' corresponding to sampling")
    parser.add_argument('-q', type=float, nargs='+', default=[0.1],
                        help=("mod(q) radius of sampled sphere in reciprocal "
                              "angstrom"))
    parser.add_argument('--bin-width', '-b', type=float, default=0.1,
                        dest='bin_width',
                        help="width of DOS bins in meV")
    parser.add_argument('--smear-width', '-s', nargs='+', dest='smear_width',
                        type=float, default=[1.],
                        help="width of DOS smearing in meV")
    parser.add_argument('--ref-npts', default=int(1e5), type=int,
                        dest='ref_npts',
                        help="Number of qpoints for reference data")
    parser.add_argument('--title', type=str, default=None)
    return parser


def get_spectrum(force_constants: ForceConstants,
                 *,
                 bin_width: Quantity,
                 max_energy: Quantity,
                 q: Quantity = (0.1 * ureg('1/angstrom')),
                 npts: int = 1000,
                 sampling: str = 'golden',
                 jitter: bool = True,
                 dos: bool = False,
                 smear_width: Optional[Quantity] = (1 * ureg('meV'))):

    assert isinstance(q, Quantity)

    energy_bins = np.arange(0,
                            (max_energy.to('meV').magnitude),
                            bin_width.to('meV').magnitude) * max_energy.units

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


def str2bool(str_bool: str) -> bool:
    if str_bool.lower() in ('y', 'yes', 't', 'true'):
        return True
    elif str_bool.lower() in ('n', 'no', 'f', 'false'):
        return False
    else:
        raise ValueError(f"Could not intepret string '{str_bool}' as bool.")


@functools.lru_cache()
def get_ref_spectrum(force_constants, *, q, max_energy, npts, dos, bin_width):
    print("Calculating reference spectrum: "
          f"q = {q}, npts = {npts}")
    return get_spectrum(force_constants,
                        max_energy=max_energy,
                        bin_width=bin_width,
                        npts=npts, q=q, dos=dos,
                        sampling='golden', jitter=False,
                        smear_width=None)


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
    filename = args.file
    summary_name = os.path.basename(filename)
    path = os.path.dirname(filename)

    all_options = {}
    comparison_options = []

    ordered_keys = ['npts', 'q', 'smear_width', 'sampling']

    for key in ordered_keys:
        value = getattr(args, key)
        if len(value) == 1:
            all_options[key] = value[0]
        else:
            comparison_options.append(key)
            all_options[key] = value

    all_options['smear_width'] = all_options['smear_width'] * ureg('meV')

    fixed_options = {key: value for (key, value) in all_options.items()
                     if key not in comparison_options}

    if 'q' in fixed_options:
        fixed_options['q'] = fixed_options['q'] * ureg('1/angstrom')
    else:
        all_options['q'] = [q * ureg('1/angstrom') for q in all_options['q']]

    if len(comparison_options) > 2:
        raise ValueError("Can't plot this many options yet, sorry! "
                         "Please only provide multiple choices for one of: "
                         "npts, q, smear-width, sampling")

    if len(args.sampling) > 1:
        if len(args.jitter) == 1:
            jitter_options = args.jitter * len(args.sampling)
        elif len(args.jitter) != len(args.sampling):
            raise ValueError("Either give a single jitter value, or they "
                             "should correspond to sampling choices.")
        else:
            jitter_options = args.jitter

        jitter_options = list(map(str2bool, jitter_options))
    elif len(args.jitter) > 1:
        raise ValueError("Multiple jitter values should be accompanied by "
                         "multiple sampling values. (These can be repeated as "
                         "appropriate.)")

    else:
        fixed_options['jitter'] = str2bool(args.jitter[0])

    bin_width = args.bin_width * ureg('meV')

    comparison_key = comparison_options[0]
    comparison_values = all_options[comparison_key]

    if len(comparison_options) > 1:
        row_key = comparison_options[1]
        row_values = all_options[row_key]
    else:
        row_key = next(x for x in ordered_keys if x not in comparison_options)
        row_values = [fixed_options[row_key]]
        del fixed_options[row_key]

    force_constants = ForceConstants.from_phonopy(
        path=path, summary_name=summary_name)

    # Energy range: Gamma-point maximum + 20%
    max_energy = np.max(force_constants
                        .calculate_qpoint_phonon_modes(np.array([[0, 0, 0]]))
                        .frequencies.to('meV').magnitude) * 1.2 * ureg('meV')

    fig, axes = plt.subplots(nrows=len(row_values), ncols=3, squeeze=False
                               # figsize=(10, 10)
                             )

    # Link axes ranges
    for i, (data_ax, box_ax, err_ax) in enumerate(axes):
        if i == 0:
            ref_axes = (data_ax, box_ax, err_ax)
        else:
            data_ax.sharey(ref_axes[0])
            box_ax.sharey(ref_axes[1])
            err_ax.sharey(ref_axes[2])

    labels = []

    for row_index, row_value in enumerate(row_values):
        data_ax, box_ax, err_ax = axes[row_index, :]

        box_data = []
        box_labels = []
        rms_data = []
        rel_data = []

        for i, value in enumerate(comparison_values):
            options = fixed_options.copy()
            options.update({comparison_key: value,
                            row_key: row_value,
                            'max_energy': max_energy,
                            'bin_width': bin_width,
                            'dos': args.dos})
            if comparison_key == 'sampling':
                options.update({'jitter': jitter_options[i]})
            elif row_key == 'sampling':
                options.update({'jitter': jitter_options[row_index]})

            ref_spectrum = get_ref_spectrum(force_constants,
                                            max_energy=max_energy,
                                            npts=args.ref_npts,
                                            dos=args.dos,
                                            bin_width=bin_width,
                                            q=options['q']
                                            ).broaden(options['smear_width'],
                                                      shape='gauss')

            if (i == 0) and (comparison_key != 'q'):
                _plot_1d_core(ref_spectrum, data_ax)
                if (row_index == 0):
                    labels.append("Reference")

            print("Calculating spectrum: ",
                  ", ".join([f'{key}={_label_print(value)}'
                             for key, value in options.items()]))
            spectrum = get_spectrum(force_constants, **options)

            diff = diff_1d(spectrum, ref_spectrum)
            box_data.append(diff.magnitude)

            rms = diff_1d_avg(spectrum, ref_spectrum, rms=True, fractional=True)
            rms_data.append(rms.magnitude)
            # rms_rel = diff_1d_avg(spectrum, ref_spectrum,
            #                       rms=True, fractional=True)
            mean_err = diff_1d_avg(spectrum, ref_spectrum, rms=False)

            if comparison_key == 'sampling':
                label_rotation = 30
                if options['jitter']:
                    label_prefix = options['sampling'] + " (jittered)"
                    box_label = label_prefix
                else:
                    label_prefix = options['sampling']
                    box_label = label_prefix
            else:
                label_rotation = None
                label_prefix = f"{comparison_key}: {value}"
                box_label = _label_print(value)

            labels.append(f"{label_prefix} - mean err {mean_err:6.3E~P}")
            box_labels.append(box_label)

            _plot_1d_core(spectrum, data_ax)

        data_ax.set_xlabel('Energy / meV')
        data_ax.set_ylim(0, None)

        box_ax.boxplot(box_data, labels=box_labels, showmeans=False)
        box_ax.set_xticklabels(box_labels, rotation=label_rotation, ha="right")
        box_ax.set_ylabel('Residuals')
        box_ax.set_xlabel(comparison_key)

        if row_key == 'sampling' and jitter_options[row_index]:
            row_suffix = ' (jittered)'
        else:
            row_suffix = ''
        box_ax.set_title(f'{row_key}: {row_value}{row_suffix}')

        if comparison_key in ('sampling',):
            err_x_vals = range(len(all_options[comparison_key]))
        elif comparison_key in ('q', 'smear_width'):
            err_x_vals = [x.magnitude for x in all_options[comparison_key]]
        else:
            err_x_vals = all_options[comparison_key]

        err_ax.plot(err_x_vals, rms_data, '-o')
        err_ax.set_yscale('log')
        
        if comparison_key in ('sampling',):
            err_ax.set_xticks(err_x_vals)
            err_ax.set_xticklabels(box_labels, rotation=label_rotation, ha="right")
        err_ax.set_xlabel(comparison_key)
        err_ax.set_ylabel('RMS error (relative)')



    if len(row_values) in spacing_data:
        spacing = spacing_data[len(row_values)]
    else:
        spacing = spacing_data[max(spacing_data)]

    data_ax.legend(labels, loc='upper center',
                   bbox_to_anchor=spacing['legend_bbox'], ncol=2)

    fig.subplots_adjust(left=0.1, right=0.98, wspace=0.5,
                        **spacing['subplots_kwargs'])

    if args.title:
        fig.suptitle(args.title)

    plt.show()


if __name__ == '__main__':
    main()
