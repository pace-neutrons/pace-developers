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
`n_p_cells_in_sc` entries) etc. As long as the user is performing a
calculation with a diagonal supercell/primitive matrix, this will be true.
However, for non-diagonal matrices, the cell origins of the unit cell for
atom #1 will not always be the same as atom #2, and some cell origins may
lie outside the supercell. This causes a problem for how Euphonic calculates
phases, as it keeps a `n_ions` length array of the cell origins, which can't
work if the cell origins for atom #1 are not the same as atom #2! Euphonic
also assumes the force constants matrix's first dimension is the same length
as cell_origins. One possible solution for this (although it has not been
implemented) is discussed in the next section.

### Incomplete Solution

It is possible to re-map the force constants so that all atoms have the
same cell origins by creating a map which maps the cell origins of atoms
2 .. n onto the equivalent origins of atom 1 so that all atoms then share
the same cell origins. The equivalent cell origins are just
r<sub>1</sub>(J) - r<sub>1</sub>(1) where r<sub>1</sub>(J) is the
coordinate of atom 1 in supercell J. This map can then be used to reorder
the entries for atom j in the force constants matrix. This has been
implemented in [this PR](https://github.com/pace-neutrons/Euphonic/pull/56)

### Follow-up solution

After implementing the above solution, problems were found with interpolation
for more complex materials (see
[this issue](https://github.com/pace-neutrons/Euphonic/issues/77)) which
revealed several further issues with converting the force constants matrix
from Phonopy's shape to Euphonic's:

 - Incorrect assumptions about the order of atoms in Phonopy's supercell. To
   resolve this the `'reduced_to'` field in `phonopy.yaml` is instead used
   which explicity describes which primitive atom corresponds to which
   supercell atom. This resulted in incorrect calculations of the cell origins
   map, which has now been corrected.
 - Incorrect calculation of the single matrix to transform from the primitive
   cell to the supercell. Phonopy contains 2 matrices, one to transform from
   **unit** cell vectors -> **super**cell vectors, and one to transform from
   **unit** cell vectors -> **primitive** cell vectors, whereas Euphonic
   doesn't make the distinction between primitive and unit cells the way Phonopy
   does, so only defines a single matrix. This should be the one to convert
   from the **primitive** cell vectors -> **super**cell vectors. This calculated
   by matrix multiplying the inverse transpose of the unit -> prim matrix by
   the unit -> super matrix.
 - Incorrect assumptions about the force constants matrix shape. Phonopy defines
   its force constants matrix with a series of 2 integers `(n_patom, n_satom)`
   where n_patom is the index of the atom in the primitive cell, and n_satom is
   the index of the atom in the supercell. However, each `n_patom` doesn't
   actually correspond to atoms in the **same** primitive cell. In
   `phonopy.yaml` each atom has a `reduced_to` integer which describes which
   supercell atom it corresponds to. It is **this** 'reduced' atom in the
   supercell that is referred to by `n_patom` rather than the primitive atoms
   themselves. As a result, these 'reduced' atoms are not necessarily in the
   same primitive cell. Because Euphonic's interpolation uses cell phases rather
   than atomic phases, the force constants must be rearranged so that each `(n_patom,)`
   part is from the same cell (lets choose the cell at the origin). This can be
   done by figuring out which `celli -> cellj` vectors are equivalent to which
   `0 -> cellk` vectors (this is done in `_get_supercell_relative_idx()`) and
   rearranging them accordingly. In this case the `cell_origins` must also be
   recentered about the origin.

These changes have been made in
[this commit](https://github.com/pace-neutrons/Euphonic/commit/64a3c527be0b97ab190cb6430867cc02ce8a5592)
