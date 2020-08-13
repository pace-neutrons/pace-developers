# An Application Programming Interface for user defined model functions in PACE
**2020-05-15**


# Scope

This documents details the required function signatures for user defined sample scattering models
and how they interface with Horace, using either Matlab, Python, C, C++ or Fortran.


# Motivation

Analysis of inelastic neutron scattering data almost always requires a parameterised model of the measured scattering intensities.
Horace, as currently implemented, requires this model to be in the form of a Matlab function.
This function is required to either 

1. Take a 4D vector of momentum-energy ![\mathbb{Q} \equiv (\mathb{Q},E)] and yield the scattering function ![S(\mathbb{Q})].
2. Take the 3D vector of momentum transfer ![\mathbf{Q}] only and yield ![N] sets of vectors ![(E_n, S(\mathbf{Q}, E_n))] where ![N] is the number of dispersion branches.

For type 2, the ![N] sets of vectors are contained in a cell array
and a helper function `disp2sqw` is used to obtain ![S(\mathbb{Q})]
by convolving the calculated delta-function dispersion with broadening functions (Gaussian is default). 
Whilst the internal fitting routines of Horace (including for resolution convolution) requires type 1 model functions (yielding ![S(\mathbb{Q})]),
many actual user models are type 2, including `SpinW` and `Euphonic`.
Thus, the new PACE implementation should allow both types of models.
We also note, that when instrumental resolution convolution (`TobyFit`) is used,
the broadening function in `disp2sqw` should only represent some intrinsic physical broadening
(such as a quasiparticle lifetime).
Whereas when `TobyFit` is not used,
the broadening function in `disp2sqw` will be a combination of both intrinsic and instrumental resolution broadening.

In the current Horace implementation, these model functions are used by the `multifit_sqw` function/class
(which inherits from `multifit`) to fit to data using a built-in Levenberg-Marquardt optimizer. 
The [new design for PACE](Model_Optimisation_Design.md) proposes instead to use a host of classes including `OptFunction` and `OptModel`.
`OptModel` will be more like the current `multifit` (or `tobyfit`) class,
whilst `OptFunction` is a wrapper around the user supplied model function to handle parameter bindings and bounds currently handled by `multifit`.
`OptFunction` should therefore have functionality to transform type 2 input to type 1 input
whilst `OptModel` would expect only type 1 input.

The current implementation of Horace is Matlab-focussed and user defined model functions must be Matlab functions.
PACE, however, will have a Python version or interface.
For ease of use, therefore, users *should* be able to define their models using Python functions.
In addition, many models of inelastic scattering are quite compute-intensive.
For this reason, PACE should also be able to support user defined models which are embodied in compiled libraries.
The aim of this design document is to define the interface between these user defined models, in whichever language, and the Horace/PACE fitting infrastructure.

However, for concreteness, *the rest of this document will assume that the new optimisation **framework** will be written in Matlab.*
The proposed API may need to change should it be decided to implement the optimisation framework in a different language.


# <a href="external_interfaces"></a> Matlab interfaces to external languages

