# Proposed Integrated Syntax when using a combination of Horace, SpinW, Brill and MSlice
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

This document will include both working (mostly Matlab) and proposed (mostly Python) code examples.
Proposed code examples will be marked by black lines on either side of the code block.
The code examples will use a combination of Brille, SpinW, Horace and MSlice.


## Namespaces in the Python interface

The proposed Python interface for Horace is to use a [compiled library](../../python_interface/design/01_pace_python_high_level_discussion.md).
However, if more than one compiled Matlab library is loaded into Python,
there is a restriction that data cannot be passed directly between them, but must go through the Python host process, causing a performance bottle-neck.
This is because there may be incompatible application binary interfaces (ABIs) between the compiled Matlab libraries.
To avoid this problem, we propose to include all necessary programs for PACE (e.g. Horace and SpinW at a minimum) within a single compiled library, tentatively called "Pacy".
The Python wrapper module for this library will have submodules for Horace (`pacy.horace`), SpinW (`pacy.spinw`) and general Matlab functions (`pacy.matlab`).


## Workflow

The workflow is:

1. [Horace](https://github.com/pace-neutrons/Horace/) or *MSlice* is first used to extract (a subset of) the data to be modelled or fitted.
2. SpinW or Brille is then used to simulate the extracted data with some set of model parameters. 
The returned results should be of the same class as the data such that they may be easily plotted by Horace or MSlice.
3. If the model has parameters (e.g. SpinW), it should be possible to fit those parameters to the measured data.
4. For both fitting and simulation of a model, it should be possible to incorporate the instrumental resolution in the calculcation.

## Extracting the data

For single crystal data, this is currently possible in Matlab using Horace:

```matlab
proj = projaxes([1 0 0], [0 1 0]);
cut1 = cut_sqw(sqw_file, proj, [hmin hstep hmax], [kmin kstep kmax], [lmin lmax], [emin estep emax]);
```

The above example assumes that data processing to construct an `.sqw` file combining multiple measurements of a crystal at different orientations is done.
Triplets of numbers indicate that the data is to be rebinned along that axis (defined by the projection `proj`), whilst doublets indicates the data should be integrated between those ranges.
Thus the example generates a 3D `sqw` object `cut1` from the 4D data in the `sqw_file`.

The proposed syntax for Python is:

<table>
<td><img src="https://placehold.it/5x100/000000/000000?text=+"></td>
<td>
<pre lang="python">
from pacy import horace as h
proj = {'u':[1,0,0], 'v':[0,1,0], 'type':'rrr'}
cut1 = h.cut_sqw(sqw_file, proj, (hmin, hstep, hmax), (kmin, kstep, kmax), 
                                 (lmin, lmax), (emin, estep, emax))
</pre>
</td>
<td><img src="https://placehold.it/5x100/000000/000000?text=+"></td>
</table>

This syntax purposefully mirrors the Matlab usage, but we propose that the function definition follow more "Pythonic" lines:

<table>
<td><img src="https://placehold.it/5x100/000000/000000?text=+"></td>
<td>
<pre lang="python">
def cut_sqw(sqw_input: Union[Path, sqw],     # input is either path to sqw file or sqw object in memory
            proj: Dict[str, Any] = None,     # Defaults to: {'u':[1,0,0], 'v':[0,1,0], 'type':'rrr'}
            u_range: Optional[Tuple] = None,
            v_range: Optional[Tuple] = None,
            w_range: Optional[Tuple] = None,
            e_range: Optional[Tuple] = None,
            no_pix: Optional[bool] = False,  # If this is True, will return a dnd object, else sqw 
            ) -> Union[sqw, dnd]
</pre>
</td>
<td><img src="https://placehold.it/5x100/000000/000000?text=+"></td>
</table>

So that users need not specify all the positional arguments but could specify, e.g., `cut1 = h.cut_sqw(sqw_file, proj, e_range=(emin, estep, emax))`,
leaving the other range parameters their default values, `(-float('inf'), 0, float('inf'))` where a step of `0` means to use the step size of the data.

For powder data, data extraction is currently possible using the MSlice program.
There are two implementations of MSlice: [one](https://github.com/mantidproject/mslice) in Python as part of [Mantid](https://www.mantidproject.org)
and [the original](http://mslice.isis.rl.ac.uk/Main_Page) written in Matlab.
The original Matlab MSlice is mostly a GUI program with an undocumented CLI (by using the underlying functions of the GUI).
This program is also currently not being maintained so we will not use it.

In Python, the syntax to extract data from a powder measurement using Mantid MSlice is:

```python
import mslice.cli as m
dat2 = m.Load(nxs_file)
cut2 = m.Slice(d2, f'|Q|,{qmin},{qmax},{qstep}', f'DeltaE,{emin},{emax},{estep}')
```

Note that unlike in Horace, the original pixel information is not retained in this rebinning operation.

We propose the following syntax for powder data handling in Horace, should it be implemented:

<table>
<td><img src="https://placehold.it/5x70/000000/000000?text=+"></td>
<td>
<pre lang="matlab">
proj = projaxes('powder');
cut2 = h.cut_sqw(sqw_file, proj, [qmin, qstep, qmax], [emin, estep, emax]);
</pre>
</td>
<td><img src="https://placehold.it/5x70/000000/000000?text=+"></td>
</table>

This syntax should retain pixel information just like the equivalent single crystal invocation.


## Modelling the data

We assume that [SpinW](https://spinw.org/) would be used to model the magnetic excitations.
To set up and evaluate a model on single crystal data with current syntax in Matlab is:

```matlab
tri = sw_model('triAF', 1); 
spinw_pars = {'hermit', false, 'formfact', true, 'resfun', 'gauss'}; 
sim1 = disp2sqw_eval(cut1, @tri.horace_sqw, spinw_pars, fwhm);
```

This same syntax should also be possible (unchanged) for powder data, which has not been implemented.

In Python it would be:

<table>
<td><img src="https://placehold.it/5x70/000000/000000?text=+"></td>
<td>
<pre lang="python">
from pace import spinw as sw
tri = sw.sw_model('triAF', 1)
spinw_pars = {'hermit': False, 'formfact': True, 'resfun': 'gauss'}
sim1 = h.disp2sqw_eval(cut1, tri.horace_sqw, fwhm, **spinw_pars)
</pre>
</td>
<td><img src="https://placehold.it/5x70/000000/000000?text=+"></td>
</table>

[//]: # (**comment)

In addition to using SpinW directly, it is possible to use Brille to interpolate a SpinW model (in Matlab):

```matlab
tri = sw_model('triAF', 1); 
spinw_pars = {'hermit', false, 'formfact', true, 'resfun', 'gauss'}; 
brl_pars = {'max_volume', 1e-5};
brl = brillem.Brille(tri, brl_pars{:});
sim_cut = disp2sqw_eval(exp_cut, @brl.horace_sqw, spinw_pars, fwhm);
```

And the proposed Python syntax:

<table>
<td><img src="https://placehold.it/5x150/000000/000000?text=+"></td>
<td>
<pre lang="python">
import brille as b
tri = sw.sw_model('triAF', 1)
spinw_pars = {'hermit': False, 'formfact': True, 'resfun': 'gauss'}
brl_pars = {'max_volume':1e-5}
brl = b.Brille(tri, **brl_pars)
sim1 = h.disp2sqw_eval(cut1, brl.horace_sqw, fwhm, **spinw_pars)
</pre>
</td>
<td><img src="https://placehold.it/5x150/000000/000000?text=+"></td>
</table>

Again these syntax should work for powder data objects, possibly replacing `h.disp2sqw` with `m.disp2sqw` method of `MSlice` (yet to be implemented).


## Fitting the data with resolution convolution

Horace includes a fitting framework which uses a Levenberg-Marquardt minimizer.
The following example uses Brille and the TobyFit Monte Carlo resolution convolution method:

```matlab
proj = projaxes([1 0 0], [0 1 0]);
cut1 = cut_sqw(sqw_file, proj, [hmin hstep hmax], [kmin kstep kmax], [lmin lmax], [emin estep emax]);
model = pcsmo(JF1, JA, JF2, JF3, Jperp, D);   % User model defined as a function
model_pars = {'mat', {'JF1', 'JA', 'JF2', 'JF3', 'Jperp', 'D(3,3)'}, ...
              'hermit', false, 'optmem', 0, 'useFast', true, 'formfact', true, ...
              'resfun', 'gauss', 'coordtrans', diag([2 2 1 1])};
brl_pars = {'max_volume', 1e-5};
brl = brillem.Brille(model, brl_pars{:});
sample = IX_sample(true,[0,0,1],[0,1,0],'cuboid',[0.01,0.05,0.01]);
maps = maps_instrument(ei, freq, 'S');
cut1 = set_sample(cut1, sample);
cut1 = set_instrument(cut1, maps);
tbf = tobyfit(cut1);
tbf = tbf.set_fun (@brl.horace_sqw, {[J1 J2 J3 J4 J5 J6 0.1] model_pars{:}});
tbf = tbf.set_mc_points(5);
[data_out, fitdata] = tbf.fit();
```

The proposed Python syntax for this is:

<table>
<td><img src="https://placehold.it/5x400/000000/000000?text=+"></td>
<td>
<pre lang="python">
from pacy import horace as h
from pacy import spinw as sw
import brille as b
<br>
proj = {'u':[1,0,0], 'v':[0,1,0], 'type':'rrr'}
cut1 = h.cut_sqw(sqw_file, proj, [hmin, hstep, hmax], [kmin, kstep, kmax], 
                                 [lmin, lmax], [emin, estep, emax])
model = pcsmo(JF1, JA, JF2, JF3, Jperp, D)   # User model defined as a function
model_pars = {'mat':['JF1', 'JA', 'JF2', 'JF3', 'Jperp', 'D(3,3)'],
              'hermit':False, 'optmem', 0, 'useFast':True, 'formfact':True,
              'resfun':'gauss', 'coordtrans':np.diag([2 2 1 1])}
brl_pars = {'max_volume', 1e-5};
brl = b.Brille(model, brl_pars{:});
sample = h.IX_sample(True,[0,0,1],[0,1,0],'cuboid',[0.01,0.05,0.01]);
maps = h.maps_instrument(ei, freq, 'S');
cut1.set_sample(sample);
cut1.set_instrument(maps);
tbf = h.tobyfit(cut1);
tbf.set_fun(brl.horace_sqw, [J1, J2, J3, J4, J5, J6, 0.1], **model_pars);
tbf.set_mc_points(5);
data_out, fitdata = tbf.fit();
</pre>
</td>
<td><img src="https://placehold.it/5x400/000000/000000?text=+"></td>
</table>

[//]: # (**comment)

Similar syntax should also apply to powder data (Python implementations for fit may need to be added to MSlice).


## Implications for implementations

Whilst the handling of single crystal data is mostly complete for Matlab users, Python implementations and handling of powder data is still to be written.
There is a [prototype Python implementation](https://github.com/mducle/hugo) whose syntax is the basis for the syntax proposed in this document.
However, this implementation currently does not support fitting data, nor the use of a SpinW model (only a pure Python user model).
The main barrier at present to this work is inter-communications between Matlab and Python interpreters.
The fastest computations requires Matlab and Python to share the same process (which thus shares memory).
In this mode, a single instance of each interpreter is supported, but nested interpreters is not.
This is an issue because the built-in Matlab-Python bridge in Matlab automatically launches its own slave Python interpreter.
This causes an issue if the user is running Python and runs Horace through a slave Matlab interpreter.
The nested interpreters will then cause a hard-crash (segmentation fault memory error).

This is currently not an issue for SpinW (since it is a Matlab program), but is an issue for Euphonic.
It may become an issue for SpinW when `pySpinW` is fully implemented and released to users.
One option to overcome this issue is to run the interpreters in different processes, which would allow nested interpreters.
However, the current implementation for this in Matlab 2020a is extremely slow.
An alternative option specifically for `pacy` is to write a bridge `mex` file to communicate directly with the parent Python process
and funnel calls to Euphonic and `pySpinW` through this rather than the built-in Matlab-Python interface.

Handling of powder data is currently very poorly supported.
There exists a program, MSlice, with separate (non-compatible) Python and Matlab implementations.
However, in neither case does it support evaluation or fitting of user defined models.
Furthermore the Matlab implementation is no longer maintained.
Thus handling of powder data requires us to chose one of two approaches:

1. An implementation of powder data handling in Horace which leverages its fitting framework.
2. An implementation of a fitting framework (or wrappers to the base Mantid fitting framework) for MSlice.

Adopting approach 1 means that both Matlab and Python user interfaces could be supported in principle (using `pacy` for Python),
whereas option 2 will essentially mean that *powder data analysis would only be supported in Python and not Matlab*.
This is because running MSlice from Matlab would also require Mantid and would require a non-trivial set-up and installation.

There already exists a prototype powder handling implementation in Horace but it is not robust.
It is uncertain how much developer effort would be required to perfect this implementation, or if it should be rewritten.
Furthermore, the current powder analysis workflows only use Mantid/MSlice,
so that if we adopt approach 1 we should need users to additionally install `pacy` which is a very large download.
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
