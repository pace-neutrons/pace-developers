# PACE Instrumental Resolution Convolution
**2020-04-06**

# Overview

Inelastic neutron scattering counts neutron absorption events as a function of
momentum, ![\mathbf{Q}], and energy, ![E], transferred from the neutron to the sample.
The *rate* at which events are detected is proportional to the so-called doubly-differential scattering cross section

![S(\mathbf{Q},E) \propto \frac{\partial^2\sigma}{\partial \mathbf{Q} \partial E}]

which is directly comparable to theoretical models for excitation processes in a condensed matter system.

The momentum transferred to the sample is the difference of the initial and final momenta of the neutron

![\mathbf{Q} = \mathbf{k}_\text{i} - \mathbf{k}_\text{f}]

and the energy transferred is the difference of the initial and final kinetic energy of the neutron

![E = \frac{\hbar^2}{2m_\text{n}}(k_\text{i}^2 - k_\text{f}^2)]

Neutron scattering instruments are typically constructed to allow an appreciable uncertainty in
the initial and final momenta of detected neutrons, ![\delta\mathbf{k}_\text{i}] and ![\delta\mathbf{k}_\text{f}], respectively.
These uncertainties naturally give rise to uncertainties in the momentum, ![\delta\mathbf{Q}], and energy, ![\delta E], transferred to the sample;
and therefore uncertainties in the doubly-differential cross section.
In the interest of simplified notation we can define a momentum-energy four vector ![\mathbb{Q} \equiv (\mathb{Q},E)], with uncertainty ![\delta\mathbb{Q}].
The uncertainty in momentum-energy at a given ideal momentum-energy point gives rise to the instrumental resolution function ![R(\mathbb{X};\mathbb{Q})].
The instrumental resolution is, in general, a scalar function of the four components of ![\mathbb{Q}] and we can define its variance along each component of ![\mathbb{Q}]

![V_i(\mathbb{Q}) \equiv \frac{\int d\mathbb{X} X_i^2 R(\mathbb{X};\mathbb{Q})}{\int d\mathbb{X} R(\mathbb{X};\mathbb{Q})} -\left(\frac{\int d\mathbb{X} X_i R(\mathbb{X};\mathbb{Q})}{\int d\mathbb{X} R(\mathbb{X};\mathbb{Q})}\right)^2]

from which we will always find ![\sqrt{\mathbb{V}(\mathbb{Q})} \propto \delta\mathbb{Q}(\mathbb{Q})].

In some cases it may be possible and desirable to approximate the instrumental resolution function by a hyperellipsoid.


The Proper Analysis of Coherent Excitations (PACE) requires the possibility of accounting for resolution effects when comparing
discreet measured inelastic neutron scattering data, ![S_i(\mathbb{Q}_i)],
to a continuous model scattering function, ![S(\mathbb{Q};\mathbf{p})].
In order to do so functionality to estimate the instrumental resolution ![R(\mathbb{X};\mathbb{Q})] and to compute its convolution with a continuous model

![R\left\{S(\mathbb{Q};\mathbf{p})\right\}\equiv\int R(\mathbb{X};\mathbb{Q})S(\mathbb{X};\mathbf{p})d\mathbb{X}]

must be provided.



# Context
In line with the model optimisation provided by PACE,
users will provide a function or class method which calculates and returns ![S(\mathbb{Q};\mathbf{p})]
at an array of ![\mathbb{Q}] values and constant model parameter values ![\mathbf{p}].
These user-provided scattering functions may account for some instrumental effects, e.g., slowly-varying backgrounds,
and are unlikely to account for resolution.
In cases where features of the model are of comparable size to the instrumental resolution an accurate estimate to model parameters will only be possible if the model is convoluted with the resolution _before_ comparison with measured intensity.

By providing the necessary resolution wrapper to user-provided ![S(\mathbb{Q};\mathbf{p})] models
PACE will enable the routine extraction of physically relevant parameters from measured inelastic neutron scattering data.

