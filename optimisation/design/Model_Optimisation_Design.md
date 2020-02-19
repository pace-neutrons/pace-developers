# PACE Model Optimisation
**2020-02-18**

<!---
LaTeX equations used repeatedly can be defined as references, with format
	[latex_equation]: %-encoded link to image generator
then, if image generation fails for some reason, the alt-text for each equation
will still contain the raw LaTeX equation which is often intelligible

Constructing the %-encoded link can be done at, e.g., the codecogs website
	https://www.codecogs.com/eqnedit.php?latex=latex_equation
--->
[\mathbf{p}]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bp%7D
[\mathbf{p}_0]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bp%7D_0
[\mathbf{x}]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bx%7D
[\mathbf{Q}]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7BQ%7D
[E]: https://latex.codecogs.com/svg.latex?E
[\omega]: https://latex.codecogs.com/svg.latex?%5Comega
[\mathbb{Q}]: https://latex.codecogs.com/svg.latex?%5Cmathbb%7BQ%7D
[\mathbb{Q}_i]: https://latex.codecogs.com/svg.latex?%5Cmathbb%7BQ%7D_i
[S_i(\mathbb{Q}_i)]: https://latex.codecogs.com/svg.latex?S_i%28%5Cmathbb%7BQ%7D_i%29
[S(\mathbb{Q})]: https://latex.codecogs.com/svg.latex?S%28%5Cmathbb%7BQ%7D%29
[S(\mathbb{Q};\mathbf{p})]: https://latex.codecogs.com/svg.latex?S%28%5Cmathbb%7BQ%7D%3B%5Cmathbf%7Bp%7D%29
[r(\mathbf{p})]: https://latex.codecogs.com/svg.latex?r%28%5Cmathbf%7Bp%7D%29
[f(\mathbf{p})]: https://latex.codecogs.com/svg.latex?f%28%5Cmathbf%7Bp%7D%29
[S(\mathbf{Q},E) \propto \frac{\partial^2\sigma}{\partial \mathbf{Q} \partial E}]: https://latex.codecogs.com/svg.latex?S%28%5Cmathbf%7BQ%7D%2C%20E%29%20%5Cpropto%20%5Cfrac%7B%5Cpartial%5E2%20%5Csigma%7D%7B%5Cpartial%20%5Cmathbf%7BQ%7D%20%5Cpartial%20E%7D
[\mathbb{Q} \equiv (\mathb{Q},E)]:https://latex.codecogs.com/svg.latex?%5Cmathbb%7BQ%7D%5Cequiv%28%5Cmathbf%7BQ%7D%2CE%29
[r(\mathbf{p}) = \sum_i \left|\frac{S_i(\mathbb{Q}_i) - S(\mathbb{Q}_i;\mathbf{p})}{w_i}\right|^2]: https://latex.codecogs.com/svg.latex?r%28%5Cmathbf%7Bp%7D%29%20%3D%20%5Csum_i%20%5Cleft%7C%20%5Cfrac%7BS_i%28%5Cmathbb%7BQ%7D_i%29%20-%20S%28%5Cmathbb%7BQ%7D_i%3B%20%5Cmathbf%7Bp%7D%29%7D%7Bw_i%7D%20%5Cright%7C%5E2
[\mathbf{J}(\mathbf{p}) = \frac{\partial f(\mathbf{p})}{\partial p_1} \ldots \frac{\partial f(\mathbf{p})}{\partial p_n}]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7BJ%7D%28%5Cmathbf%7Bp%7D%29%20%3D%20%5Cleft%5B%20%5Cfrac%7B%5Cpartial%20f%28%5Cmathbf%7Bp%7D%29%7D%7B%5Cpartial%20p_1%7D%5C%2C%5Cldots%5C%2C%5Cfrac%7B%5Cpartial%20f%28%5Cmathbf%7Bp%7D%29%7D%7B%5Cpartial%20p_n%7D%20%5Cright%5D
[\mathbf{J}(\mathbf{p})]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7BJ%7D%28%5Cmathbf%7Bp%7D%29
[f_i(\mathbf{p})]: https://latex.codecogs.com/svg.latex?f_i%28%5Cmathbf%7Bp%7D%29
[\mathbf{J}_i(\mathbf{p})]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7BJ%7D_i%28%5Cmathbf%7Bp%7D%29
[m]: https://latex.codecogs.com/svg.latex?m
[m,n,o,\ldots,p]: https://latex.codecogs.com/svg.latex?%5C%5Bm%2Cn%2Co%2C%5Cldots%2Cp%5C%5D
[N]: https://latex.codecogs.com/svg.latex?N
[p_3 = 1 - p_2]: https://latex.codecogs.com/svg.latex?p_3%20%3D%201%20-%20p_2

# Overview

Inelastic neutron scattering counts neutron absorption events as a function of
momentum, ![\mathbf{Q}], and energy, ![E], transferred from the neutron to the sample.
The *rate* at which events are detected is proportional to the so-called doubly-differential scattering cross section

![S(\mathbf{Q},E) \propto \frac{\partial^2\sigma}{\partial \mathbf{Q} \partial E}]

which is directly comparable to theoretical models for excitation processes in a condensed matter system.
In the interest of simplified notation we can define a momentum-energy four vector ![\mathbb{Q} \equiv (\mathb{Q},E)].