One immediate restriction on non-Matlab user-defined model functions is that its *input* arguments must be "plain-old-data" (POD, numeric types or strings) arrays only, and not objects.
This is because Matlab does not allow its own objects (instances of Matlab-defined classes) to be passed to external libraries.
(A workaround for this for the Python user interface using a compiled Horace library exists,
and is described [here](../../python_interface/design/01_pace_python_high_level_discussion.md#interpreter-calls)).
This means that the second type of function signatures described in the [optimisation design document](Model_Optimisation_Design.md#optimisation-function-object), 
where Matlab objects (in particular an `sqw` object) are passed as input to the user defined function,
will not be possible with non-Matlab functions, unless `OptFunction` unwraps this object into a (several) POD array(s).

The next difficulty is to infer the required input arguments for user defined model functions.
Several methods for this springs to mind:

1. Using properties of `OptFunction` to indicate the input that the user defined model function takes as described [here](Model_Optimisation_Design.md#optimisation-function-object).
2. By Horace interrogating the function as to its input requirements by calling it with a single special argument.
3. Embedded in the function name - for example functions with suffix `_sqw` are assumed to take crystal coordinates ![\mathbf{Q}] as inputs.
4. Infer input arguments using language specific constructs (e.g. the `inspect` module in Python, C++ templates).

Which of these methods is best depends on the language of the user defined model function and is a topic for discussion.
The first method would be easiest to implement for all languages.
The second method will likely only work for Matlab and Python,
since variable number of arguments is difficult to implement in compiled languages.
Method 3 (inference from function name) will probably work for all languages,
but may prove difficult to implement for the compiled languages.
Method 4 would only work for Python and C++.

As discussed in the section on [user models written in compiled languages](#compiled) below,
Matlab has two ways to call functions in a compiled library,
the simpler of which uses a C interface (not C++).
*As noted there, we propose to use this C-style approach, in order to present a simple and uniform API for all compiled languages.*
However, this means that methods 2 and 4 for inferring input arguments are not feasible,
and method 3 would be difficult to implement as discussed in the [section on the C API](#c_functions).


## <a name="python"></a> Python

There are two use cases for user defined model functions written in Python:

1. The user is running Matlab (has a license) and wants to call a model function (e.g. Euphonic) written in Python.
2. The user is running Horace in Python using the compiled library and wants to call their own Python model function.

Taking the first case, it is currently possible to do this in Matlab
(as exemplified by the [`meuphonic` project](https://github.com/pace-neutrons/Meuphonic)).
This requires, however, conversions between Matlab and Python data types,
(as demonstrated by the `m2p` and `p2m` methods of [Brille](https://github.com/g5t/brille/)),
which implicitly requires a memory copy in each direction
(one memory copy of each input and output arrays for a single function evaluation).

We can avoid the memory copy for the input argument arrays as long as they are restricted to be numeric arrays (`numpy` on Python-side) only.
This would use a `mex` file to wrap the Python function call and its arguments in a `numpy` array,
similar to the work described [here](../../python_interface/design/02_pace_python_implementation_discussion.md#pymatpy).

As noted in the [Appendix](#app_nativememory), avoiding a memory copy of the output argument is only possible
by passing a Matlab-allocated memory block (wrapped in a `numpy` array) to Python for the user defined function to fill in its value.
This is not straightforward for users to implement (it requires users to avoid using the assignment operator for the output [return] value).
In these cases, it is likely that a memory copy of the output argument is unavoidable.
However, for PACE-supported projects such as Euphonic, this method may be used to avoid the output memory copy.

For the second case (user without Matlab license running Horace through Python and a compiled library),
we can use a similar [`mex` file](https://github.com/mducle/hugo/blob/master/src/call_python.cpp).
This again will wrap the input arguments so that no memory copies occur, provided that the inputs are only numeric arrays,
and the Python side function expects only `numpy` arrays as inputs.
Again, like the first case, output arguments will have to be memory-copies
or the user-defined function should fill in values in a Matlab-allocated `numpy` wrapped array.


## <a name="compiled"></a> Compiled languages

Matlab supports calling functions from compiled libraries through two interfaces:

1. A procedural interface using `loadlibrary` and `calllib` for dynamically loaded libraries using C calling conventions.
2. An object oriented interface using `clib` for C++ specifically.

For case 1, "C calling conventions" may apply to code written in C, Fortran (since 2003) and C++ (with `extern C`).
This method is essentially the same as using the `dlopen` (POSIX) or `LoadLibrary` (Windows) system calls.
In this case the library and entry point function names are given as strings to `loadlibrary` (library name) and `calllib` (function name)
and must match those in the compiled library.
In order for Matlab to understand the required input and output types,
the header `.h` file of the library should be provided to the `loadlibrary` call.
(This header file should be the same for Fortran and C++ code).
We propose to define this header file in the API and include it with Horace so users need not write their own.
This does mean that the function signatures are restricted
and precludes using methods 2 and 4 for inferring input arguments described in the [above section](#external_interfaces).

For case 2, Matlab requires a compiled wrapper (which it calls an *interface*) to the C++ library.
This wrapper is generated by the `clibgen` function in Matlab from a C++ `.hpp` header file and a Matlab live `.mlx` script
(a skeleton one is auto-generated by `clibgen`).
The Matlab generated wrapper library allows the user to create an object of the C++ class defined by the library
and to call its methods / access its properties directly in Matlab.
For example, if the C++ library `samplelib` defines a `Crystal` object with properties `BMatrix` and `Orientation` and method `Rotate`,
the properties may be obtained in Matlab by `xtal = clib.samplelib.Crystal(abc, alf); B = xtal.BMatrix;`
and `rotated_xtal = xtal.Rotate(alpha, beta, gamma); new_orientation = rotated_xtal.Orientation`. 

Whilst the `clib` approach allows C++ classes to be more directly accessed in Matlab,
it is not necessary for our purposes, which requires only calling a single function.
Furthermore, using `clib` requires a compiled wrapper library to be generated using `clibgen`,
which should be done for each user generated function.

*For these reasons, we propose to use the* `loadlibrary` *and* `calllib` *method instead, with a predefined header file.*
This header file (which must be a file - this is a limitation of `loadlibrary`) may be generated on-the-fly
in order to accommodate custom user function names.
Also, if we are to accommodate method 3 for inferring input arguments [noted above](#external_interfaces)
then this header file must be generated dynamically.

The actual function signatures and API are discussed for each language separately in the sections below, 
but we should note here a limitation with using `loadlibrary` (and using dynamically loaded libraries in general).
This is because the C-language function may only accept pointers to arrays,
and because, as noted [in the appendix](app_nativememory) the main Matlab code and library codes have different memory heaps,
so they must each be responsible for allocating *and deallocating* their own memory.
That is, a memory error will occur if Matlab tries to deallocate a memory block allocated by the library and vice versa.
To avoid this, *we propose to not allow user functions to allocate their own memory for the results array*.
That is, Matlab will allocate an array for the results and pass the pointer to this to the user model function.
The user model function must then fill this array with the result of the calculations,
rather than using their own allocated array.

Finally we note that the compiled library interface deal *exclusively* with real-valued variables.
The user defined model function is supplied with real input coordinates ![\mathbb{Q}] and is expected to return real ![S(\mathbb{Q})].
It should thus not return complex values, even if the calculations result in complex values.
In these cases it should either raise an error or a warning.


# User defined model function signatures

## <a name="matlab_functions"></a> Matlab

```matlab
function user_model_sqw(qh, qk, ql, en, parameters, varargin)
function user_model_dsp(qh, qk, ql, parameters, varargin)
function user_model_pow(modQ, en, parameters, varargin)
function user_model_1d(en, parameters, varargin)
function user_model_0d(parameters, varargin)
```

This follows the convention established by the current implementation of `multifit`.
`varargin` is a cell array of an arbitrary number of arguments which is passed directly to the function and is not modified by the minimizer.
`user_model_sqw` corresponds to type 1 in the [initial section](#motivation),
and `user_model_dsp` corresponds to type 2.
The other three signatures are new and corresponds to suggestions in the [optimisation design document](Model_Optimisation_Design.md#calling-the-function-inside-optfunction),
and represents modelling a powder sample,
a sample with dispersionless excitations (e.g. crystal field levels)
and scattering with no dependence on the sample orientation or energy (e.g. background from sample environment) respectively.

In order to use these functions with the new optimisation framework, one should initialise an `OptFunction` object referencing them e.g.

```matlab
optfun_sqw = OptFunction(@user_model_sqw, 'type', 'double', 'inputs', 4, 'parameters', parvec, 'arguments', argcell);
optfun_dsp = OptFunction(@user_model_dsp, 'type', 'double', 'inputs', 3, 'parameters', parvec, 'arguments', argcell);
optfun_pow = OptFunction(@user_model_pow, 'type', 'double', 'inputs', 2, 'parameters', parvec, 'arguments', argcell);
optfun_1d = OptFunction(@user_model_1d, 'type', 'double', 'inputs', 1, 'parameters', parvec, 'arguments', argcell);
optfun_0d = OptFunction(@user_model_0d, 'type', 'double', 'inputs', 0, 'parameters', parvec, 'arguments', argcell);
```

where `parvec` is a vector of parameters and `argcell` is a cell-array of arguments (which may be omitted),
which is passed (as `varargin`) unmodified directly to the user functions.


## <a name="python_functions"></a> Python

When a Python function is to be called from Horace running in Matlab, the following signatures should be used:

```python
def user_model_sqw(qh, qk, ql, en, parameters, *args):
def user_model_dsp(qh, qk, ql, parameters, *args):
def user_model_pow(modQ, en, parameters, *args):
def user_model_1d(en, parameters, *args):
def user_model_0d(parameters, *args):
```

A Matlab cell array is passed to Python as a list which corresponds to the positional arguments `*args`.
The "pythonic" way would be to used named keyword arguments `**kwargs` which are Python `dict`s / Matlab `struct`s,
however this behaviour is not as natural in Matlab.

In the case of `pyHorace` which is run from Python, slightly modified function signatures are possible:

```python
def user_model_sqw(qh, qk, ql, en, parameters, *args, **kwargs):
```

etc. could be used instead, since `pyHorace` will have Python wrappers which can interpret "(string, param)" pairs in a cell array as keyword arguments.
To set up the `OptFunction` objects in `pyHorace` either keyword or positional arguments will be accepted, but not a mix:

```python
optfun_sqw = m.OptFunction(user_model_sqw, 'type', 'double', 'inputs', 4, 'parameters', parvec, 'arguments', arglist)
optfun_sqw = m.OptFunction(user_model_sqw, type='double', inputs=4, parameters=parvec, **kwargs_for_func)
```

A mix of keywords and Matlab-style pairs of keyword and positional arguments will give an error, as this mix can cause ambiguities which are hard to parse.


## <a name="c_functions"></a> C

As we are using `loadlibrary` / `calllib` to get Matlab to evaluate a function in a compiled library,
we need to use C-calling conventions for these functions for all languages: C, C++ and Fortran.
In order to accommodate Fortran, these functions *should pass by reference only*, and have no return values.

The function signatures in C is thus:

```c
void user_model_sqw(const double *qh, const double *qk, const double *ql, const double *en,
                    const double *parameters, double *results, unsigned long *n_elem);
void user_model_dsp(const double *qh, const double *qk, const double *ql,
                    const double *parameters, double *result_omega, double *results_S, int *n_elem);
```

where `n_elem` is the number of elements which Matlab expects `results` to have and the length of all input vectors.

When constructing the `OptFunction` object in Matlab, the user should use a gateway Matlab function (e.g. `@compiled_model`)
and must tell Horace which type of C function is used (how many inputs) and their names:

```matlab
argcell = {'library_name', 'mymodellib', 'function_name', 'mymodel'};
optfun_sqw = OptFunction(@compiled_model, 'type', 'double', 'inputs', 4, ...
                         'parameters', parvec, 'arguments', argcell);
```

By default `'function_name'` is one of the names given above (e.g. `user_model_sqw`).
`compiled_model` can be a very simple function:

```matlab
function out = compiled_model(h, k, l, en, p, libname, funcname)
    if ~libisloaded(libname)
        loadlibrary(libname, '/tmp/userlib.h')  % userlib.h is dynamically generated
    end
    if ~exist('funcname', 'var'); funcname = 'user_model_sqw'; end
    res = libpointer('doublePtr', h);
    calllib(libname, funcname, h, k, l, en, p, res, numel(h));
    out = res.value;
end
```

Matlab automatically translates `h`, `k`, `l`, `en`, and `p` to constant C pointers (without memory copy),
and we use `libpointer` to allocate a Matlab array which is attached to a C pointer for the results.

PACE will provide a gateway function like `@compiled_model`,
but users may also implement their own gateway functions.
These case will look to Horace just like if the user model was a pure Matlab function.


## <a name="cpp_functions"></a> C++

Because we are using the Matlab C library interface, we cannot use any C++-specific constructs in the exported user defined function header.
In addition, functions must be declared `extern "C"` when compiled into a library.
The C++ signature therefore looks very similar to the C signatures:

```cpp
extern "C" void user_model_sqw(const double *qh, const double *qk, const double *ql, const double *en, const double *parameters, double *result, int *n_elem);
```

## <a name="fortran_functions"></a> Fortran

We will only support Fortran 2003 and newer standards, as this release introduced a [standard C-language binding](https://fortran.bcs.org/2002/interop.htm)
(previously a de-facto standard which worked for most compilers was used).
This is not strictly necessary since the functions we use are simple enough that some underscore name mangling is sufficient,
however restricting to Fortran 2003 will allow further enhancements as noted in the section on [use of non-parametric arguments](#user_internal_objects).

```fortran
subroutine user_model_sqw(h, k, l, en, parameters, results, n_elem) bind(C)
    integer, intent(in) :: n_elem
    real(8), dimension(n_elem), intent(in) :: h, k, l, en
    real(8), dimension(:), intent(in) :: parameters
    real(8), dimension(n_elem), intent(out) :: results
    ...
end subroutine user_model_sqw
```

Note that users should define a Fortran `subroutine` and not a `function` as this will return a value which is not expected by the C header.
Also note that `parameter` and `result` are Fortran keywords and may not be used as variable names.
`bind(C)` is needed to generate C-readable function names
(Fortran compilers usually append a `_` to user function names to avoid name collisions with system libraries,
but this is compiler dependent and was a source of bugs before the standardisation in Fortran 2003).


# <a name="user_internal_objects"></a> Non-variable parameters in compiled user models

While the function signatures for Matlab and Python functions allowed for arbitrary non-parametric data to be passed to the user functions,
the function signatures for compiled libraries described above do not.
The functionality given by the `args` and `varargin` parameters in Python and Matlab *could* be achieved by other means in compiled libraries.
For example, in Fortran a `common` block may be used to pass parameters from one iteration to another,
whilst in C and C++ a global `struct` or a set of global variables serves the same purpose.

These methods are not thread-safe however.
Although it is envisaged that parallelisation in Horace will use MPI and hence not need threads,
it may be good to provide an alternative to global variables to pass non-varying parameters between model function evaluations.
In addition, it would allow these parameters to be initialised from Matlab at runtime.

We propose to allow a C `struct` to be passed (as a `void *` pointer) between Matlab and the user function.
The user defined function signature would thus be changed to:

```c
void user_model_sqw(const double *qh, const double *qk, const double *ql, const double *en,
                    const double *parameters, double *results, int *n_elem, void *owndata);
```

Users may either generate the structure in Matlab by converting a Matlab `struct` to a C-`struct` using `libstruct` in Matlab,
or they may define a pair of functions to create and destroy the structure which Horace will call as needed.
In order to allow flexibility in these functions,
the function signature for these initialisation and destruction functions should be defined by the users themselves.
Specifically we propose the following syntax for declaring these types of functions to `OptFunction` in Matlab:

```matlab
% Case 1: Where users define a struct using libstruct in Matlab
my_struct.p = 3.141592; my_struct.f = [1 1 2 3 5]; my_struct.l = libpointer('cstring', 'logfile.dat');
argcell = {'library_name', 'mymodellib', 'function_name', 'mymodel', 'need_own_data', true, ...
           'own_data_struct', libstruct('mymodel_struct', my_struct)};

% Case 2: where they want to allocate / deallocate their own data structure
argcell = {'library_name', 'mymodellib', 'function_name', 'mymodel', 'need_own_data', true, ...
           'own_data_struct_fields', {'char', 'int', 'double'}, ...
           'own_data_struct_values', {libpointer('cstring', 'input.dat'), int32(378161), [4.13 4.13 9.51 90 90 120]}};

optfun_sqw = OptFunction(@compiled_model, 'type', 'double', 'inputs', 4, ...
                         'parameters', parvec, 'arguments', argcell);
```

The user must first specify that they `need_own_data`.
By default this parameter is false and the other parameters `own_data_struct` etc. are empty.

In case 1, users specify the input data as a Matlab `struct` and use `libstruct` to convert it to a C `struct`.
This could be used for the simple input of non-parametric data.
Note that if a C string type (`char *`) is specified as a field, it must be created on the Matlab side using `libpointer`.
Note also that `int` or other types should be specified explicitly (Matlab uses `double` by default).

In case 2, users specify two additional parameters, `own_data_struct_fields` and `own_data_struct_values`, to `OptFunction`.
From these, Horace will construct the following initialisation / destruction function signatures:

```c
void *mymodel_init(const char *p1, const int *p2, const double *p3);
void mymodel_destroy(void *model_data);
```

The initialisation function should return an allocated structure cast to a void pointer.
The alternative signature with no return value does not work because Matlab does not allow a library to overwrite a `libpointer` object.
Thus the Fortran signature (see below) for `_init` should be a `function` rather than a `subroutine`.

The initialisation/destruction function name prefixes will always be the same as the model function name,
and the suffix will always be `_init` or `_destroy`.
`p1`, `p2` and `p3` etc. are defined by `own_data_struct_fields` and may be scalars or arrays.
In the case of arrays the user defined functions must know in advance how many elements they have.
The pointers `p1`, `p2` etc. will point to memory owned by Matlab and may be deallocated after the call to `mymodel_init`,
so the initialisation function must *copy* their contents into `model_data` rather than just assign the pointer.
The user should define the structure in C, and then cast the `void*` pointer to its type:

```c
#include <stdlib.h>
#include <string.h>
struct mymodel_data {
    char *in;
    int seed;
    double[6] alf;
    double *pos;   /* Additional field defined in _init() */
    double *bonds; /* Additional field defined in _init() */
}
void *mymodel_init(const char *in, const int *seed, const double *alf) {
    struct mymodel_data *the_data = (struct mymodel_data *)malloc(sizeof(mymodel_data));
    // Need to allocate the char array
    the_data->in = (char *)malloc(strlen(in) * sizeof(char));
    strcpy(the_data->in, in);
    the_data->seed = *seed;
    memcpy(the_data->alf, alf, 6*sizeof(double));
    /* further processing - e.g. reading input file */
    return (void *)the_data;
}
void mymodel_destroy(void *model_data) {
    free(((struct mymodel_data *)model_data)->in);
    free(model_data);
}
```

Case 2 is envisaged for situations where the user model function needs to define additional fields to the `struct`,
for example from reading an input file, than can be defined simply in Matlab.

The C++ syntax will be the same, apart from being in an `extern "C"` block,
and perhaps using `new` and `delete` instead of `malloc` and `free`.

## <a name="fortran_structs"></a> Fortran

The Fortran syntax for the model function is slightly different and will need to use the ISO C bindings defined in Fortran 2003.
The user has to define the structure as a Fortran class (`type`)
and then associate the received C pointer to a Fortran pointer to this class
with the `c_f_pointer` subroutine provided by the ISO C bindings.

```fortran
subroutine user_model_sqw(h, k, l, en, parameters, results, n_elem, c_data) bind(C)
    use iso_c_bindings
    type my_data
        real(8) dat
    end type my_data

    integer, intent(in) :: n_elem
    real(8), dimension(n_elem), intent(in) :: h, k, l, en
    real(8), dimension(:), intent(in) :: parameters
    real(8), dimension(n_elem), intent(out) :: results
    type(c_ptr), intent(in), value :: c_data
    type(my_data), pointer :: f_data
    ...
    call c_f_pointer(c_data, f_data)
    ...
    ! Use the data as: f_data%dat
end subroutine user_model_sqw
```

Note the `use iso_c_bindings`, and that the input structure should be declared as `type(c_ptr), value`,
since although C passes a pointer, Fortran interprets it as a value.
If it is declared only as `type(c_ptr)` a memory error will occur
when the call to the system subroutine `c_f_pointer` tries to associate the un-dereferenced `c_data` to `f_data`.

Handling string inputs from C to Fortran is also tricky because the ISO bindings
define a C string to be a Fortran *array* of 1-element `character`s rather than a (Fortran) string.
Thus, a helper function is needed:

```fortran
module my_sqw
    use iso_c_bindings
    type my_data
        type(c_ptr) :: my_string
    end type my_data

    contains

    ! https://stackoverflow.com/questions/20365293/
    function c2fstr(c_str)
        interface
            pure function strlen(s) bind(C, name="strlen")
                use, intrinsic :: iso_c_binding
                type(c_ptr), intent(in) :: s
                integer(c_size_t) strlen
            end function strlen
        end interface
        type(c_ptr) c_str
        character(kind=c_char, len=strlen(c_str)), pointer :: c2fstr
        call c_f_pointer(c_str, c2fstr)
    end function c2fstr

    subroutine user_model_sqw(h, k, l, en, parameters, results, n_elem, c_data) bind(C)
        integer, intent(in) :: n_elem
        real(8), dimension(n_elem), intent(in) :: h, k, l, en
        real(8), dimension(:), intent(in) :: parameters
        real(8), dimension(n_elem), intent(out) :: results
        type(c_ptr), intent(in), value :: c_data
        type(my_data), pointer :: f_data
        ...
        call c_f_pointer(c_data, f_data)
        print *, c2fstr(f_data%my_string)
        ...
    end subroutine user_model_sqw
 
end module my_sqw
```

Note that the C string here is defined to be `type(c_ptr)` (not `c_char`),
and we use the C standard library function `strlen` to determine the string length to define the correct Fortran string.
Also note that the `c2fstr` function only casts a C pointer to a Fortran pointer.
If the underlying C data is destroyed the Fortran pointer will be dangling.
Thus this method will not be suitable for use in case 2 when users need to initialise their own structures.

In these cases, the Fortran syntax for non-string data is similar to the C examples:

```fortran
module my_sqw
    use iso_c_bindings
    type my_data
        real(8) val
    end type my_data

    contains

    function user_model_init(val) bind(C) result(c_struc)
        real(8), intent(in) :: val
        type(c_ptr) :: c_struc
        type(my_data), pointer :: f_data
        allocate(f_data)
        f_data%val = val
        c_struc = c_loc(f_data)
    end function user_model_init

    subroutine user_model_destroy(c_struc) bind(C)
        type(c_ptr), intent(in) :: c_struc
        type(my_data), pointer :: f_data
        call c_f_pointer(c_struc, f_data)
        deallocate(f_data)
    end subroutine user_model_destroy

    subroutine user_model_sqw(h, k, l, en, parameters, results, n_elem, c_data) bind(C)
        ...
    end subroutine user_model_sqw
 
end module my_sqw
```

In Fortran the assignment is a copy-assignment, and there is no need to dereference the inputs.
Note the use of a `function` for `user_model_init` rather than a `subroutine` since we must return the pointer to the structure.

String handling is much more complicated, however, and needs another helper function.
A working example may be found in the [hugo repository](https://github.com/mducle/hugo/blob/master/extlib/fe_sqw_struct_init.f90#L12).


# Conclusions

The proposed API for user defined model functions has be specified,
in the form of function signatures for functions written in Matlab, Python, C, C++ and Fortran.

Working examples may be found [here](https://github.com/mducle/hugo/tree/master/extlib).


# <a name="app_nativememory"></a> Appendix: Matlab array from Python allocated memory

When we run a Python interpreter in a Matlab instance or a compiled Horace library in a Python instance,
we use *in-process* library loading so have only a single *process*,
meaning that both Matlab and Python memory are accessible to the other.
However, in order to dynamically allocate memory each *compilation unit* (e.g. Matlab *or* Python) requires its own *free memory store* (or *heap*)
and does not know about the other's heap.
Thus memory allocated by Matlab must be deallocated by Matlab and similarly with Python.
That is, Matlab cannot deallocate memory allocated by Python because it does not know about the Python heap.

Thus the ideal design would have a Matlab or Python object *share* a memory block.
`numpy` allows this using the `OWNDATA` flag which may be set by the user,
so that when a `numpy` array which does not own its data is deleted,
`numpy` will not try to free the associated memory.
Matlab does not (in its published API) allow this.

Nonetheless, it is possible using the `createArrayFromBuffer` to create a Matlab array which wraps some arbitrary memory
but it is not possible to tell Matlab not to deallocate this memory when it deletes the array.
Thus when an array created using `createArrayFromBuffer` with a non-Matlab allocated buffer is deleted,
a heap memory error will occur which will crash the program.
Matlab only supports the use of `createArrayFromBuffer` using Matlab allocated memory using the `createBuffer` method.
It is possible to modify the internals of a Matlab array to manually disassociate such an array from its buffer
and then safely delete the array but this requires extensive wrapping and is still a fragile design.

We have thus decided not to implement such a design and to either require functions
to fill in a Matlab allocated array or to live with a memory copy.

<!---
LaTeX equations used repeatedly can be defined as references, with format
	[latex_equation]: %-encoded link to image generator
then, if image generation fails for some reason, the alt-text for each equation
will still contain the raw LaTeX equation which is often intelligible

Constructing the %-encoded link can be done at, e.g., the codecogs website
	https://www.codecogs.com/eqnedit.php?latex=latex_equation
--->
[\mathbb{Q} \equiv (\mathb{Q},E)]:http://latex.codecogs.com/svg.latex?%5Cmathbb%7BQ%7D%5Cequiv%28%5Cmathbf%7BQ%7D%2CE%29
[S(\mathbb{Q})]: http://latex.codecogs.com/svg.latex?S%28%5Cmathbb%7BQ%7D%29
[\mathbf{Q}]: http://latex.codecogs.com/svg.latex?%5Cmathbf%7BQ%7D
[\mathbb{Q}]: http://latex.codecogs.com/svg.latex?%5Cmathbb%7BQ%7D
[N]: http://latex.codecogs.com/svg.latex?N
[(E_n, S(\mathbf{Q}, E_n))]: http://latex.codecogs.com/svg.latex?%28E_n%2C%20S%28%5Cmathbf%7BQ%7D%2C%20E_n%29%29
