[Ab2tds Docs](http://ftp.esrf.fr/scisoft/AB2TDS/)  

# Running Ab2tds
## Preprocessing steps
Ab2tds has a few different steps to the calculation (BZ zone reconstruction, DW factor) and each needs specific parameters to match the Euphonic calculation. Each step outputs an .md5 file that must be used as input for the next step:

**BZ Reconstruction**
An example of this input can be found in `lzo/ab2tds/symmetry_input` in the repo (docs [here](http://ftp.esrf.fr/scisoft/AB2TDS/zone_reconstruction.html)). Required params:
* `APPLYTIMEREVERSAL = 0` Not sure whether this has an effect on the result
* `CALCULATECOMPLEMENT = 0` Don't know what this does
* `energy_scaling = 1.0`

**Debye-Waller factor**  
An example of this input can be found in `lzo/ab2tds/dw_input` in the repo (docs [here](http://ftp.esrf.fr/scisoft/AB2TDS/debye_waller.html)). Required params:
* `APPLYTIMEREVERSAL = 0` Not sure whether this has an effect on the result
* `Temperature = 100`

**Fourier Interpolation of Dynamical Matrix**  
An example of this input can be found in `lzo/ab2tds/fourier_input` in the repo (docs [here](http://ftp.esrf.fr/scisoft/AB2TDS/dynamicalFT.html)). This step might not be required if you're not using interpolation - need to test this. Required params:
* `APPLYTIMEREVERSAL = 0` Not sure whether this has an effect on the result
* `Nfour_interp = 4` This mostly depends on whether you're using Ab2tds to calculate structure factors with or without interpolation. If with interpolation I've found Nfour_interp = 4 on a CASTEP grid with phonon_fine_kpoint_mp_spacing = 0.005 works well for LZO. For insulators such as Quartz which have a longer range force constants matrix, I haven't yet found an mp_spacing/Nfour_interp combination that gives very accurate results

## S(Q,w) map calculation
### Without Interpolation  
This requires a .phonon file for the q-points you want to plot, a q-point grid file that has had the above preprocessing steps to be turned into an .md5 file and an input parameter file. Run with:  
`make_TDS_DispersionIntensityCurvesClone qpt_cut.phonon input_param_file qpt_grid.md5`   
An example input parameter file is at `lzo/ab2tds/fourier_input/011_scan/intensity_map_input.py`. This input file needs to match the specific cut you are simulating (docs [here](http://ftp.esrf.fr/scisoft/AB2TDS/DispersionIntensityCurvesClone.html)). Required params:
* `APPLYTIMEREVERSAL=0` Not sure whether this has an effect on the result
* `Temperature=100`
* `resolutionfile='resolution.txt'` A file with 2 columns; the energy in cm-1 and the value of the resolution function. 
  For benchmarking purposes, we don't want to apply a resolution function at all as that's not what we're testing. To try 
  and convolve with a delta function I tried:  
  ```-4  0.000000e+00
  -3  0.000000e+00
  -2  0.000000e+00
  -1  0.000000e+00
   0  1.000000e+00
   1  0.000000e+00
   2  0.000000e+00
   3  0.000000e+00
   4  0.000000e+00
   5  0.000000e+00
  ```
  But this still seems to leave some zig-zag artefacts on the S(Q,w) map. For benchmarking it is perhaps better to look at 
  the raw structure factors for each branch, which are output in the `alongthelineF.dat` file
* `Saturation=0.5` only affects the saturation in the displayed image, not in the data output to files, so doesn't really 
  matter what this value is
* `lowerLimit=0` This also only affects the displayed image, just set to 0
* `bottom_meV=0` Setting to 0 ignores negative frequencies
* `NEUTRONCALC=1` Needs to be set to 1 for neutron scattering (otherwise it does x-ray)
* `CohB={'La': 8.24, 'Zr': 7.16, 'O': 5.803}` This must be specified if NEUTRONCALC=1. A dictionary containing the coherent scattering lengths for each atom type
* `NeutronE=1e10` Ab2tds uses this to calculate Stokes scattering (usually applied to Raman scattering), to ignore this, this can be effectively set to 1 by setting an absurdly high neutron energy
* `branchWeight=np.ones(3*n_ions).tolist()` We want all phonon branches to be weighted the same, so use Numpy to make an 
  array of ones the same length as the number of branches
* `EigScal=0` Must be set to 0 (or, actually, any number except 1 or 2) for a neutron calculation
* `UniqueIon=-1` We want to use all ions in the calculation so set to -1  
**NOTE: the following 3 parameters are not documented as being required for S(Q,w) without interpolation but I've found they actually are required**
* `redStarts=[[0.0, 0.0, -6.0]]` - 2D array as its supposed to be an array of q-point starts for when you want to plot 
  multiple sections in reciprocal space. I've only used it for a single section, and set this as the first q-point in the 
  .phonon file
* `redEnds=[[0.0, 10.0, 4.0]]` - same as redStarts but for the last q-point in the .phonon file
* `Nqlines=[501]` - this is the number of q-points in the .phonon file. Again this is supposed to be the number of q- 
  points in each section that you want to plot, but I'm only plotting one section. That's why this value is a list rather 
  than just an integer.  

### With Interpolation
As we are testing Euphonic's interpolation and structure factor calculation,
rather than Ab2tds' interpolation, it has been decided not to validate against
Ab2tds' interpolation. Information about running Ab2tds with interpolation is
left here for completeness.

This requires a q-point grid file that has had the above preprocessing steps to be turned into an .md5 file, and an input parameter file. Run with:  
`make_TDS_DispersionIntensityCurves qpt_grid.md5 input_param_file`   
This input file needs to match the specific cut you are simulating (docs [here](http://ftp.esrf.fr/scisoft/AB2TDS/DispersionIntensityCurves.html)). I will only list the params that are different to the S(q,w) without interpolation calculation:
* `Nfour_interp=4` Set this to whatever was set in the 'Fourier interpolation of the dynamical matrix' preprocessing step
* `tth_max=45` This parameter isn't mentioned in the documentation but in the code is documented as 'When searching for 
  maximum contrast angles, the maximum 2theta angle achievable on the beamline'. This is used to calculate contrast in the 
  displayed image (_I think_) so shouldn't have any effect on the output, set to the default of 45.
* `Nqlines=[500]` - redStarts and redEnds can be set to the same as S(Q,w) without interpolation, but in this case Nqlines must actually be set as **number of q-points - 1**

# Ab2tds Output
Ab2tds has many output files, the most useful ones are:
* `res.dat` Contains the S(Q,w) map with resolution, each row is an energy bin and each column is a q-point
* `alongthelineF.dat` Contains the raw (non energy-binned) structure factors for each branch and q-point. Each row is a q-point and each column is a branch

# Comparing Euphonic and Ab2tds

For details on the comparison, see
[here](https://github.com/pace-neutrons/euphonic-validation/blob/9a76831/shared/compare_data/validate_ab2tds.ipynb)