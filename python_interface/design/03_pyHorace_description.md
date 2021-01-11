# A description of the prototype pyHorace implementation
**2020-12-29**


## Table of Contents

[Background](#background)

[Compiled Matlab](#compiled-matlab)

[Gateway functions and proxy classes](#gateway-functions-and-proxy-classes)

[Calling Python from compiled Matlab](#calling-python-from-compiled-matlab)

[Limitations and future work](#limitations-and-future-work)

[Code Examples](#code-examples)


# Background

PACE is a collection of several different programs written in both Matlab and Python (or C/C++)
and meant to be used from both Matlab *and* Python in an *integrated* fashion.

That is, users should be able to call a PACE program written in Python from a PACE program written in Matlab and vice versa,
using a Matlab *or* Python interpreter.
It is relatively straightforward for Matlab users to access the Python components of PACE using 
[Matlab's built-in `py.*`](https://uk.mathworks.com/help/matlab/call-python-libraries.html) interface/namespace.
This document, however, focuses on the case of Python users accessing the Matlab components of PACE.

As detailed in an [architectural decision record](../../0010-use-compiled-matlab-for-python.md)
we chose to use the Matlab Compiler toolbox to "compile" the Matlab parts of PACE.
This allows our users to use PACE as a Python module 
(tentatively called `pyHorace`, but perhaps it should be `pyPace` or some such) 
without needing a Matlab license.
Instead they need to download and install a Matlab Components Runtime (MCR), a free but restricted distribution of Matlab,
which can be used to run the "compiled" Matlab code only (and not normal m-files).

This method, detailed in [two](01_pace_python_high_level_discussion.md) [previous](02_pace_python_implementation_discussion.md) design documents,
is subjected to some restrictions imposed by the way the MCR and the `py.*` Python-bridge is implemented by Mathworks.
Firstly, the `py.*` implementation _always_ spawns its own dependent Python interpreter.
When called within a normal Matlab interpreter this is fine.
However, when the Matlab code has been compiled and is being run within a _Python_ interpreter,
this second (Matlab-launched) Python interpreter causes the parent Python interpreter to crash.
Thus, `pyHorace` cannot use any Matlab code which refers to `py.*`.

Instead, an alternative method for Matlab code to call Python, via a `mex` file using the CPython API, has been implemented.
Together with a new framework which wraps Python code in a Matlab object intended for use by Euphonic and Brille,
this allows the use of both Matlab and Python PACE interfaces with the minimum of changes to existing Matlab or Python codes.

This documents describes the separate parts of the [prototype](https://github.com/mducle/hugo)
minimum viable implementation of the PACE Python interface,
and also the prototype Python class wrapper intended to be used by the PACE Matlab interface.

We first detail how Matlab classes are wrapped in a Python proxy class which exposes their properties and methods to Python.
We then move to how communications between PACE programs written in different languages is facilitated.
Finally we describe remaining issues with the approach taken and how the prototype may be improved for production.


# Compiled Matlab

As noted in [ADR #10](../../documentation/adr/0010-use-compiled-matlab-for-python.md) the decision was taken
to use "compiled" Matlab code for the Python interface to Horace/Herbert rather than to rewrite them in Python/C++.
This imposes certain constraints on an "pyHorace" implementation:

1. Only user written "gateway" m-file *functions* may be called directly from Python 
(or executed on the commandline) when used from compiled Matlab code.
2. Matlab is run as a loaded library within the Python process ("in-process" execution).
3. The Matlab help system is not available to compiled Matlab code.
4. The Matlab MCR requires the use of its own standard libraries which implies restrictions on which compilers/Python versions can be used.

Point 1 means that Matlab classes and standard Matlab functions cannot be *directly* created or called from Python 
(a specific gateway function which constructs the class must be used instead).
However, any Matlab code (and indeed the entire standard Matlab built-in library of functions and classes) may be in "included" in the compiled library.
The restrictions is that this "included" code may only be accessed by the user-written m-file *function* (not class)
and not by the user calling those functions/classes from Python.
Given this major limitation, the approach taken by the "Hugo" prototype is to use a gateway function,
`call_method` which takes the *name* of a Matlab function, class or class method and a set of arguments and uses
`feval` to call those "included" functions/class/methods.
This is described in more detail in the [next section](#gateway-functions-and-proxy-classes).

Point 2 means that the native Matlab way of calling Python (using the `py.*` namespace) cannot be used
but also means that a `mex` file can be used for this purpose.
This is described in detail in the [section on Python user functions](#calling-python-from-compiled-matlab).

Point 3 means that if we would like users to be able to use `help(sqw)` or similar
we would need to generate the help text and wrappers for each function / class we export (not currently implemented).
This and point 4 and other limitations are discussed in the [limitations section](#limitations-and-future-work)


# Gateway functions and proxy classes

["pyHorace"](https://github.com/mducle/hugo) is based on a framework (["pySpinW"](https://github.com/spinw/pyspinw)) written for SpinW by S. Ward.
The core of this is a Matlab "gateway" function, [`call_method.m`](https://github.com/mducle/hugo/blob/master/src/call_method.m#L101)
which takes the name of a Matlab function and its arguments and uses `feval` to evaluate it.
When compiled using the Matlab Compiler SDK as a Python module,
it maybe accessed in Python using `<module_name>.call_method('function_name', object, [<arg_list>])`.
To make it easier to use, this core gateway function and the Python module (called `horace` and containing the compiled Matlab archive)
is wrapped in a Python class, [`pyHorace.Matlab`](https://github.com/mducle/hugo/blob/master/pyHorace/Matlab.py#L60),
whose `__getattr__()` special method is overloaded to call `call_method`.

This allows a syntax like:

```
from pyHorace import Matlab
Matlab.cut_sqw('sqw_file', [], [], [], [-1,1])
```

Where the `Matlab` class translates this to `horace.call_method('cut_sqw', [], ['sqw_file', [], [], [], [-1,1])` internally in `__getattr__()`.
However, since this method requires overloading the `__getattr__` method of a class, users *always have* to use the "dot" method-access notation.
I.e., `from pyHorace.Matlab import *; cut_sqw('sqw_file', [], [], [], [-1,1])` will not work
because `pyHorace.Matlab` is not a Python module but a class.
In addition `help(pyHorace.Matlab.cut_sqw)` will also not work
because this actually refers to a (dynamically constructed) Python wrapper function.
Thus if we want the above two functionalities (accessing Matlab "included" functions/classes and help)
we will need to write explicit Python wrappers for *every* Matlab function (including class methods) we want to expose this way.
Alternatively if we don't need to provide help/documentation,
we can wrap only those functions whose syntax we want to extend to make more "Pythonic".

The other major feature of `pyHorace` is a Python [`MatlabProxyObject`](https://github.com/mducle/hugo/blob/master/pyHorace/MatlabProxyObject.py) class
which wraps a Matlab class so that it appears transparent to Python users.
That is, Python users can call the methods and access the properties of any Matlab class in Python using the "dot" notation as if they are in Matlab.
This works by overloading the special Python methods `__getattr__` and `__setattr__`
to call the equivalent Matlab special functions `subsref` and `subassgn`
to access the methods/properties of a class.
In addition, the Python `__repr__`, `__str__`, `__dir__` and `__doc__` methods are also overloaded
to provide a description of the object, its methods and help text (except that the Matlab help system is not accessible in a compiled application).
This wrapper is needed because any new-style (defined by `classdef`) Matlab object returned by `call_method` and its wrappers
is opaque to Python and cannot be handled by purely Python functions.

Old-style Matlab objects are treated as plain `struct`s and are automatically converted to Python `dict`s,
losing any connection with the methods defined in their `@` folders.
To overcome this, `pyHorace` includes a [`thinwrapper`](https://github.com/mducle/hugo/blob/master/src/thinwrapper.m) class which wraps an old style class.
Whenever an old-style class (or [struct with an old style member](https://github.com/mducle/hugo/blob/master/src/has_thin_members.m))
is returned by a Matlab function to Python, [`call_method`](https://github.com/mducle/hugo/blob/master/src/call_method.m#L115)
instead [wraps](https://github.com/mducle/hugo/blob/master/src/wrap_obj.m) it by storing the actual old-style object in the Matlab base namespace
and returning to Python a `thinwrapper` (new-style) object.
The only property of this object is the string name of the actual (old-style) object in the base namespace.
This is used by [Python side wrappers](https://github.com/mducle/hugo/blob/master/pyHorace/MatlabProxyObject.py#L79)
to allow users to transparently access the (old-style) Matlab objects as if they were Python objects.

To facilitate all this wrapping, and to make the user syntax more natural, there is an automatic data conversion class,
[`DataTypes`](https://github.com/mducle/hugo/blob/master/pyHorace/DataTypes.py),
which converts data from Python to Matlab (`encode`) and vice versa (`decode`).
Two particular use cases of this automatic conversion are to convert a Python list of numbers 
[directly](https://github.com/mducle/hugo/blob/master/pyHorace/DataTypes.py#L42) into a Matlab numerical array
(Matlab would otherwise convert any Python list into a *cell* array which would give an error if the Matlab function was not expecting this);
and to [wrap `numpy` arrays](https://github.com/mducle/hugo/blob/master/pyHorace/TypeWrappers.py)
such that no data copy is involved in the Python-to-Matlab conversion. 

The `DataTypes` class also handles transparent conversion of the `MatlabProxyObject` and allows Python functions to be passed to Matlab
where they can be evaluated through a `mex` function as explained in the next section.


# Calling Python from compiled Matlab

As noted in the [restrictions section](#compiled-matlab), Python code can be called in the normal Matlab interpreter using the `py.*` namespace.
For example, `py.numpy.random.rand(int32(3),int32(3))` will create a 3x3 numpy array of random numbers in Matlab.
This method, however, *must* not be used in compiled Matlab code intended to be used as a Python module,
because it causes a second Python interpreter to started within the same process as the Matlab process 
(which is actually the same process as the parent *Python* process because we are loading Matlab "in-process"). 
Having two Python interpreters in the same process invariably causes a memory error and hard crash.
There is no restriction on including `py.*` code in a compiled Matlab application 
because they can be safely handled if the Matlab application is called directly from the commandline and not loaded as a Python module.
A possible work-around is create the second Python interpreter (launched by `py.*`) in a new process ("out-of-process" execution). 
However testing shows that this imposes huge performance penalties (using Brille becomes an order of magnitude slower).
Furthermore for `pyHorace` the second interpreter is not connected with the user's interpreter
so cannot know about any fitting/modelling functions they have defined.

For these reasons, `pyHorace` opted to use a `mex` [file](https://github.com/mducle/hugo/blob/master/src/call_python.cpp) which is
called by Matlab instead of the Python function input. 
This mex file is linked to the CPython API so it can access the parent Python interpreter which is loaded into the same process.
(Thus this method will not work with an out-of-process Python interpreter).

First when the `DataTypes` class encounters a Python callable (a function or class which can be called), instead of passing this to Matlab,
it stores the function reference in a [module-global dictionary](https://github.com/mducle/hugo/blob/master/pyHorace/FunctionWrapper.py#L21),
and then creates a Matlab [`pythonFunctionWrapper`](https://github.com/mducle/hugo/blob/master/src/pythonFunctionWrapper.m) object
which stores the (string) key to the Python function.
Whenever `call_method` encounters a `pythonFunctionWrapper` object,
it [wraps](https://github.com/mducle/hugo/blob/master/src/check_wrapped_function.m) this in a call to the mex `call_python` function with the correct key.
Thus it appears to the user that Matlab is calling a Python function transparently (but actually happens is that Matlab calls `call_python`).
`call_python` then [retrieves](https://github.com/mducle/hugo/blob/master/src/call_python.cpp#L390) the Python function reference from the module-global `dict` 
and [calls](https://github.com/mducle/hugo/blob/master/src/call_python.cpp#L413) that function with the arguments given to it.

The majority of the code in `call_python` is for data conversion between Matlab and Python.
This is because `mex` functions may only take and return *Matlab* data types (Python objects are not allowed).
Similarly the CPython `PyObject_Call` function requires that inputs to the called functions are all of the `PyObject` type.
Thus `call_python` converts Matlab types to their Python equivalent and vice versa as per this table:

|      Python         |      |      Matlab      |
| ------------------- | ---- | ---------------- |
| `numpy.ndarray`     | <--> | numeric array    |
| `list` of numbers   | ---> | numeric array    |
| `str`               | <--> | `char` array     |
| `str`               | <--- | `string`         |
| `list` of `str`     | <--> | `string` array   |
| `dict`              | <--> | `struct`         |
| `list` of `dict`    | <--> | `struct` array   |
| `list`              | <--> | `cell` array     |
| `tuple`             | ---> | `cell` array     |
| ------------------- | ---- | ---------------- |

where "<-->" indicates the conversion is bi-directional, whilst "--->" a conversion from Python to Matlab only,
and "<---" is a conversion from Matlab to Python only.
That is, a Python `list` of numbers will be converted to a Matlab numeric array,
but such an array would never be converted back to a Python `list` (it would be converted to a `numpy.ndarray` instead).
And, both Matlab `string` and `char` arrays are converted to Python `str` but Python `str`s are always converted to `char` arrays.

The conversion from a Matlab array to a Python array involves no data copies - the raw memory pointed to by Matlab is wrapped in a numpy `array` object.
This is possible because that memory is only used in the Python function to be executed and not more widely.
The reverse conversion (from a `numpy` array to a Matlab array) involves a data copy
because Matlab `mex` does not support a shared data wrapping over memory which is not allocated by Matlab.
That is, Matlab supports creating a Matlab array only with two sets of API functions, 
`CreateArray` and the combination of `CreateArrayFromBuffer` and `CreateBuffer`.
`CreateArray` takes a pointer or iterator and copies the memory referenced,
whilst `CreateBuffer` allocates memory on the Matlab heap and returns a `unique_ptr` which is consumed by `CreateArrayFromBuffer`.

Note that Matlab objects, enumerations and sparse data types are currently not converted and will give an "`Unrecognised input`" error.
Likewise, Python objects or other data types not listed above returned by the Python functions will give an "`Unknown return type`" error.
In principle the conversions between Matlab and Python objects and vice versa
can be wrapped using the mechanisms described above for Matlab objects (through a `MatlabProxyObject`)
and below (through a `pythonclasswrapper`) for Python objects but this has not been implemented.

## The SpinW-Brille interface

Whilst the above mechanism works well for `multifit` to call a user defined Python model function or Euphonic,
for the SpinW-Brille interface an extra level of wrapping is needed.
This is because (after [ADR #9](../../documentation/adr/0009-brille-integration.md)) the Matlab SpinW code calls the Python Brille code directly.
Furthermore SpinW requires access to the Brille (Python) `BZGrid*` objects, which is possible with the built-in Matlab-Python (`py.*`) interface
but not allowed when using `call_python` because `mex` files can only return Matlab types.

The prototyped solution (subject to a ADR ([#12](../../documentation/adr/0012-matlab-python-wrapper.md))),
is to use two separate mechanisms for Matlab code to access Python.
One mechanism uses the built-in `py.*` namespace and is intended to be used from Matlab only (e.g. for users with a Matlab license).
The second mechanism will use `call_python` with Matlab-side and Python-side wrappers, and is intended to be used by `pyHorace`.
The key to ensuring interoperability is that both mechanisms present the same "API" to the Matlab code calling them
(SpinW in this particular case).
This would allow a single implementation of the Matlab code of SpinW, which will use one of the two different "back-ends",
depending on whether it is called from Matlab directly or from `pyHorace` in Python.

The "API" chosen is to present the Python classes / objects as if they are Matlab ones, with the same properties and methods.
For example, the Euphonic Python `ForceConstants` class is wrapped in a Matlab
[`force_constants`](https://github.com/mducle/horace-euphonic-interface/blob/da5e86fbd896e671a7380a14d494c6cdded2e718/%2Beuphonic/force_constants.m)
class which transparently passes through method calls and properties such that users can use the same syntax is Matlab as in Python.
E.g. `fc = ForceConstants.from_castep('quartz.castep_bin'); ph = fc.calculate_qpoint_phonon_modes([[1,1,1]])` in Python
and `fc = force_constants.from_castep('quartz.castep_bin'); ph = fc.calculate_qpoint_phonon_modes([1 1 1])` in Matlab.
This approach ensures that no instances of `py.` are present in the Matlab calling code which is compiled to produce `pyHorace`.
Hence, Matlab should never launch a second conflicting Python interpreter which could cause a crash in `pyHorace`.

An [implementation](https://github.com/mducle/horace-euphonic-interface/blob/light_wrapper/%2Beuphonic/light_python_wrapper.m)
of the first mechanism (using `py.*` intended to be used from the Matlab interpreter directly)
suited to the needs of Euphonic and Brillem, is currently in review.
In this case the Matlab `light_python_wrapper` class is used to wrap Python classes.
It works by overloading the `subsref` operator to intercept all "dot" and parenthese notation and passes these to Python.
In addition, it provides a `help` method which prints the Python documentation for the classes.

The equivalent class in the second mechanism (to be used by `pyHorace`) is
[`pyclasswrapper`](https://github.com/mducle/hugo/blob/master/src/pyclasswrapper.m).
This is a much lighter class which also overloads `subsref` but uses `call_python` instead of `py.*`
and does not provide as much functionality as `light_python_wrapper` (no `help` method for example).
Because `call_python` is a `mex` function and cannot return a Python object directly (unlike the `py.*` interface),
additional wrappings are needed on the Python side.
Firstly each Python class to be exposed to Matlab needs to have a 
[constructor function](https://github.com/mducle/hugo/blob/master/pyHorace/FunctionWrapper.py#L27) reference
stored in the module-global dictionary which `call_python` accesses.
This would create the desired (Python) object and store it in another module-global dictionary, returning the string key to `call_python`.
This key is then stored by `pyclasswrapper` (in contrast `light_python_wrapper` stores the actual Python object).
Two additional functions (`get_obj_prop` and `call_obj_method`) are defined and their references stored in the `call_python` dictionary.
They are called by `pyclasswrapper` to access properties and call methods of the Python object. 
`pyclasswrapper` passes the string key and method/property name to the object to these functions
and they then look up the objects in the module-global dictionary and use `getattr` to access the method/property of the Python object.


# Limitations and future work

There are currently some limitations due to the architecture chosen for `pyHorace` which can be alleviated with more work:

1. The Python syntax for any Matlab function/methods must exactly follow the Matlab syntax.
2. Matlab functions can only be called as methods of the `Matlab` class and not independently (e.g. `without the m.* prefix`)
3. Matlab help text cannot be accessed from Python.
4. MPI routines don't work.

Limitations 1 and 2 come from the choice, outlined in the [first section](#compiled-matlab) to use a gateway function which calls `feval`.
This can be overcome by writing an additional Python wrapper for each Matlab function or class we want to expose to Python.
Alternatively the `Matlab` and `MatlabProxyObject` classes can be modified to automatically
convert Python keyword arguments to `('name', value)` pairs to be passed to Matlab if the Matlab code is modified to accept them.

Limitation 3 comes from a restriction of the compiled Matlab output itself:
Matlab does not allow access to its online documentation system from compiled code.
The only way to work around this is to save the help text for every Matlab function or class we want to expose to Python to a text file
and then to either generate wrappers for each (such as that used to overcome limitations 1 and 2)
or to modify the `Matlab` and `MatlabProxyObject` classes to look up these help text.

Limitation 4 is because the MPI routines need to launch additional instances of the Matlab interpreter which is not possible from within Python.
This is just a limitation of the state of the current code rather than anything more fundamental,
and will be resolved when "compiled" workers are implemented in the MPI framework.
These compiled workers would be just like the compiled `horace` Python module except that instead of using `call_method`
and other Python focused gateway functions, they would use just `worker_v2.m` as the gateway function.
The MPI framework should then be able to launch these compiled worker executable and communicate as usual.

In addition, however, there are also limitations imposed by Matlab which cannot be alleviated:

5. Must compile Matlab code for specific Matlab release.
6. Must use a specific C++ compiler for the `mex` files.

Restriction 5 means for example that a package created with Matlab R2020a can only be used with the MCR 2020a version.
(Note that users must download and install the MCR to run `pyHorace` even if they already have a Matlab license and Matlab installed
unless they also have the Matlab Compiler toolbox installed).
Matlab also only supports specific C++ compilers for `mex` files.
Using an older compiler will generate files which will work on a new Matlab version but the reverse is generally not true.
This means that if we want to support the widest range of operating systems and Matlab versions,
we need to use an older compiler which may not support newer C++ features (e.g. from C++17 or C++20).


# Code Examples

Many examples are included in the root folder [prototype implementation](https://github.com/mducle/hugo).
We reproduce here an example of generating a simulated phonon spectrum with resolution convolution,
which uses a combination of Horace and Euphonic.

```python
from euphonic import ForceConstants
from pyHorace import Matlab, EuphonicWrapper
m = Matlab
import numpy as np

# Some parameters
scalefac = 1e12
effective_fwhm = 1
intrinsic_fwhm = 0.1

# Make a cut of a measured dataset using Horace
wsc = m.cut_sqw('quartz/2ph_m4_0_ECut.sqw', [-3.02, -2.98], [5, 0.5, 38])

# Set up instrument and sample information
is_crystal = True; xgeom = [0,0,1]; ygeom = [0,1,0];
shape = 'cuboid'; shape_pars = [0.01,0.05,0.01];
wsc = m.set_sample(wsc, m.IX_sample(is_crystal, xgeom, ygeom, shape, shape_pars));
ei = 40; freq = 400; chopper = 'g';
wsc = m.set_instrument(wsc, m.merlin_instrument(ei, freq, chopper));

# Loads a CASTEP DFT dataset and create an object to calculate the dispersion
fc = ForceConstants.from_castep('quartz/quartz.castep_bin')
euobj = EuphonicWrapper(fc, debye_waller_grid=[6, 6, 6], temperature=100,
                        negative_e=True, asr=True, chunk=10000, use_c=True)

# Calculates a simulated spectrum *without* resolution convolution
wsim = m.disp2sqw_eval(wsc, euobj.horace_disp, (scalefac), effective_fwhm)

# Explicitly create a Matlab function handle here,
# since we can't use the "@" notation in the `set_fun` command below.
disp2sqwfun = m.eval('@disp2sqw');

# Calculate *with* resolution convolution
kk = m.tobyfit(wsc);
kk = kk.set_fun(disp2sqwfun, [euobj.horace_disp, [scalefac], intrinsic_fwhm]);
wsimres = kk.simulate()

# Plot
hf = m.plot(wsc); m.pl(wsim); m.acolor('red'); m.pl(wsimres);
m.uiwait(hf)
```

In the example, Matlab functions are called from Python using the `m.<func_name>` syntax
which is described in the [second section](#gateway-functions-and-proxy-classes). 

`fc` and `euobj` are purely Python objects and `euobj.horace_disp` is a Python function reference.
This Python function reference can be used in place of a Matlab function handle in Matlab functions that need one.
In the above example these are `disp2sqw_eval` and `set_fun`.
In the first instance, `m.disp2sqw_eval` actually calls `Matlab.__getattr__()`
as described in the [second section](#gateway-functions-and-proxy-classes).
`__getattr__()` detects a Python function reference and converts it to a Matlab `pythonFunctionWrapper` object,
storing the actual Python function reference in a module-global dictionary
as described in [this section](#calling-python-from-compiled-matlab).
It then calls the Matlab `call_method('disp2sqw_eval',...)` function.
This detects a `pythonFunctionWrapper` object and rewraps this in a Matlab anonymous function around
the `mex` function `call_python()` which knows to look in the module-global dictionary to call the true Python function.
This anonymous function handle is then passed to the desired Matlab function (`disp2sqw_eval` in this case),
which treats it just like any other Matlab function handle it is passed.

In the example, we also need to pass the function handle to `disp2sqw_eval` to `set_fun`,
but we used `disp2sqwfun = m.eval('@disp2sqw')` to do this.
This is because we have chosen not to implement the Matlab "@" notation to create a function handle from a function name.
It may be possible to implement this in Python, but the unary "@" symbol in Python is reserved for decorators and cannot be overloaded.
It is also the binary matrix multiplication operator, and this operator can be overloaded using the `__matmul__` function. 
However, this would mean that the syntax must be something like `0@m.disp2sqw` (requiring something on the LHS of the function name).
Alternatively one of the Python unary arithmetic operator symbols (`~` inverse, `-` negative, or `+` positive) could be overloaded. 

