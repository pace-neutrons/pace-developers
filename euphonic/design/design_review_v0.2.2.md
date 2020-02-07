# Review of v0.2.2 design

# Current class hierarchy

<img align="center" src="images/euphonic_classes_v0.2.2.png">

All Euphonic objects are based on a main `Data` superclass. This contains any
methods that can apply to both vibrational or electronic data e.g. DOS
calculations.

`BandsData` - This contains **electronic** data. It mainly exists to enable
reading of CASTEP `.bands` files to maintain parity with CASTEP's
`dispersion.pl` and `dos.pl` scripts

`PhononData` - This contains **vibrational** data read from a `.phonon` file.
It always contains frequencies/eigenvectors, and has methods to calculate the
structure factor, Debye-Waller factor

`InterpolationData` - This is a subclass of `PhononData` and contains the force
constants matrix, and maybe frequencies/eigenvectors if they have been
calculated. It wraps the `PhononData` class functions to check if there are any
frequencies/eigenvectors before attempting to calculate the structure factor,
Debye-Waller factor

# Plotting

Plotting functions are in `euphonic.plot` rather than being object methods, and
plots are made with Matplotlib.

`euphonic.plot` also contains some functions for outputting Grace files for
plotting, but these are not routinely tested, and I'm reluctant to maintain
them. Again they are mainly there to provide similar functionality to CASTEP's
`dispersion.pl` and `dos.pl` scripts

# Units
Units are implemented with the `pint` package, internally all units are in
atomic units (Hartree, bohr radius, electron mass etc.), but when a user
accesses an attribute, it is wrapped as a Pint Quantity and returned as the
appropriate unit. e.g. `PhononData` has a `_freqs` attribute which is in
Hartree, but the user should access `freqs` which is a property that returns
`_freqs` wrapped and converted to the appropriate units (default 'meV').

The user can change the units that quantities are returned in by using the
`change_e_units` method, which changes the `_e_units` attribute which is a
string which is used by the `freqs` property, for example, to convert units.

# Current API Example
Example of interpolating and plotting an S(Q, w) map:

```
from euphonic.data.interpolation import InterpolationData
from euphonic.plot import plot_sqw_map
from euphonic.util import mp_grid

# Read data
idata = InterpolationData.from_castep('quartz')

# This uses seekpath to generate a 'recommended' q-point path
_, unique_ions = np.unique(idata.ion_type, return_inverse=True)
structure = (idata.cell_vec.magnitude, idata.ion_r, unique_ions)
qpts = skp.get_explicit_k_path(structure)["explicit_kpoints_rel"]

# Interpolate phonons
idata.calculate_fine_phonons(qpts, asr='reciprocal')

# Calculate phonons on a grid for Debye-Waller factor
dw_idata = InterpolationData.from_castep('quartz')
dw_idata.calculate_fine_phonons(mp_grid([5,5,5]), asr='reciprocal')

# Calculate S(Q,w) map
scattering_lengths = {'Si': 4.1491, 'O': 5.803}
ebins = np.arange(0, 160, 0.5)
idata.calculate_sqw_map(scattering_lengths, ebins, dw_data=dw_idata, T=300)

# Plot S(Q,w) map
fig, ims = plot_sqw_map(idata, ewidth=1.0)
fig.show()
```

# Issues with current design
 - `BandsData` doesn't really fit in
 - `InterpolationData` may or may not contain frequencies, this could be
 confusing, and you have to specifically check for them
- Currently, it's inconsistent whether things are returned from methods or
stored in the object. E.g. the sqw_map quietly gets stored in the
`PhononData`/`InterpolationData` object, but the (unbinned) structure factors
just get returned. What to do when we have different kinds of structure factor
(coherent crystal/powder, incoherent)? It needs to be made more consistent
- Class/attribute naming could be improved

See [proposed design](design_proposal_from_v0.2.2.md)

