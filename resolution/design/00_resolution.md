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

The uncertainty at a given ideal measurement point gives rise to the instrumental resolution function, ![R(\mathbb{Q};\mathbb{Q}_0)].
The instrumental resolution function is continuous in momentum-energy space, ![\mathbb{Q}], and is a functional of the configuration where the instrument is set to record intensity, ![\mathbb{Q}_0] &mdash; the resolution function typically depends on much more than *just* ![\mathbb{Q}_0], but precisely *what* it depends on is instrument dependent and beyond the scope of this document.
We can define the components of the ![4\times4] covariance matrix of the instrumental resolution function at ![\mathbb{Q}] as

![V_{ij}(\mathbb{Q}) \equiv \frac{\int d\mathbb{X} X_i X_j R(\mathbb{X};\mathbb{Q})}{\int d\mathbb{X} R(\mathbb{X};\mathbb{Q})} - \frac{\int d\mathbb{X} X_i R(\mathbb{X};\mathbb{Q})}{\int d\mathbb{X} R(\mathbb{X};\mathbb{Q})}\frac{\int d\mathbb{X} X_j R(\mathbb{X};\mathbb{Q})}{\int d\mathbb{X} R(\mathbb{X};\mathbb{Q})}]

where the integrals over ![\mathbb{X}] cover all momentum-energy space, and the ![X_i], ![X_j] are components of the orthonormal basis therein.

In some cases it may be desirable to approximate the instrumental resolution function by a hyperellipsoid defined from the covariance matrix.

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

By providing the necessary resolution wrapper to user-provided ![S(\mathbb{Q};\mathbf{p})] models,
PACE will enable the routine extraction of physically relevant parameters from measured inelastic neutron scattering data.

## Deliverables
- modifications to the `OptModel`, `OptFunctions`, and `OptFunction` classes
- a new `OptFunction` subclass, `TobyfitOptFunction` to perform resolution convolution following the `tobyfit` scheme
- possibly more `OptFunction` subclasses to perform resolution convolution following other schemes


# Existing Solution
Resolution convolution is accomplished within the existing `multifit` framework through specialisation of the MATLAB class `mfclass`.
Like [`OptModel`], `mfclass` contains independent-variable array(s), foreground and background function(s) plus their parameters and meta information for fixing and binding-together parameters.

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

The flexibility provided by the interaction of `mfclass`, `mfclass_wrapfun`, and `mfclass_plist` comes with the significant drawback that code utilising these classes can be difficult to understand and maintain.

Specifically in the case of `mfclass_tobyfit`, only some of the information and none of the proceedures required to perform the resolution convolution are provided within the class as properties and methods.
The remaining information is produced when a special tobyfit-defined private method of the `sqw` class is stored as a property of and called by a method of `mfclass_wrapfun`, and the entire convolution proceedure is implemented as another tobyfit-defined public method of the `sqw` class which is also stored as a property of and called by a method of `mfclass_wrapfun`.


[`OptModel`]: ../../optimisation/design/Model_Optimisation_Design.md#optimisation-model-object
[existing `multifit` solution]: ../../optimisation/design/Model_Optimisation_Design.md#existing-solution
[mfclass]: images/mfclass_diagram.png

# Proposed Solution
The solution proposed here is driven by the aspiration that all of the machinery required to carry out a resolution convolution method should be part of the class which implements the scheme.
This in turn will hopefully improve the chances that someone first encountering PACE will be able to easily understand and maintain the resolution convolution functionality.

As part of the [optimisation scheme] a new class [`OptFunction`] will be created; objects of this class are not intended to handle instrumental resolution convolution.
Instead resolution effects will be dealt with by extending `OptFunction` with one or more new classes.

There has been some discussion of implementing new methods for estimating the instrumental resolution of a direct-geometry time-of-flight spectrometer, e.g., making use of Monte Carlo ray-tracing to produce a probability distribution of neutron states incident on the sample along with analytic approximations to the secondary spectrometer.

Additionally, we have investigated new methods for performing the resolution convolution &mdash; notably, reuse of in-resolution function evaluations for nearby detector pixels.

In order to support multiple ways of estimating the instrument resolution and performing the convolution we require a flexible resolution convolution scheme to be implemented in conjunction with `OptFunction`.

