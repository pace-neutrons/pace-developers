# Phonopy Reader

Euphonic currently only interfaces directly with CASTEP, but there are other
modelling codes available. It might not be worthwhile to reinvent the wheel and
write interfaces for each individually, so instead Phonopy has been used as a
lingua franca to all other calculators. See the Phonopy docs on
[interfaces](https://phonopy.github.io/phonopy/interfaces.html#calculator-interfaces).

## Changes to Phonopy
To more ensure all data in consistent, it is recommended that Euphonic users
collect all their Phonopy data into a single `phonopy.yaml` file. This has been
allowed by adding `--include-x` flags to Phonopy, see this
[pull request](https://github.com/phonopy/phonopy/pull/108).

## Limitations

## Interpolation using a primitive axis

Euphonic currently cannot support reading force constants and interpolating
when `PRIMITIVE_AXIS`  has been used to generate the Phonopy force constants,
as the primitive cell and supercell may not be commensurate. This problem
comes from a difference in the phase convention between Euphonic and Phonopy.
Euphonic uses the **origin coordinate of each cell** in the supercell, whereas
Phonopy uses the **coordinate of each atom** in the supercell. You can convert
between these, and use the primitive and supercell matrices provided by
Phonopy to get the cell origin coordinate for each atom in the supercell:

```
import numpy as np
import yaml

with open('phonopy.yaml', 'r') as yaml_file:
    data = yaml.safe_load(yaml_file)

# To convert from unit cell to supercell
sc_matrix = data['supercell_matrix']
# To convert from unit cell to primitive cell
p_matrix = data['primitive_matrix']

# To convert from primitive cell to supercell
u_to_sc_matrix = np.einsum('ij,jk->ik',
                           np.rint(np.linalg.inv(p_matrix)).astype(np.int32),
                           sc_matrix)
# Number of primitive cells in the supercell
n_pcells_in_sc = np.rint(np.linalg.det(u_to_sc_matrix))

# p_ion_r are atom coordinates in primitive cell, in primitive cell fractional
# coordinates
p_n_ions = len(data['primitive_cell']['points'])
p_ion_r = np.zeros((p_n_ions, 3))
for i in range(p_n_ions):
    p_ion_r[i] = data['primitive_cell']['points'][i]['coordinates']

# sc_ion_r are atom coordinates in supercell, in supercell fractional
# coordinates
sc_n_ions = len(data['supercell']['points'])
sc_ion_r = np.zeros((sc_n_ions, 3))
for i in range(sc_n_ions):
    sc_ion_r[i] = data['supercell']['points'][i]['coordinates']

# Convert from supercell fractional coordinates to unit cell fractional
sc_ion_r_ucell = np.einsum('ij,jk->ik', sc_ion_r, u_to_sc_matrix)

# The first n_p_cells_in_sc coordinates are coordinates for atom #1, the
# second n_p_cells_in_sc coordinates are for atom #2 etc.
# Therefore, to get the cell origin for each atom, the fractional coordinate
# of each atom within the primitive cell must be subtracted
cell_origins = sc_ion_r_ucell - np.repeat(p_ion_r, n_p_cells_in_sc, axis=0)
```

If the primitive cell and supercell are commensurate (the `u_to_sc_matrix` is
diagonal), the `cell_origins` for atom #1 in the primitive cell (the first
`n_p_cells_in_sc` entries), will be the same for atom #2 (the second
`n_p_cells_in_sc` entries) etc. Phonopy only supports diagonal supercell
matrices, so as long as the user is performing a calculation with the unit
cell, this will be true. However, the primitive cell could be in any
orientation, so the cell origins of the unit cell for atom #1 will not always
be the same as atom #2, and some cell origins may lie outside the supercell.
This causes a problem for how Euphonic calculates phases, as it keeps a
`n_ions` length array of the cell origins, which can't work if the cell
origins for atom #1 are not the same as atom #2! Euphonic also assumes the
force constants matrix's first dimension is the same length as cell_origins.
One possible solution for this (although it has not been implemented) is
discussed in the next section.

### Solution

It is possible to re-map the force constants so that all atoms have the
same cell origins by creating a map which maps the cell origins of atoms
2 .. n onto the equivalent origins of atom 1 so that all atoms then share
the same cell origins. The equivalent cell origins are just
r<sub>1</sub>(J) - r<sub>1</sub>(1) where r<sub>1</sub>(J) is the
coordinate of atom 1 in supercell J. This map can then be used to reorder
the entries for atom j in the force constants matrix. This has been
implemented in [this PR](https://github.com/pace-neutrons/Euphonic/pull/56)
