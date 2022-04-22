#! /usr/bin/env python3
# euphonic 0.6.4+7.gded0c57

import sys

import matplotlib.pyplot as plt
import numpy as np

from euphonic.readers.phonopy import _extract_summary

def plot_cell(ax, vecs, trans=np.zeros((3, 3)), color=None):
    for i, vec in enumerate(vecs):
        ax.plot([0, vec[0]] + trans[0],
                [0, vec[1]] + trans[1],
                [0, vec[2]] + trans[2], color=color)

if len(sys.argv) > 1:
    summary_file = sys.argv[1]
else:
    raise ValueError('Input phonopy.yaml required')

cell_info = _extract_summary(summary_file, fc_extract=True)
vecs = cell_info['cell_vectors']
atom_r_cart = np.einsum('ij,jk->ik', cell_info['atom_r'], vecs)
sc_atom_r_cart = np.einsum('ij,jk->ik', cell_info['sc_atom_r'], vecs)

co_per_atom = cell_info['sc_atom_r'] - cell_info['atom_r'][cell_info['sc_to_pc_atom_idx']]
non_int = np.where(np.abs(co_per_atom
                          - np.rint(co_per_atom)) > 1e-5)[0]
if len(non_int) > 0:
    raise RuntimeError(
        f'Non-integer cell origins for atom(s) '
        f'{", ".join(non_int.astype(str))}, '
        f'check coordinates and indices are correct')
co_per_atom = np.rint(co_per_atom).astype(np.int32)
co_per_atom_cart = np.einsum('ij,jk->ik', co_per_atom, vecs)
_, co_idx = np.unique(co_per_atom, return_inverse=True, axis=0)
sc_atom_type = [cell_info['atom_type'][sc_idx] for sc_idx in cell_info['sc_to_pc_atom_idx']]
_, type_idx = np.unique(sc_atom_type, return_inverse=True)

markers = ['o', 'x', '^', 's', ]
colors = ['c', 'orange', 'm', 'g', 'r', 'b', 'y', 'indigo']

# Create plot
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# Plot original unit cell
for i in range(len(atom_r_cart)):
    ax.scatter(*atom_r_cart[i], color='k', alpha=0.5, marker='s', s=50)
# Plot supercell
for i, sc_atom_r_cart_i in enumerate(sc_atom_r_cart):
    marker = markers[type_idx[i]%len(markers)]
    color = colors[co_idx[i]%len(colors)]
    # Plot atoms
    ax.scatter(*sc_atom_r_cart_i, color=color, marker=marker)
    # Plot cell origins
    ax.scatter(*co_per_atom_cart[i], color=color, marker='*')
    # Plot cell vectors
    plot_cell(ax, vecs, trans=co_per_atom_cart[i], color=color)

plt.show()