## `OptFunction` subclasses
`OptFunction` will be extended to include an `initialise()` method which performs no action by default, and a `simulate()` method which calls the `initialise()` method before the `evaluate()` method. Same-named similar extensions will be added to `OptFunctions` as well.
The two 'gateway' methods, `simulate()` and `optimise()`, in `OptModel` will be modified to first call its contained `OptFunctions` objects' `initialise()` and then to continue utilising a private `evaluate()` method to finish simulating or optimising the model.
The `initialise()` and `evaluate()` methods of `OptFunction` and `OptFunctions` should be accessible only to objects of the classes intended to hold them, namely `OptFunctions` and `OptModel`, respectively.

With these changes we can then implement a new subclass of `OptFunction` for any resolution convolution scheme.
Notably, we must produce `TobyfitOptFunction` which reproduces the resolution estimation and convolution scheme in `tobyfit`.
Other possible schemes include `RaytracedResolutionOptFunction` which uses a ray-tracing-derived lookup table for ![\delta\mathbf{k}_\text{i}];
and `Kernel2DOptFunction` which uses a user-defined two dimensional kernel to 'smooth' an `axes` model in the same way that the independent data has been smoothed.

![OptFunction_subclasses]

[OptFunction_subclasses]: images/OptFunction_subclasses.png
[optimisation scheme]: ../../optimisation/design/Model_Optimisation_Design.md
[`OptFunction`]: ../../optimisation/design/Model_Optimisation_Design.md#optimisation-function-object

## Possible (partial) implementation
The requisite methods for `OptModel`, `OptFunctions`, and `OptFunction` to support resolution covolution subclasses could be implemented as

```matlab
classdef OptModel
    properties
        multipliers {mustBeOptFunctions} = [];
        foregrounds {mustBeOptFunctions} = [];
        backgrounds {mustBeOptFunctions} = [];
    end
    methods
        function varargout = simulate(obj, varargin)
            obj.initialise();
            varargout = obj.evaluate(varargin{:});
        end
        function varargout = optimise(obj, varargin)
            obj.initialise();
            % optimisation implemented here
            varargout = obj.evaluate(varargin{:});
        end
    end
    methods (Access = private)
        function initialise(obj)
            obj.multipliers=obj.multipliers.initialise();
            obj.foregrounds=obj.foregrounds.initialise();
            obj.backgrounds=obj.backgrounds.initialise();
        end
        function varargout = evaluate(obj, varargin)
            % evaluation of M*F+B implemented here
        end
    end
end
```
```matlab
classdef OptFunctions
    properties
        reduction_operator
        optfunctions {mustBeOptFunction} = [];
    end
    methods
        function varargout = simulate(obj, varargin)
            obj.initialise();
            varargout = obj.evaluate(varargin{:});
        end
    end
    methods (Access = {?OptModel})
        function obj=initialise(obj)
            for i=1:numel(obj.optfunctions)
                obj.optfunctions(i)=obj.optfunctions(i).initialise();
            end
        end
        function varargout = evaluate(obj, varargin)
            % implement reduction of optfunctions evaluations
        end
    end
end
```
```matlab
classdef OptFunction
    methods
        function varargout = simulate(obj, varargin)
            obj.initialise();
            varargout = obj.evaluate(varargin{:});
        end
    end
    methods (Access = {?OptFunctions})
        function obj=initialise(obj)
        end
        function varargout = evaluate(obj, varargin)
            % implement evaulation
        end
    end
end
```