## Deliverables
- To be determined -- see [Possible Solutions](#possible-solutions) below


# Existing Solution
Resolution convolution is accomplished within the existing `multifit` framework through specialisation of the MATLAB class `mfclass`.
Like [`OptModel`] `mfclass` contains independent-variable array(s), foreground and background function(s) plus their parameters and meta information for fixing and binding-together parameters.

Additionally, `mfclass` supports 'wrapping' its foreground and background functions in arbitrary other functions by including a `mfclass_wrapfun` object.
When the `mfclass` methods `simulate()` or `fit()` are called the `mfclass_wrapfun` property's `wrap_functions_and_parameters()` method is used to

1. (optionally) initialise any temporarily cached values
2. construct the 'wrapped' functions which will be called with the independent-variable arrays, the `mfclass` foreground/background function properties, the cached information from the initialisation, and the parameters needed by the function(s)

A diagram showing the relationships between the classes of the `multifit` framework follows

![mfclass]

In the specific case of convoluting the instrumental resolution with one or more user-provided functions, a special class `mfclass_tobyfit` is used which has `mfclass` as its superclass.
Details required for the resolution estimation and integration are provided as additional properties of each `mfclass_tobyfit` object, and are initialised with sensible default values.
This enables resolution convoluted fitting to be performed by replacing, e.g., the call to `multfit_sqw()` in the [existing `multifit` solution] with a call to a different gateway function `tobyfit()`:

```matlab
obj = tobyfit(sqw_obj1 {, sqw_obj2, ...}); % object containing 1+ sqw object(s)
obj = obj.set_fun(@user_sqw_function, p_i); % define a foreground function
obj = obj.set_bfun(@user_bkg_function, p_j); % define a background function
obj = obj.set_free(...); % optionally fix foreground parameters
obj = obj.set_bfree(...); % optionally fix background parameters
obj = obj.set_bind(...); % optionally bind foreground parameters
obj = obj.set_bbind(...); % optionally bind background parameters
[sim_obj(s), p_fit] = obj.fit();  
```

The flexibility provided by the interaction of `mfclass`, `mfclass_tobyfit`, `mfclass_wrapfun`, and `mfclass_plist` comes with the significant drawback that the code is difficult to understand and therefore difficult to maintain.


[`OptModel`]: ../../optimisation/design/Model_Optimisation_Design.md#optimisation-model-object
[existing `multifit` solution]: ../../optimisation/design/Model_Optimisation_Design.md#existing-solution
[mfclass]: images/mfclass_diagram.png

# Possible Solutions

As part of the optimisation scheme a new class [`OptFunction`] will be created; objects of this class will contain information indicating whether their evaluation requires convolution with an estimate of the instrumental resolution.
Exactly how this should be accomplished has thus far been unaddressed -- this design document will rectify that deficiency.

There has been some discussion of implementing new methods for estimating the instrumental resolution of a direct-geometry time-of-flight spectrometer, e.g., making use of Monte Carlo ray-tracing to produce a probability distribution of neutron states incident on the sample along with analytic approximations to the secondary spectrometer.

Additionally, we have investigated new methods for performing the resolution convolution -- notably, reuse of in-resolution function evaluations for nearby detector pixels.

In order to support multiple ways of estimating the instrument resolution and performing the convolution we require a flexible resolution convolution scheme to be implemented in `OptFunction`.
Such a flexible scheme can be achieved in one of, at least, two ways:

1. Add new properties and methods directly to `OptFunction`
2. Create a new class, `ResScheme`, to hold the new properties and methods and add it as a property to `OptFunction` 

## Methods added to `OptFunction`
Adding the new properties and methods directly to `OptFunction` is unlikely to be the preferred solution, since it does not implement an easy way to hold extraneous information which may be necessary for only some resolution convolution schemes.
The extra information added to `OptFunction` may be

![OptFunction_extension]

One advantage to this approach is that the `convolute()` method would have direct access to all information about the user-defined function thereby simplifying its interface.

[OptFunction_extension]: images/OptFunction_extension.png

## New class added as property to `OptFunction`
An alternative approach is to produce a new abstract class `ResScheme` with only a single concrete property and method, `has_effect` and `does_anything()`, respectively.
`OptFunction` will be extended to contain a single `ResScheme`, and will only attempt to perform a resolution convolution if `OptFunction.scheme.does_anything()` returns `true`.
We can then produce any number of `ResScheme` subclasses to implement specific combinations of instrumental resolution estimation and convolution schemes, each of which can contain additional properties and methods as necessary.

Notably, we must produce `ResTobyfit` which reproduces the resolution estimation and convolution scheme present in `tobyfit`.
Other possible schemes include `ResRaytrace` which uses a ray-tracing-derived lookup table for ![\delta\mathbf{k}_\text{i}].

![ResScheme]

Classes which inherit from `ResScheme` and return true for `does_anything()` must implement a method `convolute()` to perform the convolution of their estimate to the instrumental resolution and the continuous model function at a set of specified ![\mathbb{Q}_i].
The `ResScheme.convolute()` method will likely need to take the `sqw` object(s) input to the `OptFunction`, `OptFunction.function` and `OptFunction.parameters` as input -- though one could envisage a very simple convolution scheme which would not require any of the information contained in the `sqw` beyond the input array(s) for `OptFunction.function`.

[ResScheme]: images/ResScheme.png


[`OptFunction`]: ../../optimisation/design/Model_Optimisation_Design.md#optimisation-function-object

## Usage
Under the assumption that implementing a new class is the best option, the adding `tobyfit` resolution convolution to a function in the `OptModel` scheme might be accomplished by:

``` matlab
% construct a function which takes only a parameter vector and returns a scalar
% for use as an overall multiplier:
multiplier = OptFunction(@(x) x(1), 'inputs', 0, 'parameters', [1.,]);

hklT = {'type', 'double', 'inputs', 4};
sqwT = {'type', 'sqw', 'inputs', 1};

% create a ResScheme object to use the tobyfit method of resolution convolution 
% optionally modifying any of the default tobyfit parameters, e.g., mcpoints
resTobyfit = ResTobyfit('mcpoints',50);

% construct OptFunction objects to represent a model of spinwave and a model of phonons
% only include resolution convolution with the spinwaves
sw_func = OptFunction(@spinwaves, hklT{:}, 'parameters', p_spinwave, 'scheme', resTobyfit);
ph_func = OptFunction(@phonons,   hklT{:}, 'parameters', p_phonon);  

bg = [OptFunction(@linear_in_h_bkg, hklT{:}, 'parameters', [1,0]), ...
      OptFunction(@incoherent_elastic, hklT{:}, 'parameters', [0]), ...
      OptFunction(@my_spurions, sqwT{:}, 'parameters', [1,2,3,4], 'fixed', [-1,0,1,0], 'binding', [@(p)-p(2)])];
% only the second and fourth parameters for @my_suprions are free:
%   the last is opposite in sign to the second,
%   the first is kept constant and will have a binding function automatically created
% the created OptFunction will have
%   bg(3).fixed == [2,0,1,0]
%	bg(3).binding == [@(p)-p(2), @(p)p(1)]
%   bg(3).mapping = [2,4]

% Create the OptModel object
% the first background function should be treated independently for each sqw
% and all other functions apply to all sqw objects
opt = OptModel([sqw_object_1, sqw_object_2], ...
               'foreground', [sw_func, ph_func],...
               'background', OptFunctionsArray(bg, 'applies', {-1,0,0}), ...
               'multiplier', multiplier);

% run the optimiser
opt.set_backend(...); % specified by name? extra meta parameter specification?
opt.optimise();

% pull out all fit parameters
p_fit = opt.get_parameters();
% or just those from the foreground function(s)
p_spinwave_and_phonon_fit = opt.get_foreground().get_parameters();
% or just one of the foreground functions
p_phonon_fit = opt.get_foreground().get_parameters(2);

```

# Alternative syntax
If the functionality within `mfclass_wrapfun` is used beyond `mfclass_tobyfit` or we desire to maintain its flexibility within `OptFunction`, then an alternative syntax could be used.

| Syntax | Alternative |
|--------|-------------|
| `OptFunction.scheme` | `OptFunction.wrapper` |
| `OptFunction.get_scheme()` | `OptFunction.get_wrapper()` |
| `OptFunction.set_scheme()` | `OptFunction.set_wrapper()` |
| `ResScheme` | `WrapScheme` |
| `ResScheme.convolute()` | `WrapScheme.wrap()` |

Supporting wrapping schemes beyond resolution convolution would likely require additional input checking within the `WrapScheme.wrap()` method, but would support, e.g., basic constant-Gaussian broadening which could be advantageous in some situations.

[//]: # (# Milestones)
[//]: # (# Feedback)
[//]: # (# Open Questions)



<!---
LaTeX equations used repeatedly can be defined as references, with format
	[latex_equation]: %-encoded link to image generator
then, if image generation fails for some reason, the alt-text for each equation
will still contain the raw LaTeX equation which is often intelligible

Constructing the %-encoded link can be done at, e.g., the codecogs website
	https://www.codecogs.com/eqnedit.php?latex=latex_equation
--->
[\mathbf{Q}]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7BQ%7D
[E]: https://latex.codecogs.com/svg.latex?E
[\omega]: https://latex.codecogs.com/svg.latex?%5Comega
[\mathbb{Q}]: https://latex.codecogs.com/svg.latex?%5Cmathbb%7BQ%7D
[\mathbb{Q}_i]: https://latex.codecogs.com/svg.latex?%5Cmathbb%7BQ%7D_i
[S_i(\mathbb{Q}_i)]: https://latex.codecogs.com/svg.latex?S_i%28%5Cmathbb%7BQ%7D_i%29
[S(\mathbb{Q})]: https://latex.codecogs.com/svg.latex?S%28%5Cmathbb%7BQ%7D%29
[S(\mathbb{Q};\mathbf{p})]: https://latex.codecogs.com/svg.latex?S%28%5Cmathbb%7BQ%7D%3B%5Cmathbf%7Bp%7D%29
[\mathbb{p}]: https://latex.codecogs.com/svg.latex?%5Cmathbb%7Bp%7D
[S(\mathbf{Q},E) \propto \frac{\partial^2\sigma}{\partial \mathbf{Q} \partial E}]: https://latex.codecogs.com/svg.latex?S%28%5Cmathbf%7BQ%7D%2C%20E%29%20%5Cpropto%20%5Cfrac%7B%5Cpartial%5E2%20%5Csigma%7D%7B%5Cpartial%20%5Cmathbf%7BQ%7D%20%5Cpartial%20E%7D
[\mathbb{Q} \equiv (\mathb{Q},E)]:https://latex.codecogs.com/svg.latex?%5Cmathbb%7BQ%7D%5Cequiv%28%5Cmathbf%7BQ%7D%2CE%29
[m]: https://latex.codecogs.com/svg.latex?m
[m,n,o,\ldots,p]: https://latex.codecogs.com/svg.latex?%5C%5Bm%2Cn%2Co%2C%5Cldots%2Cp%5C%5D
[N]: https://latex.codecogs.com/svg.latex?N
[p_3 = 1 - p_2]: https://latex.codecogs.com/svg.latex?p_3%20%3D%201%20-%20p_2

[\mathbf{Q} = \mathbf{k}_\text{i} - \mathbf{k}_\text{f}]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7BQ%7D%20%3D%20%5Cmathbf%7Bk%7D_%5Ctext%7Bi%7D%20-%20%5Cmathbf%7Bk%7D_%5Ctext%7Bf%7D
[E = \frac{\hbar^2}{2m_\text{n}}(k_\text{i}^2 - k_\text{f}^2)]: https://latex.codecogs.com/svg.latex?E%20%3D%20%5Cfrac%7B%5Chbar%5E2%7D%7B2m_%5Ctext%7Bn%7D%7D%28k_%5Ctext%7Bi%7D%5E2%20-%20k_%5Ctext%7Bf%7D%5E2%29
[\delta\mathbf{k}_\text{i}]: https://latex.codecogs.com/svg.latex?%5Cdelta%5Cmathbf%7Bk%7D_%5Ctext%7Bi%7D
[\delta\mathbf{k}_\text{f}]: https://latex.codecogs.com/svg.latex?%5Cdelta%5Cmathbf%7Bk%7D_%5Ctext%7Bf%7D
[\mathbf{k}_\text{i}]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bk%7D_%5Ctext%7Bi%7D
[\mathbf{k}_\text{f}]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bk%7D_%5Ctext%7Bf%7D
[\delta\mathbf{Q}]: https://latex.codecogs.com/svg.latex?%5Cdelta%5Cmathbf%7BQ%7D
[\delta E]: https://latex.codecogs.com/svg.latex?%5Cdelta%20E
[\delta\mathbb{Q}]: https://latex.codecogs.com/svg.latex?%5Cdelta%5Cmathbb%7BQ%7D
[R(\mathbb{Q}) \propto \delta\mathbb{Q}(\mathbb{Q})]: https://latex.codecogs.com/svg.latex?R%28%5Cmathbb%7BQ%7D%29%20%5Cpropto%20%5Cdelta%5Cmathbb%7BQ%7D%28%5Cmathbb%7BQ%7D%29
[R(\mathbb{X};\mathbb{Q})]: https://latex.codecogs.com/svg.latex?R%28%5Cmathbb%7BX%7D%3B%5Cmathbb%7BQ%7D%29
[R\left\{S(\mathbb{Q};\mathbf{p})\right\}\equiv\int R(\mathbb{X};\mathbb{Q})S(\mathbb{X};\mathbf{p})d\mathbb{X}]: https://latex.codecogs.com/svg.latex?R%5Cleft%5C%7BS%28%5Cmathbb%7BQ%7D%3B%5Cmathbf%7Bp%7D%29%5Cright%5C%7D%5Cequiv%5Cint%20R%28%5Cmathbb%7BX%7D%3B%5Cmathbb%7BQ%7D%29S%28%5Cmathbb%7BX%7D%3B%5Cmathbf%7Bp%7D%29d%5Cmathbb%7BX%7D
[V_i(\mathbb{Q}) \equiv \frac{\int d\mathbb{X} X_i^2 R(\mathbb{X};\mathbb{Q})}{\int d\mathbb{X} R(\mathbb{X};\mathbb{Q})} -\left(\frac{\int d\mathbb{X} X_i R(\mathbb{X};\mathbb{Q})}{\int d\mathbb{X} R(\mathbb{X};\mathbb{Q})}\right)^2]: https://latex.codecogs.com/svg.latex?V_i%28%5Cmathbb%7BQ%7D%29%20%5Cequiv%20%5Cfrac%7B%5Cint%20d%5Cmathbb%7BX%7D%20X_i%5E2%20R%28%5Cmathbb%7BX%7D%3B%5Cmathbb%7BQ%7D%29%7D%7B%5Cint%20d%5Cmathbb%7BX%7D%20R%28%5Cmathbb%7BX%7D%3B%5Cmathbb%7BQ%7D%29%7D%20-%5Cleft%28%5Cfrac%7B%5Cint%20d%5Cmathbb%7BX%7D%20X_i%20R%28%5Cmathbb%7BX%7D%3B%5Cmathbb%7BQ%7D%29%7D%7B%5Cint%20d%5Cmathbb%7BX%7D%20R%28%5Cmathbb%7BX%7D%3B%5Cmathbb%7BQ%7D%29%7D%5Cright%29%5E2
[\sqrt{\mathbb{V}(\mathbb{Q})} \propto \delta\mathbb{Q}(\mathbb{Q})]: https://latex.codecogs.com/svg.latex?%5Csqrt%7B%5Cmathbb%7BV%7D%28%5Cmathbb%7BQ%7D%29%7D%20%5Cpropto%20%5Cdelta%5Cmathbb%7BQ%7D%28%5Cmathbb%7BQ%7D%29