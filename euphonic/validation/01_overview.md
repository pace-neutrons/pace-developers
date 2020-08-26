# Euphonic Validation

For Euphonic to be a reliable piece of scientific software it must be validated,
both against other software and experimental data. 

There are 4 types of output that must be validated:
- Coherent crystal structure factor (resolved by q-point and phonon mode)
- Coherent crystal inelastic neutron scattering intensities (binned in q and
energy)
- Interpolated frequencies
- Interpolated eigenvectors

For details on how these are calculated see [here](../design/04_algorithms.md)

## Repositories

The repository for storing validation scripts/results is at
https://github.com/pace-neutrons/euphonic-validation. This will store the
results from OClimax/Ab2tds/Euphonic, but also the input files required to
rerun them.

The experimental data files are too large to be hosted on Github, so will be
stored on a SAN file server, see
[here](https://github.com/pace-neutrons/Horace/blob/58df1c0/documentation/adr/0012-use-network-storage-for-large-datafiles.md).

## Chosen software
- [**Ab2tds**](03_ab2tds.md) will be used to verify the coherent crystal
structure factor calculation
- [**OClimax**](02_oclimax.md) will be used to verify the coherent crystal
inelastic neutron scattering intensities
- **CASTEP** and **Phonopy** will be used to verify interpolated frequencies
- A combination of **CASTEP**, **Phonopy**, and **OClimax** will be used to
verify the interpolated eigenvectors

Details on why each of these pieces of software have been chosen are below

**Coherent crystal structure factor**

This is the structure factor calculated per q-point and per phonon mode, so
hasn't yet been binned in energy. This allows direct testing of the structure
factor calculation, without any artefacts created by binning or instrumental
broadening. To test the structure factor calculation only (rather than
interpolation) the phonon frequencies and eigenvectors must be read from a
common source, a CASTEP `.phonon` file. Currently, only [Ab2tds](03_ab2tds.md)
can provide the mode resolved coherent crystal structure factors as output, so
this will be used for comparison.

**Coherent inelastic neutron scattering intensities**

This has been binned in energy and what is measured experimentally. Both
[OClimax](02_oclimax.md) and [Ab2tds](03_ab2tds.md) can calculate this and
output to a file. However, the instrumental resolution in Ab2tds can't be turned
off and results in strange [artefacts](03_ab2tds.md#visual-comparison) that make
a fair numerical comparison difficult. As a result, only OClimax will be used
for validating intensities. Again, to test the intensity calculation only rather
than the interpolation, the frequencies and eigenvectors must be read from a
common source. As OClimax and Euphonic can both read CASTEP `.phonon` and
Phonopy files, both of these will be used for testing intensities with OClimax.

**Interpolated frequencies**

Euphonic can calculate phonon frequencies from force constants read from CASTEP 
`.castep_bin` and Phonopy `phonopy.yaml` files. These 2 pieces of software can
also calculate their own phonon frequencies and output them to files which
Euphonic can read, so both CASTEP and Phonopy will be used to verify Euphonic's
interpolated frequencies

**Interpolated eigenvectors**

Eigenvectors are harder to test, they cannot be directly numerically compared as
for degenerate modes the eigenvectors are an arbitrary mix in the degenerate
subspace. However, this will not have an effect on physical observables, (as
this will result in a sum over the degenerate modes) so the scattering
intensities can still be compared. So, to test the interpolated eigenvectors the
results from the following pipelines must be compared:

```
Phonopy force constants -> Phonopy interpolation -> OClimax intensities
Phonopy force constants -> Euphonic interpolation -> Euphonic intensities
CASTEP force constants -> CASTEP interpolation -> OClimax intensities
CASTEP force constants -> Euphonic interpolation -> Euphonic intensities
```
## Comparison with software
**Discussion:**
One option to get a good variety of points for comparison with OClimax and
Ab2tds would be to produce a 'spaghetti' plot of high-symmetry paths, which
would get good coverage over the 1st Brillouin Zone, and use a set of random
q-points across a wide range of +/-Q values, to get good coverage of low
symmetry points and test the effect of quantities such as the Debye-Waller
factor at high Q. This is possible with Euphonic, however, both Ab2tds and
OClimax expect straight lines through Q-space (for OClimax see the `Q_vec`
parameter [here](02_oclimax.md#single-crystal-parameters), for Ab2tds see the
`redStarts` parameter [here](03_ab2tds.md#without-interpolation)). Computing at
a set of random points would therefore not be possible without running
OClimax/Ab2tds once for each random q-point. Something like a spaghetti plot may
be possible with Ab2tds using an array of `redStarts` parameters, but producing
this with OClimax would need it to be run once for each q-direction.

**Conclusion:**
As random points/spaghetti plots will be either difficult/impossible with
Ab2tds/OClimax, it has been decided to simulate a variety of experimental data
cuts, 2-3 Q-E cuts for each material. These should be a mix of high/low symmetry
and high/low Q.

## Comparison with experimental data
Euphonic will be verified against cuts of experimental data in
[Horace](https://github.com/pace-neutrons/Horace). The cuts chosen must varied:
cover a large range in +/-Q, and have a variety of low and high energy modes.
For some materials a 'spaghetti' plot of a path through the 1st BZ might be
appropriate to validate calculations across the whole zone.

Horace simulation functions (specifically `disp2sqw`) will be used to run
Euphonic from Horace and create .sqw objects from Euphonic data.

## Chosen Materials
A variety of materials have been chosen for validation: small/large unit cells,
with/without the dipole-dipole term correction, and calculated with a variety of
simulation codes.

|Material|Instrument|Simulation Code|Atoms/unit cell|Cells/supercell|Dipole Correction?|
|--------|----------|---------------|---------------|---------------|------------------|
|La<sub>2</sub>Zr<sub>2</sub>O<sub>7</sub>|MERLIN|CASTEP|22|4|No|
|Quartz|MERLIN|CASTEP|9|100|Yes|
|Niobium|LET|CASTEP|1|1728|No|

## Metrics

The metrics used for validation will be mean and maximum absolute error, and
mean and max relative error. The mean absolute error is defined as:
<p><img align="center" src="http://chart.apis.google.com/chart?cht=tx&chl=\frac{\sum_{i=1}^{n}|y_i-x_i|}{n}"/></p>

And the mean relative error is defined as:
<p><img align="center" src="http://chart.apis.google.com/chart?cht=tx&chl=\frac{1}{n}\sum_{i=1}^{n}\frac{|y_i-x_i|}{x_i}"/></p>

For comparing structure factors and frequencies, the mean/max absolute error is
meaningful, as they both have a defined unit (e.g. meV) so can be used for
comparison. However, as values of the structure factor at Bragg peaks may be
extremely large, this may give an unrepresentative value, so it might make sense
to exclude these values from the calculation, use a relative error tolerance, or
simply just test that they give some 'large' value.

Neutron scattering intensities may be subject to an arbitrary scaling factor so
comparing absolute values doesn't make sense. For comparing intensities the
mean/max relative error will be used. However, for near zero values of
intensity, the relative error may be unrepresentatively large. In this case,
this would require use of an absolute error tolerance.

In all cases it might be sensible to calculate both an absolute and relative
error.