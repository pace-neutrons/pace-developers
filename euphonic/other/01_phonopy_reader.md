# Phonopy Reader

Euphonic currently only interfaces directly with CASTEP, but there are other
modelling codes available. It might not be worthwhile to reinvent the wheel and
write interfaces for each individually, so instead Phonopy has been used as an
interface to many other codes. See the Phonopy docs on
[interfaces](https://phonopy.github.io/phonopy/interfaces.html#calculator-interfaces).

## Changes to Phonopy
To more ensure all data in consistent, it is recommended that Euphonic users
collect all their Phonopy data into a single `phonopy.yaml` file. This has been
allowed by adding `--include-x` flags to Phonopy, see this
[pull request](https://github.com/phonopy/phonopy/pull/108).

## Converting Phonopy's Force Constants to Euphonic's

### Difficulties with a non-diagonal supercell matrix or primitive matrix

Reading the force constants from a Phonopy calculation which has a
non-diagonal supercell matrix or primitive matrix has some subtle
difficulties, as in that case the primitive cell and supercell will not be
commensurate. This problem comes from a difference in the phase convention
between Euphonic and Phonopy. Euphonic uses the **origin coordinate of each
cell** in the supercell, whereas Phonopy uses the **coordinate of each atom**
in the supercell. You can convert between these, and use the primitive and
supercell matrices provided by Phonopy to get the cell origin coordinate for
each atom in the supercell.

In `phonopy.yaml` each atom in the supecell has a `reduced_to` coordinate
which describes which atom in the unit cell it corresponds to. If the primitive
cell and supercell are commensurate (the matrix to convert from the primitive
cell to supercell is diagonal), the `cell_origins` for each atom where
`reduced_to=1` will be a unique list, and this list will be the same as the
list for where `reduced_to=2` etc. However, for non-diagonal matrices these
lists will not always be the same, and some cell origins may lie outside the
supercell. This causes a problem for how Euphonic calculates phases, as it
keeps a `n_cells_in_supercell` length array of the cell origins, which can't
work if the cell origins for atom #1 are not the same as atom #2! The initial
solution for this is discussed in the next section.

### Initial solution

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