The Proper Analysis of Coherent Excitations (PACE) will always require comparison of 
discreet measured inelastic neutron scattering data, ![S_i(\mathbb{Q}_i)],
to a continuous model scattering function, ![S(\mathbb{Q})].
Often model scattering functions contain adjustable parameters, ![\mathbf{p}], which should be modified
to improve agreement between the model and measurement.
For a set of model parameters one can define a *weighted residual*

![r(\mathbf{p}) = \sum_i \left|\frac{S_i(\mathbb{Q}_i) - S(\mathbb{Q}_i;\mathbf{p})}{w_i}\right|^2]

where the per-observation weights, ![w_i](https://latex.codecogs.com/svg.latex?w_i), could be constant or some function of the variance,
and the goal of any **Model Optimisation** scheme is then to find
![\mathbf{p} \in \mathbb{R}^n](https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bp%7D%5Cin%5Cmathbb%7BR%7D%5En )
which minimises ![r(\mathbf{p})] or some other
![f(\mathbf{p}): \mathbb{R}^n \rightarrow \mathbb{R}](https://latex.codecogs.com/svg.latex?f%28%5Cmathbf%7Bp%7D%29%3A%5Cmathbb%7BR%7D%5En%5Crightarrow%5Cmathbb%7BR%7D).
*Alternatively, the goal could be to find the ![\mathbf{p}] which maximises ![f(\mathbf{p})] but this is equivalent to minimising 
![-f(\mathbf{p})](https://latex.codecogs.com/svg.latex?-f%28%5Cmathbf%7Bp%7D%29)
and so is a simple extension.*

# Context
PACE users will provide a function or class method which calculates and returns ![S(\mathbb{Q};\mathbf{p})]
at an array of ![\mathbb{Q}] values and constant model parameter values ![\mathbf{p}].
These user-provided scattering functions may account for instrumental effects, e.g., slowly-varying backgrounds
or resolution broadening, but likely will not.
Advanced users may wish to implement their own ![f(\mathbf{p})] but the majority of users will be happy
to use a PACE-provided ![r(\mathbf{p})].

Different **Model Optimisation** schemes may require additional information.
Local-minima optimisers need an initial guess for the model parameters, ![\mathbf{p}_0].
Global-minima optimisers may need lower- and upper-bounds in 
![\mathbb{R}^n](https://latex.codecogs.com/svg.latex?%5Cmathbb%7BR%7D%5En) for ![\mathbf{p}].
Most optimisers require the Jacobian of the function to be minimised, e.g.,

![\mathbf{J}(\mathbf{p}) = \frac{\partial f(\mathbf{p})}{\partial p_1} \ldots \frac{\partial f(\mathbf{p})}{\partial p_n}]

which depends on the user-provided scattering function, the measured data, and the choice of ![f(\mathbf{p})].
Some optimisation algorithms require ![f_i(\mathbf{p})] and ![\mathbf{J}_i(\mathbf{p})] for each ![\mathbb{Q}_i], and perform the sum over
![i](https://latex.codecogs.com/svg.latex?i) internally.

Since PACE is responsible for ![S_i(\mathbb{Q}_i)] and ![r(\mathbf{p})] it must also calculate ![\mathbf{J}(\mathbf{p})] for arbitrary (user-provided) ![S(\mathbb{Q};\mathbf{p})].
Doing so in a way which simplifies calculating the Jacobian for advanced users who provide their own ![f(\mathbf{p})]
is desirable.

By providing the necessary glue to connect user-provided ![S(\mathbb{Q};\mathbf{p})] and one-or-more optimisers PACE will enable
the routine extraction of physically relevant parameters from measured inelastic neutron scattering data.

## Deliverables
- New classes `OptModel`, `OptFunctionsArray`, and `OptFunction`, detailed below
- Callback function to calculate ![r(\mathbf{p})] for user-provided ![S(\mathbb{Q};\mathbf{p})].
- Callback function to calculate ![\mathbf{J}(\mathbf{p})] for arbitrary ![f(\mathbf{p})]; including ![r(\mathbf{p})]
- Framework for interfacing to one or more optimisation libraries implementing:
  + the Levenberg-Marquardt nonlinear least squares algorithm
  + a global optimiser, e.g., one or more of the algorithms in [NLopt](https://nlopt.readthedocs.io/en/latest/NLopt_Algorithms/)
  + a derivative-free optimiser, e.g., [DFO-LS](https://github.com/numericalalgorithmsgroup/dfols)
  + *Bayesian Inferrence* 
    - Approximating a ![f(\mathbf{p})] surface using:
      + A tree of Parzen estimators (TPE) [HyperOpt](https://github.com/hyperopt/hyperopt)
      + Gaussian processes [GPFlow](https://github.com/GPflow/GPflow)
    - Generalised statistical modelling using a Markov-Chain Monte Carlo algorithm to calculate the integrals yielding the marginalized distributions [PyMC3](https://docs.pymc.io/)
      

## Excluded
There may be ways to automatically estimate ![\mathbf{p}_0] for arbitrary ![S(\mathbb{Q};\mathbf{p})]
-- this is left for a future machine-learning algorithm.
In the mean time users will need to provide an appropriate ![\mathbf{p}_0] along with their model.

Similarly it may be possible to automatically provide reasonable parameter bounds by searching for
discontinuities in ![S(\mathbb{Q};\mathbf{p})]. This too is beyond the scope of this project.
Users will need to provide parameter bounds in the form of linear or non-linear equalities or inequalities,
depending on which optimisation back-end is to be used.   



# Existing Solution
Users of `Horace` are able to optimise models with signatures of the form

```matlab
function S = user_sqw_function(h, k, l, w, p)
  % h, k, l, and w will all have the same shape
  % p is a vector of the optimization parameters
  ...
  return S; % a size(h) double array
end
```
or

```matlab
function S = user_sqw_function(h, k, l, w, p, c)
  % h, k, l, w, and p are as above,
  % c is a cell array containing extra non-optimised model information
  ...
  return S; % a size(h) double array
end
``` 
where the actual model implementation, contained in the omitted section, is allowed to be any valid MATLAB code.

The function is provided to `Horace` methods, e.g., `sqw_eval`, by means of either a function handle or
a function string. Internally the builtin MATLAB function `feval` is used to pass arguments to the user-provided function.
Optimisation is accomplished through a `multifit_sqw` object.
The `multifit_sqw` object is a light wrapper around a `multifit` object, which contains a specialised implementation
of the Levenberg-Marquardt algorithm and interally constructs ![r(\mathbf{p})] and ![\mathbf{J}(\mathbf{p})] as needed.

`multifit` has the ability to fix parameters and to bind select (overparametrised) model parameters with linear equalities,
e.g.,
![p_2 = 2p_1 - 1](https://latex.codecogs.com/svg.latex?p_2%20%3D%202p_1%20-1),
both of which reduce the effective parameter space dimensionality and should be maintained.

Another nice feature of the current implementation that should be retained is the ability to simultaneously
fit multiple datasets with some functions/parameters associated with individual datasets and others associated with all datasets.

A typical use of `multifit_sqw` to optimise the parameters of a model to one or more `sqw` datasets might be
executed by the following MATLAB excerpt.

```matlab
obj = multifit_sqw(sqw_obj1 {, sqw_obj2, ...}); % object containing 1+ sqw object(s)
obj = obj.set_fun(@user_sqw_function, p_i); % define a foreground function
obj = obj.set_bfun(@user_bkg_function, p_j); % define a background function
obj = obj.set_free(...); % optionally fix foreground parameters
obj = obj.set_bfree(...); % optionally fix background parameters
obj = obj.set_bind(...); % optionally bind foreground parameters
obj = obj.set_bbind(...); % optionally bind background parameters
[sim_obj(s), p_fit] = obj.fit();  
```
As a MATLAB value class `multifit` objects have immutable properties, so any method acting on a `multifit` object produces a new object;
the syntax `obj = obj.method()` is a workaround to this issue.
Note that the foreground and background functions have been provided independent initial parameter vectors
these are combined into
![\mathbf{p}_\text{fit}](https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bp%7D_%5Ctext%7Bfit%7D) as a cell array of vectors (?).
 
# Proposed Solution

A simplified overall context diagram for PACE shows that it will be used by researchers after their inelastic neutron scattering data has been reduced into some number of NXSPE files.

![PACE context diagram][Context]

A container diagram shows that PACE will provide both a MATLAB and Python interface for the researcher, both of which will be able to interact directly with Horace and an improved version of multifit.

![PACE container diagram][Container]

Looking at the components of Horace and the multifit replacement, here dubbed multiFit+, we see that Horace provides functionality to create and interact with `sqw` objects.
multiFit+ will provide an interface to external modelling codes and external optimisation codes, will interact strongly with tobyfit, and will consist primarily of the new optimisation functionality detailed in this document.


![PACE components diagram][Components]

[Context]: images/C4_PACE_Opt_1_Context.png
[Container]: images/C4_PACE_Opt_2_Containers.png
[Components]: images/C4_PACE_Opt_3_Components.png

## Optimisation Function Object
The minimum information required for a model to simulate a `sqw` object are the ![\mathbb{Q}_i] contained in the object
and one or more model parameters.
It may also be desirable to give a function access to experimental details, e.g.,
a scaling function may require the sample temperature to include the Bose thermal-population factor,
or a background function may account for a sample-angle or scattering-angle dependent spurious signal.

At a minimum `OptFunction` must support user defined functions which require only ![\mathbb{Q}_i],
and therefore take four equal-shape arrays of floating point numbers,
as well as user defined functions which require the `sqw` object.
For added flexibility in potential other uses for `OptFunction` it should support functions which take
any number of numeric arrays and functions which take any number of array-like objects.
The supported function signatures are therefore:

1. `numeric_arrays(a, ..., p)` of which `S_of_Q_w(h,k,l,w, p)` is a specific case
2. `arrays_objects(a, ..., p)` of which `S_of_Q_w(sqw_obj, p)` is a specific case

Depending on the language in which `OptFunction` is defined this can be implemented in a variety of ways.

It will be desirable to support convolution of the instrumental resolution with a user provided function using, e.g., `TobyFit`.
However such a convolution should not be performed indiscriminately for all functions.

The `OptFunction` object must contain properties which are

- the user defined function
	+ as a string containing its name, a function handle, or a function pointer,
	depending on implementation language
- an indication of whether instrumental resolution convolution should be performed
	+ this might be as simple as a boolean flag or could be a more complicated structure with details for the convolution, *this will be determined later and should not be fixed at this point*
- the initial (or last used) parameter vector for the model
- a vector describing which parameters are allowed to be changed or, conversely, which parameters must not be changed
	+ this could be a logical vector the same size as the parameter vector
	+ a variable length vector with parameter indices
	+ or something else depending on the implementation language
- a structure of some sort describing optional bindings between parameters
	+ for example, a number-of-parameters length vector of indices into an array of parameter binding functions
	+ or some other implementation again depending heavily on language.
- if memory allows it *might* be desirable to store the last evaluation result of the user defined function
  	+ this would be a zero-length numeric vector if no prior evaluation was performed. 

Depending on details of the implementation language additional properties may be required

- the type of input the user defined function expects
- the number of inputs the user defined function expects
	
In C++ both of these can be defined through appropriate usage of templates and the [Function objects library](https://en.cppreference.com/w/cpp/utility/functional).
In Python the `inspect` module can be used to determine this information.
In MATLAB it *may* be possible to obtain this information from a function definition through use of [partially-documented meta functions](http://undocumentedmatlab.com/articles/function-definition-meta-info) and, possibly, enforced usage of [Function Argument Validation](https://mathworks.com/help/matlab/matlab_prog/function-argument-validation-1.html) in user functions but with so much uncertainty this should be left as a stretch goal.

The `OptFunction` object must  contain methods to:

- evaluate the function when given appropriate input, e.g., ![(a,\ldots)](https://latex.codecogs.com/svg.latex?%28a%2C%5Cldots%29).
- query all properties
	+ There should be two variants of the parameter vector accessors.
	The first should directly access the stored parameter while the second should
	respect the status of the parameters, only returning or directly-updating those which are
	both free and independent.
- update all properties, with the exception of the user defined function which is *immutable*
	+ The user defined function does not need to be truly immutable since a determined user can
    find a way to redefine the function, instead we should try to enforce the concept that one
    `OptFunction` object corresponds to a specific instance of one function -- since the parameters
    for one function will generally not be applicable to a second function.


As an example of the independent parameter access method, if there are ![N]
parameters but the first parameter is fixed and
the third parameter is bound to the second via 
![p_3 = 1 - p_2](https://latex.codecogs.com/svg.latex?p_3%20%3D%201%20-%20p_2)
then the reduced query method should return 
![{p_2, p_4, \ldots, p_N}](https://latex.codecogs.com/svg.latex?%5C%7Bp_2%2C%20p_4%2C%20%5Cldots%2C%20p_N%5C%7D)
and the reduced update method should take a 
![N-2](https://latex.codecogs.com/svg.latex?N-2)
length vector, 
![\mathbf{d}](https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bd%7D)
and update the parameter vector to be
![\mathbf{p} = {p_1, d_1, 1-d_1, d_2, \ldots, d_{N-2}}](https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bp%7D%20%3D%20%5C%7Bp_1%2C%20d_1%2C%201-d_1%2C%20d_2%2C%20%5Cldots%2C%20d_%7BN-2%7D%5C%7D)

### Calling the function inside `OptFunction`
Each `OptFunction` object knows how many and of what type its containing function requires as input before its parameter vector.
If the `OptFunction` `evaluate` method is called with the matching input then it should be passed along without modification.
If, however, different input is provided `OptFunction.evaluate` should be able to construct the required input.

The use case that should be supported at minimum is that a function requires four numeric vectors as input but `OptFunction.evaluate` was provided with a `sqw` object. In this case `OptFunction.evaluate` should pull the vectors `h,k,l,E` from the `sqw` object for use by the internal function.

Possible behaviour when numeric input is required but a `sqw` object is provided to `evaluate` might be

| required number | pass to function |
|-----------------|------------------|
| 0               | `void`           |
| 1               | `E`              |
| 2               | `norm(Q),E`      |
| 3               | `h,k,l`          |
| 4               | `h,k,l,E`        |

### `OptFunction` parameter binding
For the parameters of a single function we can combine the fixed/free logical information with the bound-ness of a parameter.

If we have ![N] parameters but the first parameter is fixed and
the third parameter is bound to the second via ![p_3 = 1 - p_2],
a vector of `[-1,0,1,0,...,0]` could be used to indicate that the first parameter should not vary (`-1`)
while the third parameter should be bound according to the first entry of a separate cell array of function
handles/strings, in this case, of the form `{@(p)1-p(2)}`.

It may be desirable to translate the non-varying specification into a full binding function,
which we might accomplish via

```matlab
for i=1:numel(status)
	if (status(i) < 0)
		n_bindings = numel(bindings) + 1;
		status(i) = n_bindings;
		bindings{n_bindings} = str2func(sprintf('@(x)x(%d)',i));
	end
end
```

Whether the non-varying specifications are translated or not, we can construct a mapping from the full
parameter vector to a vector containing only the independent parameters simply, e.g., `mapping = find(status==0)`.
Then the get and set methods of an object can respect the status of the parameters:

```matlab
...
	function p = get_parameters(obj)
		p = obj.parameters;
	end
	function p = set_parameters(obj, new_p)
		obj.parameters = new_p;
		p = obj.get_parameters();
	end
	function d = get_independent(obj)
		mapping = find(obj.status == 0);
		p = obj.get_parameters();
		d = p(mapping);
	end
	function d = set_independent(obj, new_d)
		mapping = find(obj.status == 0);
		% get all parameters
		p = obj.get_parameters();
		% update the independent parameters
		p(mapping) = new_d;
		% plus the dependent parameters, obeying their bindings
		for i=1:numel(obj.status)
			if (obj.status(i) > 0)
				p(i) = feval(obj.bindings{obj.status(i)}, p);
			end
		end
		% store the updated full parameter vector
		obj.set_parameters(p);
		% and extract the independent ones from the stored values
		d = obj.get_independent();
	end		
...
```

### `OptFunction` parameter limits
Some optimisers *require* that bounds be set on the applicable ranges of a model's parameters.
In a simple case the upper and lower bounds are specified for each parameter as a single number.
More flexible optimisers instead specify bounds in the form of (possibly nonlinear) inequalities provided as functions of the optimised parameters.
Such bounding functions are flexible enough to cover any conceivable parameter space restrictions and can be provided to 
each `OptFunction` as anonymous functions.

One option would be to combine the bounding functions with the binding functions cell array, and then index into
that with a separate ![N \times 2](https://latex.codecogs.com/svg.latex?N%20%5Ctimes%202) array (or two length-![N] vectors), with `0` reserved to indicate no-bounding.

In a hypothetical case where the first parameter is free and unbounded,
the second parameter is free and bound to be between constant values `lower_value`&le;`p(2)`&le;`upper_value`,
and the third parameter is free and bound to within a band defined by the first parameter,
the bounding functions specified might be of the form:

|parameter|bounds type| lower boundary: `p(i)`&ge;![f(\mathbf{p})] | upper boundary: `p(i)`&le;![f(\mathbf{p})]       |
|--------:|----------|----------------------|----------------------------|
|1        |unbound   | `@(p) -inf;`         | `@(p) inf;`                |
|2        |constant  | `@(p) lower_value;`  | `@(p) upper_value;`        |
|3        |linear    | `@(p) p(1)*slope;`   | `@(p) p(1)*slope + offset` |

### Named parameters
To facilitate setting of parameter bindings and limits it may be useful to refer to parameters by user specified names in addition to indices.
These names would need to be provided to the `OptFunction` object, ideally at creation, and would be used to translate binding or limit functions.

For example a new `OptFunction` (without any bindings) given parameter names `{'A0', 'x0', 'w0', 'A1', 'x1', 'w1'}` could then have its third and sixth parameters bound together by, e.g., `obj.bind('w1','w0')` which would be translated to the new parameter function `obj.parameter_functions{end+1} = '@(z)z(3)'` with `obj.parameter_status(3) = numel(obj.parameter_functions)`.
Or `obj.bind('x1','x0^2/3 + 12')` would become the anonymous function string `'@(y)y(2)^2/3 + 12'`.

### One possible implementation of `OptFunction`

![possible OptFunction diagram][OptFunction_diagram]

[OptFunction_diagram]: images/OptFunction_diagram.png

## Optimisation Functions Array Object
It is worthwhile to allow for a user defined ![S(\mathbb{Q};\mathbf{p})] to be constructed as the sum of a number of user defined functions held in `OptFunction`s.
And when fitting multiple datasets it will be worthwhile to have a list of `OptFunction` objects each of which is associated with one or more of the datasets.
This will allow, e.g., multiple datasets to be fit to related functions where some number of their parameters are bound by user defined relationships.
A new class is necessary to hold multiple `OptFunction` objects and handle their interactions and application to multiple datasets, `OptFunctionsArray` 

The minimum set of properties of an `OptFunctionsArray` object are

- a list of one or more `OptFunction` objects
- function to dataset applicability information
- inter-function parameter binding information
- the reduction operator to use if multiple functions apply to one dataset
	+ typically `+` or `*`, other operations *probably* do not need to be supported

The `OptFunctionsArray` object will require access methods for all properties plus methods to

- add one or more `OptFunction` objects to the list
- get a collection of the parameters of all functions and set the parameters of all functions from a similar collection (a cellarray of vectors?)
- get a vector of the independent parameters of all functions and set the independent parameters of all functions from a same-sized and ordered vector
- evaluate the functions that apply to each of a provided array of datasets

### `OptFunctionsArray` inter-function parameter binding
Binding parameters *between* functions can still be accomplished by the use of binding functions.
The best solution to accomplish this task is unclear, but may consist of

- a ![N \times 3](https://latex.codecogs.com/svg.latex?N%20%5Ctimes%203) `status` array containing function number, parameters number, and binding function number, plus a length-![N] cellarray of the binding functions
- a length-![N] cellarray of 3-vectors each with the function number, parameter number, and binding function number, and the same cellarray of binding functions as before
- a length-![N] cellarray of length-3 cellarrays each consisting of `{function_no, parameter_no, binding_fun_handle}`
- or a length-![N] array of binding objects containing the same information in a more-concrete form

In any case the meta binding functions will need to take a combined form of all (function-type) parameters as input, e.g.,
`foreground_parameters = cellfun(@(x)x.get_parameters(), obj.foreground, 'UniformOutput',false);`
and should return a single value, such that the binding can be resolved by
`foreground_parameters{function_no}(parameter_no) = feval(binding_fun_handle, foreground_parameters);`.

The specification that parameter 3 of function 2 should be equal in magnitude but opposite in sign to parameter 2 of function 1 might
then be accomplished by `{2, 3, @(p)-p{1}(2)}`.


### `OptFunctionsArray` function applicability
When multiple datasets are fit concurrently with a mixture of global and dataset-specific parameters identifying which functions correspond to which datasets is imperative.
One way to accomplish this (in MATLAB-like languages) is for the `OptFunctionsArray` object to hold a per-function-type `applies` cellarray which is the same length as the `OptFunction` vector and should have entries 

| `applies{i}` | meaning |
|--------------|---------|
| `0`  | `OptFunction` `i` applies to all datasets |
| `-1` | duplicate `OptFunction` `i` and apply them independently to each dataset |
| ![m] | `OptFunction` `i` applies *only* to dataset ![m] |
| ![m,n,o,\ldots,p] | `OptFunction` `i` applies to each of ![m,n,o,\ldots,p] |

In C++ or Python this might be better accomplished by holding a vector of vectors, e.g., `std::vector<std::vector<int>>` or `numpy.array([numpy.array([...]),...])`.

The total number of all `applies` entries, e.g., `sum(arrayfun(@(x)numel(obj.applies(x)),1:numel(applies)))` + `numel(datasets)*sum(cellarray(@(x)x==0,applies))`, should be equal to or greater than the number of datasets -- that is, each dataset must have at least one function which applies.

### One possible implementation of `OptFunctionsArray`

![possible OptFunctionsArray diagram][OptFunctionsArray_diagram]

[OptFunctionsArray_diagram]: images/OptFunctionsArray_diagram.png

## Optimisation Model Object
For efficiency of model evaluation it will be worthwhile to allow for a user defined ![S(\mathbb{Q};\mathbf{p})] to be constructed from a set of multiplier, foreground, and background functions all held in `OptFunctionsArrays` objects.
Keeping track of those `OptFunctionsArray` objects and interacting with the optimisation engine requires a new class, `OptModel`.

`OptModel` should take three `OptFunctionsArray` objects

- multiplier functions, ![M(a,\ldots;\mathbf{m}) \equiv \prod_i M_i(a,\ldots;\mathbf{m}_i)]
- foreground functions, ![F(a,\ldots;\mathbf{f}) \equiv \sum_j F_j(a,\ldots;\mathbf{f}_j)]
- background functions, ![B(a,\ldots;\mathbf{b}) \equiv \sum_k B_k(a,\ldots;\mathbf{b}_k)]

[M(a,\ldots;\mathbf{m}) \equiv \prod_i M_i(a,\ldots;\mathbf{m}_i)]: https://latex.codecogs.com/svg.latex?M%28a%2C%5Cldots%3B%5Cmathbf%7Bm%7D%29%20%5Cequiv%20%5Cprod_i%20M_i%28a%2C%5Cldots%3B%5Cmathbf%7Bm%7D_i%29
[F(a,\ldots;\mathbf{f}) \equiv \sum_j F_j(a,\ldots;\mathbf{f}_j)]: https://latex.codecogs.com/svg.latex?F%28a%2C%5Cldots%3B%5Cmathbf%7Bf%7D%29%20%5Cequiv%20%5Csum_j%20F_j%28a%2C%5Cldots%3B%5Cmathbf%7Bf%7D_j%29
[B(a,\ldots;\mathbf{b}) \equiv \sum_k B_k(a,\ldots;\mathbf{b}_k)]: https://latex.codecogs.com/svg.latex?B%28a%2C%5Cldots%3B%5Cmathbf%7Bb%7D%29%20%5Cequiv%20%5Csum_k%20B_k%28a%2C%5Cldots%3B%5Cmathbf%7Bb%7D_k%29

[M_i(a, \ldots; \mathbf{p}_i)]: https://latex.codecogs.com/svg.latex?M_i%28a%2C%20%5Cldots%3B%20%5Cmathbf%7Bp%7D_i%29
[F_j(a, \ldots; \mathbf{p}_j)]: https://latex.codecogs.com/svg.latex?F_j%28a%2C%20%5Cldots%3B%20%5Cmathbf%7Bp%7D_j%29
[B_k(a, \ldots; \mathbf{p}_k)]: https://latex.codecogs.com/svg.latex?B_k%28a%2C%20%5Cldots%3B%20%5Cmathbf%7Bp%7D_k%29
[\mathbf{p}_i]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bp%7D_i
[\mathbf{p}_j]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bp%7D_j
[\mathbf{p}_k]: https://latex.codecogs.com/svg.latex?%5Cmathbf%7Bp%7D_k

such that they collectively describe a real valued function

![\rho(a,\ldots;\mathbf{p}) = M(a,\ldots;\mathbf{m}) \times F(a,\ldots;\mathbf{f}) + B(a,\ldots;\mathbf{b})]

[\rho(a,\ldots;\mathbf{p}) = M(a,\ldots;\mathbf{m}) \times F(a,\ldots;\mathbf{f}) + B(a,\ldots;\mathbf{b})]: https://latex.codecogs.com/svg.latex?%5Crho%28a%2C%5Cldots%3B%5Cmathbf%7Bp%7D%29%20%3D%20M%28a%2C%5Cldots%3B%5Cmathbf%7Bm%7D%29%20%5Ctimes%20F%28a%2C%5Cldots%3B%5Cmathbf%7Bf%7D%29%20&plus;%20B%28a%2C%5Cldots%3B%5Cmathbf%7Bb%7D%29


which is consistent with the shape of the input,
the parameter vector ![\mathbf{p}] is the concatenation of the independent multiplier, foreground, and background parameters, ![\left{\mathbf{m},\mathbf{f},\mathbf{b}\right}],
and the multiplication and addition are
performed element-wise -- unless if all 
![M_i](https://latex.codecogs.com/svg.latex?M_i) or all 
![B_k](https://latex.codecogs.com/svg.latex?B_k) return scalar values then the multiplication or addition,
respectively, can be performed using shape promotion rules.

[\left{\mathbf{m},\mathbf{f},\mathbf{b}\right}]:https://latex.codecogs.com/svg.latex?%5Cleft%5C%7B%5Cmathbf%7Bm%7D%2C%5Cmathbf%7Bf%7D%2C%5Cmathbf%7Bb%7D%5Cright%5C%7D

The distinction between scaling, foreground, and background functions is overkill for simple cases but will enable efficient handling of resolution effects (where only the ![F_j](https://latex.codecogs.com/svg.latex?F_j) are convoluted with the instrumental resolution).

The `OptModel` object must contain the following properties:

- the multiplier, foreground, and background `OptFunctionsArray` objects
- the dataset(s) used for model simulation and/or optimisation
- the function which evaluates the per ![\mathbb{Q}_i] parts of ![f(\mathbf{p})]
  + some optimisers require ![f_i(\mathbf{p})] and ![\mathbf{J}_i(\mathbf{p})] so we must be able to calculate for each ![\mathbb{Q}_i] independently
- which back-end is to be employed in the model optimisation
  + an `enum` or similar, depending on the language

and must have methods which query and update its properties, plus:

- simulate the composite model ![\rho(a, \ldots,\mathbf{p})]
- calculate ![r(\mathbf{p})] or the user defined ![f(\mathbf{p})]
  - *possibly calculate vector ![f_i(\mathbf{p})] to support more back-ends* -- as this requires we store the result for each ![\mathbb{Q}_i] instead of accumulating 	the memory requirements will tend to be large.
  - if an optimiser requires ![f_i(\mathbf{p})] but memory requirements (or communication speed in a distributed system) preclude storing this for all ![\mathbb{Q}_i], it might be possible to use a per-dataset reduced ![f_\eta(\mathbf{p})] where ![\eta \in 1,\ldots,M], with ![M \ge N+1] for length-![N] ![\mathbf{p}] and each ![\eta] corresponding to a defined subset of all ![\mathbb{Q}_i]
- estimate ![\mathbf{J}(\mathbf{p})], when required
  - *possibly calculate the Jacobian in matrix form* which might require too much memory
  - a per-dataset reduced Jacobian might also be useful
- collect the free and independent parameters from all `OptFunctionsArray` objects into a single reduced parameter vector
- distribute a modified reduced parameter vector to all `OptFunctionsArray` objects
- run the chosen optimisation back-end

[\rho(a, \ldots,\mathbf{p})]: https://latex.codecogs.com/svg.latex?%5Crho%28a%2C%20%5Cldots%2C%5Cmathbf%7Bp%7D%29
[f_\eta(\mathbf{p})]: https://latex.codecogs.com/svg.latex?f_%5Ceta%28%5Cmathbf%7Bp%7D%29
[\eta \in 1,\ldots,M]: https://latex.codecogs.com/svg.latex?%5Ceta%20%5Cin%201%2C%5Cldots%2CM
[M \ge N+1]: https://latex.codecogs.com/svg.latex?M%20%5Cge%20N&plus;1
[\eta]: https://latex.codecogs.com/svg.latex?%5Ceta

Storing the optimisation back-end as an `enum` or similar restricts the supported back-ends to a predefined set.
This restriction may be unnecessary and should be lifted if a clear general back-end interfacing scheme becomes evident
during the implementation of `OptModel`.


### One possible implementation of the `OptModel`

![OptModel implementation diagram][OptModel_diagram]

[OptModel_diagram]: images/OptModel_diagram.png 

## Usage
The following is a pseudo-code example of how `OptModel`, `OptFunctionsArray`, and `OptFunction` might be used to fit the data contained in a `sqw` object.

``` matlab
% construct a function which takes only a parameter vector and returns a scalar
% for use as an overall multiplier:
multiplier = OptFunction(@(x) x(1), 'inputs', 0, 'parameters', [1.,]);

hklT = {'type', 'double', 'inputs', 4};
sqwT = {'type', 'sqw', 'inputs', 1};

sw_func = OptFunction(@spinwaves, hklT{:}, 'parameters', p_spinwave);
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

# Milestones
1. Partial `OptFunction` class without fixed parameters or parameter bindings.
2. Partial `OptFunctionsArray` class holding only a single `OptFunction` and lacking inter-function binding and applicability information
3. Partial `OptModel` class without multiplier or background functions, and only the ability to simulate the model
4. Add model optimisation to `OptModel` for a single, unbounded-parameter, back-end (likely, Levenberg-Marquardt)
5. Add fixed parameters and parameter binding to `OptFunction`
6. Add multiple function support to `OptFunctionsArray` with inter-function binding
7. Add foreground and background functions to `OptModel`
8. Add parameter bounds and additional optimisation back-ends to `OptModel`


# Feedback
Identifying a set of optimisation problems covering a range of difficulty that can be used for integration testing
will be necessary to check the correctness and performance of our solution.

It will be possible and necessary to test the features of `OptFunction`, `OptFunctionsArray`, and `OptModel` objects introduced at each milestone.

# Open Questions
## Model functions via the compiled MATLAB interface
`OptFunction.evaluate()` must be able to call the user defined function with the user defined number of inputs and input type.
In a pure MATLAB environment this might be accomplished by

```matlab
function s = evaluate(obj, varargin)
	% possible error checking on the number and type of inputs in varargin here
	s = feval(obj.function, varargin{:}, obj.parameters);
end
```

If model optimisation is to be supported when running compiled MATLAB/Horace from Python this requires a way to call user defined Python functions.

- Can compiled MATLAB call pure Python functions?
	+ How should such functions be provided to MATLAB? As `module.function` strings, memory addresses, etc.?
- Does compiled MATLAB have access to builtin MATLAB functions like `feval` and `str2func`?
	+ Either way it can not run arbitrary m-files! No MATLAB user functions can be called using the Python interface.


## Parameter functions via the compiled MATLAB interface
Providing parameter bounds functions to `OptFunction` and `OptModel` objects that are part of the compiled MATLAB/Horace might prove problematic.

- If MATLAB/Horace can directly call functions defined by the interactive Python interpreter then a user can easily pass Python lambda functions for the bounds functions, e.g., `lambda x: x[1]`.
- If MATLAB/Horace has access to the builtin MATLAB function `str2func` a user could pass a string representation of a MATLAB-style anonymous function, e.g., `'@(x)x(2)'`.
- If MATLAB/Horace has access to MATLAB's Python interface it could use that to construct Python lambda functions from user provided strings, e.g., `'lambda x: x[1]'`

Creating and calling a Python lambda function from within interactive MATLAB is possible:

```matlab
>> py_func = py.eval('lambda x: x[1]', py.dict);
>> py_func([1,2,3,4])
ans =
      2
```
Note that an empty Python dictionary was provided to `py.eval` as the evaluation workspace.
If the evaluated expression made reference to other variables they would need to be defined in the dictionary, e.g.,
`'lambda y: y+a'` would need a dictionary like, `py.dict(pyargs('a', 14.5))` to avoid an error *when the resulting lambda function is called*.
If a user is providing a 'lambda string' from Python they would need to insert any constant values beforehand via, e.g., `format`, rather than
passing both a string and a workspace dictionary.


## Language choice
Momentum would predict that the new PACE Optimisation interface will be written in `MATLAB` with accommodations in place to enable its use as part of the compile MATLAB/Horace interface through Python.
Still, there may be advantages to choosing a different language.
The advantages and disadvantages of each potential language need to be assessed so that an informed choice can be made.

| Language | Advantage | Disadvantage |
|----------|-----------|--------------|
| MATLAB   | **momentum**                                              |                                                            |
|          | simple interface to `sqw` and rest of Horace              | running from Python of indeterminate difficulty            |
| Python   | MATLAB interfaces to Python modules are relatively simple | running from Python might involve weird interpreter issues |
| C++      | compiled &rarr; functionality constrained &rarr; fully testable | increased distribution complexity                    |
|          | Python interface via `pybind11` simple                    | MATLAB interface via `mex` less simple                     |

The interpreter issues alluded to above is an uncertainty regarding what happens if an interactive Python interpreter calls a function in the compiled MATLAB/Horace which in turn calls functions in a Python module?

### Calling Python functions from C++

The software [`Takin`] has been written for the analysis of triple-axis neutron scattering data.
One of the features of [`Takin`] is the ability to simulate and fit user-defined functions convoluted
with a selectable estimate to the instrumental resolution.
[`Takin`] is written in `C++` and can accept model functions written in `Python` and saved to a file.
To call the user functions, [`Takin`] starts an interpreter (through `Boost.Python`),
has the interpreter parse the file, and then looks for a set of functions using predefined names 
(`TakinSqw`,`TakinInit`, and `TakinDisp`)
to later be used to accomplish a set of tasks.
The `Python` implementation is accessible in `Takin`'s repository in the file [`sqw_py.cpp`].

[`Takin`]: https://code.ill.fr/scientific-software/takin
[`sqw_py.cpp`]: https://code.ill.fr/scientific-software/takin/core/blob/master/tools/monteconvo/sqw_py.cpp

If the chosen back-end optimisation engine is written in Python a similar method can be used to 
interact with it through C++.
Importantly, `pybind11` provides a **[Python C++ interface](https://pybind11.readthedocs.io/en/stable/advanced/pycpp/)**!


## Incremental parameter binding specifications
If a `OptModel` is created to fit three datasets to a single three-parameter function (`multiplier = @(x)1`, `background = @(x)0`) which initially is treated independently for all datasets it will start with a `OptFunctionsArray` that has no inter-function bindings, e.g., `foreground.status = []`, and each `OptFunction` will have no internal bindings, e.g., `foreground.functions(:).parameter_status = [0,0,0]`.

If the user then decides that the second parameter of each function should represent a single global parameter they might bind them together via

```
	obj.bind('f2:p2', 'f1:p2');
	obj.bind('f3:p2', 'f2:p2');
```
assuming that the three-parameter `OptFunction` was created with parameter names `{'p1','p2','p3'}` and the `OptFunctionsArray` was given function names `{'f1','f2','f3'}`.

This naively might create anonymous binding functions for the `OptFunctionsArray` such that `obj.parameter_functions = {'@(x)x{1}(2)', '@(x)x{2}(2)'}` with `obj.parameter_status = {[2,2,1], [3,2,2]}`.
Such an approach creates issues when deciding how to update the dependent parameters -- namely `'f2:p2'` must be update *before* `'f3:p2'` for the functions to have the correct full parameter vectors.

A more complex implementation of the pseudomethod `bind` would recognize at the second call that `f2:p2` is already bound and might generate a second anonymous function `'@(y)y{1}(2)'` by, e.g., replacing `'x{2}(2)'` with `'@(x)x{1}(2)'`.
A more complicated still version would recognize that the newly created anonymous function is equivalent to an existing one and would set `obj.parameter_status = {[2,2,1],[3,2,1]}`.

In order for the dependency chain to always be fully resolved, do we need to restrict parameter functions to always be anonymous function strings (as produced by `func2str`) with a constant input parameter name (e.g., always `@(p)...`)?
Or can we still allow full-fledged MATLAB function handles as parameter functions with the instruction to users that they should *never* chain parameter bindings?
