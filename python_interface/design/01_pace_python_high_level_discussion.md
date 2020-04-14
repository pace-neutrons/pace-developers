# Matlab and Python: A prototype design for PACE
**2020-03-23**


# Scope

This document summarises, at a high level, methods for running interdependent Matlab and Python code alongside each other, with and without a Matlab license.
Implementation details are presented in a [separate document](02_pace_python_implementation_discussion.md).


# Motivation

PACE will be a suite of several interconnected programs for inelastic neutron scattering data analysis, which are written both in Matlab and in Python.
One major goal of the project is to have both a Matlab and a Python user interface (of which the Python interface *would not require a Matlab license* to use).
Thus, in order to present the user with a seamless experience,

1. All component programs should be accessible from Python or Matlab regardless of which language they are written in.
2. Component programs need to be able to call and/or pass data to each other, regardless of which language they or their dependencies are written in.

Furthermore, the analysis of inelastic neutron scattering data almost always requires a parameterised model of the measured scattering intensities.
Whilst PACE will provide built-in models, another major project goal is to allow user-defined functions in Python or Matlab (or compiled functions in C/C++/Fortran for speed).
Thus there needs to be a way for the [optimiser](/optimisation/design/Model_Optimisation_Design.md) to call this function regardless of the language of either.

This document describes ways for Python code to call Matlab and vice versa, and also discusses how Matlab code may be packaged for users without a Matlab license.


# Overview