Then the `tobyfit` resolution convolution scheme could be implemented similar to
```matlab
classdef TobyfitOptFunction < OptFunction
    properties (Access=public)
        mc_points {mustBePositive,mustBeInteger}
    end
    properties (Access=public, Hidden)
        crystal_refinement_parameters {mustBeTobyfitSampleRefinement} = [];
        moderator_refinement_parameters {mustBeTobyfitModeratorRefinement} = [];
        cached_lookup_tables {mustBeTobyfitLookup} = [];
    end
    properties (Access=private)
        mc_contributions_
    end
    properties (Dependent, Hidden)
        mc_contributions
    end
    methods
        function obj = set.mc_contributions(obj, varargin)
            obj = mc_contributions_parse(obj, varargin{:});
        end
        function mcc = get.mc_contributions(obj)
            mcc = obj.mc_contributions_;
        end
        function varargout = simulate(obj,varargin)
            obj.initialise();
            varargout = evaluate(obj,varargin{:});
        end
    end
    methods (Access = {?OptFunctions})
        function obj=initalise(obj)
            % handle cached-lookup table creation
            obj.cached_lookup_tables = TobyfitLookup(obj);
        end
        function RSofQE = evaluate(obj,varargin)
            % actually performs the convolution using the instrumental
            % resolution estimate as in tobyfit and a Monte Carlo
            % integration for each independent Q,E point in the sqw(s)
            %
            % tobyfit models must take (h,k,l,e,p,...) as input and return
            % only S(Q,E) as output, so the interaction here doesn't need
            % to be terribly flexible.
            % Other OptFunction subclasses may instead make use of
            % evaluate@OptFunction(obj,varargin{:}), if it helps.
            RSofQE = obj.do_convolution();
        end
    end
end
```

## Usage
With a full implementation following the outline above, adding resolution convolution following the `tobyfit` scheme to two `OptFunction` objects which are combined into a `OptModel` for simulation and fitting might be accomplished as in the following.

``` matlab
% construct OptFunction objects to represent a model of spinwave and a model of phonons
hklT = {'type', 'double', 'inputs', 4}; % Common parameters for spinwave and phonon OptFunctions
sw_func = TobyfitOptFunction(@spinwaves, hklT{:}, 'parameters', p_spinwave);
ph_func = TobyfitOptFunction(@phonons, hklT{:}, 'parameters', p_phonon);

% construct the OptFunctions object to handle inter-foreground-function parameter binding
% and combining the functions outputs (reduction)
fg_funcs = OptFunctions([sw_func, ph_func)], 'reduction', '+');

% Create the OptModel object
%   Note: without a specified 'multiplier' or 'background' sensible defaults are
%         provided, namely @(x)1 and @(x)0, respectively.
opt = OptModel([sqw_object_1, sqw_object_2], 'foreground', fg_funcs);
```

# Converting `mfclass_tobyfit` to `TobyfitOptFunction`
Some of the functionality of `tobyfit`, e.g., fitting crystal orientation or moderator lineshape parameters, is implemented in `mfclass_tobyfit` by setting a property of the class to be a `struct` with a documented set of fields.
If the `struct` is set then a number of parameters are appended to the standard user-function parameters which are stripped-off again before the user-function is evaluated.

In `TobyfitOptFunction` the `struct` parameters should be replaced with assert-style validated object parameters, `TobyfitSampleRefinement` and `TobyfitModeratorRefinement`, and the `OptFunction` parameter accessor methods should be overloaded to get and set any additional refinement parameters.

In the `simulate()` and `fit()` methods of `mfclass_tobyfit` an initialisation function is called to construct a `struct` which contains information useful in estimating the instrumental resolution, including de-duplicated copies of instrument component probability distribution lookup tables.
The content of this `struct` depends on the input set of `sqw` objects and so can only be determined once the input is defined &mdash; this precludes the possibility of storing its information within the `sqw` objects directly.
When the resolution estimate is convoluted with the user-function this `struct` is passed as part of the function call.

For `TobyfitOptFunction` the passed `struct` tables should be replaced with an assert-style validated object parameter, `TobyfitLookup`.
Where the call to `OptFunction.initialise()` does nothing, the call to `TobyfitOptFunction.initialise()` will construct the `TobyfitLookup` object and store it within the `TobyfitOptFunction` object for use in the convolution.
Storing the new object inside of `TobyfitOptFunction` will simplify the convolution method call and could allow eventually for avoided table-recreation if a suitable hash of the inputs to `simulate()` can be devised.

# Milestones
1. Additions added to `OptModel`, `OptFunctions`, and `OptFunction`
2. `TobyfitOptFunction` created by translation from `mfclass_tobyfit`
      1. creation of new `TobyfitLookup` class to replace `struct` lookup table
      2. creation of new `TobyfitModeratorRefinement` class to replace `struct` moderator parameter property
      3. creation of new `TobyfitSampleRefinement` class to replace `struct` sample parameter property
3. New `OptFunction` subclasses, depending on development of new schemes and requirements

