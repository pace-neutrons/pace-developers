# Workflow examples using Horace, SpinW, and Brille
**2020-09-22**

## Table of Contents

[Introduction](#introduction)

[Workflow](#workflow)

[Extracting the data](#extracting-the-data)

[Modelling the data](#modelling-the-data)

[Fitting the data with resolution convolution](#fitting-the-data-with-resolution-convolution)

[Implications for implementations](#implications-for-implementations)

## Introduction

[Brille](https://github.com/brille/brille) is a C++ library with Python wrappings for symmetry operations and linear interpolation within an irreducible part of the first Brillouin Zone.
It can be used to construct the first Brillouin zone, find the high symmetry points and the irreducible polyhedron of any spacegroup.
In addition, it can be used to linearly interpolate any quantity (vector or scalar) which obeys the symmetries of the input spacegroup.
It is examples of this interpolating functionality that we shall explore in this document, specifically focusing on applications to magnetic time-of-flight neutron spectroscopy data.

This document includes both Matlab prototyped Python code examples.
The code examples will use a combination of Brille, SpinW, and Horace.
Additional unimplemented examples using MSlice are also proposed.


## Namespaces in the Python interface

The proposed Python interface for Horace is to use a [compiled library](../../python_interface/design/01_pace_python_high_level_discussion.md).
However, if more than one compiled Matlab library is loaded into Python,
there is a restriction that data cannot be passed directly between them, but must go through the Python host process, causing a performance bottle-neck.
This is because there may be incompatible application binary interfaces (ABIs) between the compiled Matlab libraries.
To avoid this problem, we propose to include all necessary programs for PACE (e.g. Horace and SpinW at a minimum) within a single compiled library, tentatively called "pyHorace".
The Python wrapper module for this library will have submodules for Horace (`pyHorace.horace`), SpinW (`pyHorace.spinw`) and general Matlab functions (`pyHorace.matlab`).
The prototype implementation, whose syntax is described below does not have these separate submodules however.
This may be implemented later to support more "Pythonic" syntax, which would require more extensive Python wrapper code.


## Workflow

The workflow is:

1. [Horace](https://github.com/pace-neutrons/Horace/) or *MSlice* is first used to extract (a subset of) the data to be modelled or fitted.
2. SpinW or Brille is then used to simulate the extracted data with some set of model parameters. 
The returned results should be of the same class as the data such that they may be easily plotted by Horace or MSlice.
3. If the model has parameters (e.g. SpinW), it should be possible to fit those parameters to the measured data.
4. For both fitting and simulation of a model, it should be possible to incorporate the instrumental resolution in the calculcation.

## Extracting the data

For single crystal data, using Horace in Matlab the syntax is:

```matlab
proj = projaxes([1 0 0], [0 1 0]);
cut1 = cut_sqw(sqw_file, proj, [hmin hstep hmax], [kmin kstep kmax], [lmin lmax], [emin estep emax]);
```

whilst in Python using the [prototype](https://github.com/mducle/hugo) it is:

```python
from pyHorace import Matlab as h
proj = {'u':[1,0,0], 'v':[0,1,0], 'type':'rrr'}
cut1 = h.cut_sqw(sqw_file, proj, [hmin, hstep, hmax], [kmin, kstep, kmax], 
                                 [lmin, lmax], [emin, estep, emax])
```

The above example assumes that the data has been processed into an `.sqw` file combining multiple measurements of a crystal at different orientations.
Triplets of numbers indicate that the data is to be rebinned along that axis (defined by the projection `proj`), whilst doublets indicates the data should be integrated between those ranges.
Thus the example generates a 3D `sqw` object `cut1` from the 4D data in the `sqw_file`.

Using the [Mantid](https://mantidproject.org) program similar 
[extraction of the data](https://github.com/tyst3273/Phonon-Explorer/blob/master/Python%20Code/Tools%20to%20access%20raw%20data/NXSAccessMantid.py)
can be done but the steps outlined below using SpinW and Brille will not work.
Mantid use may be supported in future (especially if it is decided to support the use of MSlice for powder data as noted below).

The above syntax uses only positional (non-keyword) arguments in the Python syntax.
This is because current prototype pyHorace implementation *must* mirror the Matlab syntax exactly
and Matlab does not support keyword arguments as a separate mechanism.
However, it might be more suitable for the Python syntax to use explicit keyword arguments instead.
This would require specific Python-side wrappings of the Matlab functions rather than the current generic wrapper.
With such (perhaps extensive) wrapping, a more "Pythonic" syntax can be achieved:

```python
def cut_sqw(sqw_input: Union[Path, sqw],     # input is either path to sqw file or sqw object in memory
            proj: Dict[str, Any] = None,     # Defaults to: {'u':[1,0,0], 'v':[0,1,0], 'type':'rrr'}
            u_range: Optional[Tuple] = None,
            v_range: Optional[Tuple] = None,
            w_range: Optional[Tuple] = None,
            e_range: Optional[Tuple] = None,
            no_pix: Optional[bool] = False,  # If this is True, will return a dnd object, else sqw
            ) -> Union[sqw, dnd]
```

For powder data, this is currently possible using the MSlice program.
There are two implementations of MSlice: [one](https://github.com/mantidproject/mslice) in Python as part of [Mantid](https://www.mantidproject.org)
and [the original](http://mslice.isis.rl.ac.uk/Main_Page) written in Matlab.
The original Matlab MSlice is mostly a GUI program with an undocumented CLI (by using the underlying functions of the GUI).
This program is also currently not being maintained.

In Python, the syntax to extract data from a powder measurement using Mantid MSlice is:

```python
import mslice.cli as m
dat2 = m.Load(nxs_file)
cut2 = m.Slice(d2, f'|Q|,{qmin},{qmax},{qstep}', f'DeltaE,{emin},{emax},{estep}')
```

Note that unlike in Horace, the original pixel information is not retained in this rebinning operation.

We propose the following syntax for powder data handling in Horace, should it be implemented:

```matlab
proj = projaxes('powder');
cut2 = h.cut_sqw(sqw_file, proj, [qmin, qstep, qmax], [emin, estep, emax]);
```

This syntax should retain pixel information just like the equivalent single crystal invocation.


## Modelling the data

We assume that [SpinW](https://spinw.org/) would be used to model the magnetic excitations.
To set up and evaluate a model on single crystal data with current syntax in Matlab is:

```matlab
tri = sw_model('triAF', 1); 
spinw_pars = {'hermit', false, 'formfact', true, 'resfun', 'gauss'}; 
sim1 = disp2sqw_eval(cut1, @tri.horace_sqw, spinw_pars, fwhm);
```

In Python it is:

```python
tri = h.sw_model('triAF', 1)
spinw_pars = ['hermit', False, 'formfact', True, 'resfun', 'gauss']
sim1 = h.disp2sqw_eval(cut1, tri.horace_sqw, fwhm, *spinw_pars)
```

As per [ADR #9](../../documentation/adr/0009-brille-integration.md), Brille is to be integrated within SpinW,
which would permit the Matlab syntax:

```matlab
tri = sw_model('triAF', 1); 
spinw_pars = {'hermit', false, 'formfact', true, 'resfun', 'gauss', ...
              'use_brille', true, 'node_fraction_volume', 1e-5}; 
sim1 = disp2sqw_eval(cut1, @tri.horace_sqw, spinw_pars, fwhm);
```

And in Python:

```python
tri = h.sw_model('triAF', 1)
spinw_pars = ['hermit', False, 'formfact', True, 'resfun', 'gauss',
              'use_brille', true, 'node_fraction_volume', 1e-5]
sim1 = h.disp2sqw_eval(cut1, tri.horace_sqw, fwhm, *spinw_pars)
```

Whilst these syntax currently work, their implementation is still in review and have yet to be fully tested or released.
The Python syntax also assumes that the Horace python distribution (`pyHorace`) will include SpinW as well as Horace.
This would enable both to use the same Matlab interpreter process, and make intercommunication much easier and faster.

Again these syntax should work for powder data objects, possibly replacing `h.disp2sqw`
with a (yet to be implemented) `m.disp2sqw` method of `MSlice`.


## Fitting the data with resolution convolution

Horace includes a fitting framework which uses a Levenberg-Marquardt minimizer.
The following example uses Brille and the TobyFit Monte Carlo resolution convolution method:

```matlab
proj = projaxes([1 0 0], [0 1 0]);
cut1 = cut_sqw(sqw_file, proj, [hmin hstep hmax], [kmin kstep kmax], [lmin lmax], [emin estep emax]);
model = pcsmo(JF1, JA, JF2, JF3, Jperp, D);   % User SpinW model defined as a function
model_pars = {'mat', {'JF1', 'JA', 'JF2', 'JF3', 'Jperp', 'D(3,3)'}, ...
              'hermit', false, 'optmem', 0, 'useFast', true, 'formfact', true, ...
              'resfun', 'gauss', 'coordtrans', diag([2 2 1 1]), ...
              'use_brille', 'node_volume_fraction', 1e-5, 'Qtrans', diag(1./[4 4 1])};
sample = IX_sample(true,[0,0,1],[0,1,0],'cuboid',[0.01,0.05,0.01]);
maps = maps_instrument(ei, freq, 'S');
cut1 = set_sample(cut1, sample);
cut1 = set_instrument(cut1, maps);
tbf = tobyfit(cut1);
tbf = tbf.set_fun (@model.horace_sqw, {[J1 J2 J3 J4 J5 J6 0.1] model_pars{:}});
tbf = tbf.set_mc_points(5);
[data_out, fitdata] = tbf.fit();
```

It is very similar in Python:

```python
from pyHorace import Matlab as h

proj = {'u':[1,0,0], 'v':[0,1,0], 'type':'rrr'}
cut1 = h.cut_sqw(sqw_file, proj, [hmin, hstep, hmax], [kmin, kstep, kmax], 
                                 [lmin, lmax], [emin, estep, emax])
model = pcsmo(JF1, JA, JF2, JF3, Jperp, D)   # User model defined as a function
model_pars = ['mat', ['JF1', 'JA', 'JF2', 'JF3', 'Jperp', 'D(3,3)'],
              'hermit', False, 'optmem', 0, 'useFast', True, 'formfact', True,
              'resfun', 'gauss', 'coordtrans', np.diag([2, 2, 1, 1]),
              'use_brille', 'node_volume_fraction', 1e-5, 'Qtrans', np.diag(1./[4, 4, 1])];
sample = h.IX_sample(True,[0,0,1],[0,1,0],'cuboid',[0.01,0.05,0.01]);
maps = h.maps_instrument(ei, freq, 'S');
cut1.set_sample(sample);
cut1.set_instrument(maps);
tbf = h.tobyfit(cut1);
tbf.set_fun(brl.horace_sqw, [J1, J2, J3, J4, J5, J6, 0.1], *model_pars);
tbf.set_mc_points(5);
data_out, fitdata = tbf.fit();
```

Note that Brille interpolation is currently buggy for some spin wave models.
This is because it assumes that all quantities it interpolates is periodic around the first (irreducible) Brillouin zone (BZ).
Whilst this is correct for the magnon energies (eigenvalues of the spin wave Hamiltonian),
it seems to be incorrect for the spin-spin correlation functions and neutron intensities. 
That is, in some cases the neutron intensities are periodic with a period several times the first Brillouin zone.
The temporary `Qtrans` parameter can be used as a crude workaround to produce a larger effective Brillouin zone.
This works by converting the `hkl` *Q*-values - e.g. in the above syntax `(444)` appears to Brille as `(114)`.
However, this means that degeneracies at the first BZ boundaries are poorly interpolated,
requiring a much larger grid for equivalent accuracy to when using the true first BZ.
(This is parameterised by a smaller `node_volume_fraction` value, and requires longer computation times.)

An alternative is to interpolate the eigen*vectors* of the spin wave Hamiltonian rather than the spin-spin correlation matrix.
This can be enabled with `'use_vectors', true` but results in significantly longer computation times.
This is partly because the spin-spin correlation matrix must be computed from the eigenvectors,
but also because a finer grid (smaller `node_volume_fraction`) is needed to get the required accuracy in the eigenvectors
to accurately compute the spin-spin correlation matrix.

Similar syntax should also apply to powder data (Python implementations for fit may need to be added to MSlice).


## Implications for implementations

Whilst the handling of single crystal data is mostly complete, handling of powder data is still to be written.
The [prototype Python implementation](https://github.com/mducle/hugo) is feature complete but not fully tested.
It will be described in detail in a separate design document.

Handling of powder data is currently very poorly supported.
There exists a program, MSlice, with separate (non-compatible) Python and Matlab implementations.
However, in neither case does it support evaluation or fitting of user defined models.
Furthermore the Matlab implementation is no longer maintained.
Thus handling of powder data requires us to chose one of two approaches:

1. An implementation of powder data handling in Horace which leverages its fitting framework.
2. An implementation of a fitting framework (or wrappers to the base Mantid fitting framework) for MSlice.

Adopting approach 1 means that both Matlab and Python user interfaces could be supported in principle (using `pyHorace` for Python),
whereas option 2 will essentially mean that *powder data analysis would only be supported in Python and not Matlab*.
This is because running MSlice from Matlab would also require Mantid and would require a non-trivial set-up and installation.

There already exists a prototype powder handling implementation in Horace but it is not robust.
Refactoring this to make it more robust is on the PACE roadmap, but depends on implementation of
[new APIs](https://github.com/pace-neutrons/Horace/blob/master/documentation/add/07-sqw_redesign.md) for the `sqw` and related classes in the Horace framework.
The timescale for the this work is currently uncertain but it is not anticipated that work on a powder implementation could begin for many months yet.

Furthermore, the current powder analysis workflows only use Mantid/MSlice,
so that if we adopt approach 1 we should need users to additionally install `pyHorace` which is a very large download.
On the other hand, they would need to install a similarly large download for SpinW as it is currently (part)-implemented in Python,
although it is planned in future to have a much more lightweight Python implementation.

Regarding approach 2, we estimate that it would take approximately 6-8 developer months to implement a fitting framework for MSlice.
This fitting framework would likely *not* use the built-in Mantid fitting framework which only handles 1D data.
Rather it would be better to use a standard Python library `scipy.optimize` (or a wrapper to it like `lmfit`).
It would take ~2-3 months to refactor the MSlice data objects to handle "pixel" data 
(to store an explicit transformation from plot coordinates to original data coordinates which is a one-to-many mapping; the data coordinates are fed to the user model).
An additional ~2-3 months is then needed to implement an interface to a python fitting library for the MSlice commandline.
Finally, testing the new framework would take 1-2 months.
This timeframe depends on an existing powder averaging library (perhaps from Euphonic)
and also assumes that Python versions of user model codes (e.g. `pySpinW`) exists and can be interfaced to without major development effort.

[//]: # (**comment)