The [first section](#python-interface) discusses a possible implementation of a Python interface to existing Horace/Herbert Matlab code using the *Matlab Compiler* toolbox.
The [second section](#interpreter-calls) covers how code running in a Matlab session within Python may call a Python library on the host ("python-matlab-python") and vice versa ("matlab-python-matlab").
These techniques rely on the client library being loaded into the same memory as the host, and use C `mex` or python module code to call the Matlab or Python functions directly.
An alternative which would use only pure Matlab or Python code (without needing any compilation) is to use a [reverse-communication interface](#reverse-communication-interface).
The implications of these proposed implementations on parallelisation is discussed in the [final section](#parallelisation).
We end with a [summary and discussion points](#summary).


# <a name="python-interface"></a> Python User Interface

As detailed in [this section](02_pace_python_implementation_discussion.md#compiled_matlab), Matlab code may be "compiled" using the **Matlab Compiler** and freely distributed to users without a Matlab license.
In order to run this "compiled" code, the user is required to install the free/gratis **Matlab Compiler Runtime** package, and this **MCR** package must match the version of Matlab used to compile the Horace library.
Thus, it would make sense to target a specific Matlab release for stability until new features make upgrading desirable.

The compiled Matlab library is a platform-independent Component Technology File (`ctf`) which contains compressed and encrypted versions of the `m` and `mex`-files used in the project.
The **MCR** is a platform-dependent installation ([approximately 1GB download](https://uk.mathworks.com/products/compiler/matlab-runtime.html)) which contains the base Matlab distribution and libraries but is set up to be able to run only code from `ctf`s.
Code which uses any toolbox will have that toolbox included in the `ctf`.
Depending on the desired functionality the `ctf` may be deployed as a stand-alone program, C/C++ shared library, Python or Java package with suitable bindings.
Mathworks allows the **MCR** to be packaged with the `ctf` (with suitable bindings) in a single distribution, or just the `ctf` on its own (so users need to manually install the **MCR**).

In principle only `m`/`mex`-files packaged in the `ctf` may be called by the compiled Matlab module, but we may package an `m`-file which uses the `eval` function to call any Matlab function in the base distribution.
The only limitation with this is that new Matlab functions cannot be defined by the user, except anonymous single line functions.
As such any user defined modelling function must be written in Python.

## Array data exchange between Matlab and Python

When built as a Python module, the `ctf` and Matlab interpreter is designed to be loaded into the memory of the Python process like a normal `CPython` module.
This means that the Matlab and Python programs share the same memory, and this is used by the next section to allow the calling of functions in one language by the other.
In principle, this should also mean that data **arrays** need not be copied between Python and Matlab.
However, internally the Matlab library which handles communication between Matlab and Python *does* make a copy of the array each time it converts from Matlab to Python or vice versa.
This is compounded by the default wrappers which can result in as much as *three* data copies in each direction as discussed in [this section](02_pace_python_implementation_discussion.md#type_conversions).
These other extraneous copies may be avoided using custom wrappers, which is implemented in the [prototype Python interface](https://github.com/mducle/hugo).
This wrapper, however, requires that Python-side data (implicitly assumed to be a `numpy` array) is stored in memory using a column-major (Fortran-style) layout.
If the Python data is stored in a row-major format, then an extra data copy is unavoidable (`numpy` supports both column- and row-major layouts but the Matlab-Python library only supports the former).

Another complication is **complex-valued arrays**, which the Matlab-Python library converts into two separate arrays (a real and imaginery part) in Python.
This is despite the fact that since R2018a Matlab internally stores complex arrays as a single interleaved array, where each element has both real and imaginery parts.
This is exactly the format `numpy` uses, but because the Matlab-Python library exports complex arrays to Python as separate parts it means that we must have *two* data copies in each direction.

It is possible to write `mex` files to share data between Matlab and Python without *any* copies, and this is [explored in the details](02_pace_python_implementation_discussion.md#mex_wrapping).
The implementation describe there should be robust to memory errors because they rely on created *shared-copies* of the arrays to be exported in the original language.
(Shared-copies do not involve copying data, but are arrays which share the same memory; the proposals plans to use a shared `mxArray` in Matlab, and `memoryview` in Python).
In both language as long as there is *one* object with a link to a shared-memory location, that memory will not be freed.
The proposed design thus use the shared-copies to ensure that the memory stays valid until the daughter array in the exported language is deleted.
This design has not been implemented yet, and may prove buggy in practice. 
In any case it will cause some overheads due to the need to create wrapper objects to ensure the shared-copies exist, so should perhaps only be applied to large arrays.
So, perhaps a better design strategy is to try as much as possible to avoid passing large arrays between Matlab and Python. 

## Scalar data exchange between Matlab and Python

The previous section concerns data arrays, whereas **scalar** data types passed between Matlab and Python are automatically converted as [detailed here](https://www.mathworks.com/help/matlab/matlab_external/handle-data-returned-from-matlab-to-python.html).
The exception to this is a `matlab.object` (the generic Python side class of any Matlab class) which may only be generated by a Matlab function and is passed directly to Python.
This object is nearly opaque to Python (it contains only a reference to the `mxArray` container and very few methods), however it may be passed back to another Matlab function without conversion.
This `matlab.object` rule applies only to new-style Matlab classes, defined by the `classdef` keyword, however.
Old-style Matlab classes (defined only by the `@`-directories) are treated as `struct`s and automatically converted to a Python `dict`, losing all connections with their methods.
The [prototype implementation](02_pace_python_implementation_discussion.md#user_interface) includes a thin wrapper which keeps old-style classes as `matlab.object`.
However, it is envisaged that all old-style classes in Horace/Herbert will be refactored to new-style classes by the PACE project.

Data types which are not basic scalar types or arrays of such, including Python functions and objects are not allowed to be passed to Matlab, and will raise an error if tried.
This has implications for calling Python functions from Matlab using the Python interface, as discussed in the next section.

Since array data within a `matlab.object` is *not* copied when exported from Matlab to Python, we may use it to wrap large data arrays, to avoid the data copying discussed in the previous section.
However, the reverse direction is more problematic since the Matlab-Python library does not allow arbitrary Python objects to be exported to Matlab.
Thus large array exports from Python to Matlab will need either to be copied using the default export mechanism, or we need to implement the shared-data [export mechanism described in the details](02_pace_python_implementation_discussion.md#mex_wrapping).
This will definitely be needed if large parts of PACE come to be written in Python, and only small parts remain in Matlab and will thus need to communicate much more data with Python.
As a bonus feature, the share-copies mechanism will allow users fast access to the `pix` array of an `sqw` object for example.

## Example syntax

Finally, whilst the [prototype implementation](02_pace_python_implementation_discussion.md#user_interface) has a basic Python wrapper for inferring function calls and automatic type conversions which allows for syntax such as:

```python
from pyHorace import Matlab
m = Matlab()
proj = m.projaxes([ -0.5, 1, 0], [0, 0, 1], 'type', 'rrr')
w1 = m.cut_sqw('ei30_10K.sqw', proj, [0.1, 0.02, 0.5], [1.5, 2.5], [0.4, 0.5], [3, 0.5, 20])
w2 = w1.cut([0.1, 0.5], [3, 0.5, 20])   # or m.cut(w1, [0.1, 0.5], [3, 0.5, 20])
w2.plot()                               # or m.plot(w2)
```

Note that it is not possible to import all Matlab functions or classes into the Python namespace directly so syntax which omits the `m.` will only be possible by explicitly specifying individual Python wrappers to equivalent Matlab functions.


# <a name="interpreter-calls"></a> Calling user defined functions

Depending on the outcome of the design review for the optimiser, described [here](/optimisation/design/Model_Optimisation_Design.md), the optimiser may be written in Matlab or in Python (or perhaps C++).

If the optimiser is written in Matlab (as is currently the case), then for the Python interface it needs to be able to call a Python user defined model function (because users cannot define a Matlab function using a compiled Matlab library).
Since the Matlab compiled library is loaded into the same memory as the Python process, it is possible to write a `mex` file which uses the Python C API to call a Python function defined in the host workspace.
However, the built-in Matlab-Python interface does not allow Python functions (or other non-"plain-old-data" Python objects) to be passed to Matlab.
We can thus either pass the raw memory location of the Python function (a `void*` pointer) as an integer from Python to Matlab and thence to the `mex` file, or use some other method to cache the Python function on the Python side.
The first method is quite dangerous because if the pointer is invalid (the memory address it points to is out of range or does not contain a Python function) a `segmentation fault` or `access violation` will occur which will crash Python/Matlab.
An implementation of the second method might use a Python module (say `FunctionWrapper`) which is loaded at the same time as the Matlab interpreter and defines a list of valid Python function objects.
To perform a fit with their own model, the user must call a Python wrapper around the Matlab optimiser rather than the optimiser directly.
The wrapper first adds the user defined model function to the (module-global) `FunctionWrapper` list of valid functions.
This list is not meant to be user accessible so the functions should always remain in memory and should not be accidentally garbage collected by the Python interpreter.
The wrapper then calls the Matlab optimiser and passes the index of the user defined function in the valid-functions list (rather than a pointer) and a flag to indicate this is a Python function.
The Matlab optimiser then calls a `mex` file with appropriate Python C API calls which checks the `FunctionWrapper` list, obtains the Python function from its index and calls it.
A [reference implementation](02_pace_python_implementation_discussion.md#pymatpy) may be found in the [Hugo repository](https://github.com/mducle/hugo).

On the other hand, if the optimiser is written in Python, then it must be able to call a user defined *Matlab* model function, for the Matlab user interface.
Matlab can start a Python interpreter in-memory in a similar way to how the compiled Matlab library is loaded into a Python process, such that the Python interpreter in Matlab shares the same memory as the host Matlab process.
Furthermore the `mex` C API allows execution of arbitrary command strings in the Matlab workspace in a similar way to the `eval` function.
There is also an equivalent to the `feval` function which takes a command name string and input and output arguments as `mxArray`s.
(Note that the C++ API also has `eval` and `feval` methods but accesses it through an `engine` object, which is not defined if the C++ source is compiled as a Python module and not a `mex` function, although there are ways around this).
The `eval` / `feval` methods do not accept function handles but the command name string for these may be obtained using the built-in `functions` method of function handles.
Details are discussed [here](02_pace_python_implementation_discussion.md#matpymat) but there is no prototype implementation for this use-case yet.


# <a name="reverse-communication-interface"></a> Using a Reverse Communications Interface

A reverse communications interface is a kind of synchronous inter-process communications method, which relies only on the passing of data between programs.
It is most famously used in the iterative eigenvalue solvers of the `ARPACK` library.
In that case the user does not pass the matrix to be solved directly to the solver.
Instead the user program first calls the solver to initialise the problem, and the solver returns an initial set of test eigenvectors back to the user program.
At each successive iteration the user program calls the solver with the result of the matrix product of the matrix to be solved and the test eigenvectors, and gets back another set of test eigenvectors.
In addition to the test eigenvectors, the solver will also return a flag indicating if convergence has been reached or an error state.

For our case, for concreteness, let us supposed that the optimiser is written in Matlab and is called `multifit`, and the user is using the Python interface and has written a Python model function.
We need to write a Python class `pymultifit` to wrap this function and facilitate communications with a Matlab function.
We will also need to refactor `multifit` (to `multifit_rci` say) to allow for sequential per-iteration calls.
Now, instead of calling the Matlab `multifit` directly, the user sets up `pymultifit` and calls its `fit` method.
This then calls `multifit_rci` to set up the optimiser and waits for it to return with the first set of parameters and coordinates (`hklE`) to evaluate the user function.
`pymultifit.fit` then calls the user defined function (in Python) to obtain a new set of calculated values and passes this back to `multifit_rci` to calculate the cost function and/or Jacobian.
`multifit_rci` then determines the next set of parameters to evaluate and returns this to `pymultifit.fit`.

A reference implementation of this method has not been completed as it requires a fair amount of changes to `multifit`, which will be superseded by a new optimisation module in any case.


# <a name="parallelisation"></a> Implications for parallelisation

The implementations described above rely on the Matlab and Python interpreters being loaded into the same process and thus sharing memory.
Whilst they could spawn threads, this is an inherently serial architecture.
Nonetheless it is appropriate for the current use case because we envisage that users will want to interact directly with the Matlab/Python interpreter rather than use a client-server architecture.
Thus the interpreter need not be parallelised, only certain functions called by it (perhaps including user modelling functions), which none of these methods precludes.


# <a name="summary"></a> Summary

1. It is possible to distribute a Python package of Horace/Herbert to users which wraps the Matlab code and does not require them to have a Matlab license.
2. In the most common use case, both Matlab and Python interpreters are loaded into the same process so (in principle) can read each others data directly without copying.
3. It is possible for Matlab client code to call host Python code and vice versa.
4. New style classes (defined by the `classdef` keyword) are needed for the Python interface to Matlab.

One implication of the possibility of an embedded Python within Matlab to call functions in the host Matlab workspace (and vice versa) is that it is *possible* to reimplement Horace/Herbert in Python piecemeal.
However, because of the data copying required by the internal Matlab-Python library, this piecemeal implementation would not be performant.
There is a way to avoid these data copies but this has not been prototyped or implemented yet.
In any case, as this piecemeal implementation progresses, it would likely introduce a lot of complications into the build system and testing framework, which might mean that the code becomes less stable.
It also means that there is less incentive to migrate the Horace/Herbert code base away from Matlab and keeps Matlab as a dependency for us (as developers).
Finally, it is dependent on being able to access the Matlab Compiler Toolbox which is "free" for us for the moment, but may not be in future (whenever the licenses are renegotiated).

The methods described to facilitate inter-operability between Matlab and Python are inherently serial (not least because of Python's global interpreter lock).
However, functions called by these methods need not be serial.
That is, user modelling functions, the optimiser or the resolution convolution machinery can separately be parallel (as long as they are written entirely in one language and need not call functionalities from another in their core).