[//]: # (# Feedback)
[//]: # (# Open Questions)



<!---
LaTeX equations used repeatedly can be defined as references, with format
	[latex_equation]: %-encoded link to image generator
then, if image generation fails for some reason, the alt-text for each equation
will still contain the raw LaTeX equation which is often intelligible

Constructing the %-encoded link can be done at, e.g., the codecogs website
	http://www.codecogs.com/eqnedit.php?latex=latex_equation
--->
[\mathbf{Q}]: svg/mathbfQ.svg
[E]: svg/E.svg
[X_i]: svg/Xi.svg
[X_j]: svg/Xj.svg
[\omega]: svg/omega.svg
[\mathbf{p}]: svg/mathbfp.svg
[\mathbb{Q}]: svg/mathbbQ.svg
[\mathbb{X}]: svg/mathbbX.svg
[\mathbb{Q}_0]: svg/mathbbQ0.svg
[\mathbb{Q}_i]: svg/mathbbQi.svg
[S_i(\mathbb{Q}_i)]: svg/SimathbbQi.svg
[S(\mathbb{Q})]: svg/SmathbbQ.svg
[S(\mathbb{Q};\mathbf{p})]: svg/SmathbbQmathbfp.svg
[\mathbb{p}]: svg/mathbbp.svg
[S(\mathbf{Q},E) \propto \frac{\partial^2\sigma}{\partial \mathbf{Q} \partial E}]: svg/SmathbfQEproptofracp.svg
[\mathbb{Q} \equiv (\mathb{Q},E)]:svg/mathbbQequivmathbQE.svg
[m]: svg/m.svg
[m,n,o,\ldots,p]: svg/mnoldotsp.svg
[N]: svg/N.svg
[p_3 = 1 - p_2]: svg/p31p2.svg

[\mathbf{Q} = \mathbf{k}_\text{i} - \mathbf{k}_\text{f}]: svg/mathbfQmathbfktextim.svg
[E = \frac{\hbar^2}{2m_\text{n}}(k_\text{i}^2 - k_\text{f}^2)]: svg/Efrachbar22mtextnkte.svg
[\delta\mathbf{k}_\text{i}]: svg/deltamathbfktexti.svg
[\delta\mathbf{k}_\text{f}]: svg/deltamathbfktextf.svg
[\mathbf{k}_\text{i}]: svg/mathbfktexti.svg
[\mathbf{k}_\text{f}]: svg/mathbfktextf.svg
[\delta\mathbf{Q}]: svg/deltamathbfQ.svg
[\delta E]: svg/deltaE.svg
[\delta\mathbb{Q}]: svg/deltamathbbQ.svg
[R(\mathbb{Q}) \propto \delta\mathbb{Q}(\mathbb{Q})]: svg/RmathbbQproptodeltam.svg
[R(\mathbb{Q};\mathbb{Q}_0)]: svg/RmathbbQmathbbQ0.svg
[R(\mathbb{X};\mathbb{Q})]: svg/RmathbbXmathbbQ.svg
[R\left\{S(\mathbb{Q};\mathbf{p})\right\}\equiv\int R(\mathbb{X};\mathbb{Q})S(\mathbb{X};\mathbf{p})d\mathbb{X}]: svg/RleftSmathbbQmathbfp.svg
[\sqrt{\mathbb{V}(\mathbb{Q})} \propto \delta\mathbb{Q}(\mathbb{Q})]: svg/sqrtmathbbVmathbbQpr.svg
[V_{ij}(\mathbb{Q}) \equiv \frac{\int d\mathbb{X} X_i X_j R(\mathbb{X};\mathbb{Q})}{\int d\mathbb{X} R(\mathbb{X};\mathbb{Q})} - \frac{\int d\mathbb{X} X_i R(\mathbb{X};\mathbb{Q})}{\int d\mathbb{X} R(\mathbb{X};\mathbb{Q})}\frac{\int d\mathbb{X} X_j R(\mathbb{X};\mathbb{Q})}{\int d\mathbb{X} R(\mathbb{X};\mathbb{Q})}]: svg/VijmathbbQequivfraci.svg
[\sqrt{\mathbb{V}_{ii}(\mathbb{Q})} \propto \delta\mathbb{Q}_i(\mathbb{Q})]: svg/sqrtmathbbViimathbbQ.svg
[4\times4]: svg/4times4.svg
