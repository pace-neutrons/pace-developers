[<-previous](0009-brille-integration.md) | next->

# 10. pyHorace Matlab code should use a mex interface to call Python functions

Date: 2020-Dec-02

## Status

Proposed


## Context

`pyHorace` ([prototype](https://github.com/mducle/hugo)) is the proposed Python module for PACE
which packages the Matlab Horace/Herbert codes as a "compiled" library.
The Matlab code within this library needs to interact with Python code in the host.
As detailed in [this design document](../../01_pace_python_high_level_discussion.md#-calling-user-defined-functions)
there are two main methods for the compiled Matlab code to call a Python function:

1. Using a `mex` file.
2. Using a "reverse communications interface" (RCI).

In the `mex` method, a reference to the Python function is given to the `mex` file which uses the CPython
API to call that function (in Python) and then automatically converts (copies) the results to Matlab (`Array`) format.
In the RCI approach, the standard Matlab-Python interface is used but is restricted to specific use of `multifit`.
This is because the standard Matlab-Python interface does not allow the compiled Matlab code to call Python functions
directly, it only allows the Python interpreter to call the compiled Matlab functions.
Thus, to allow `multifit` to work, the Matlab `multifit` class needs to be refactored to allow it to _receive_ the residuals
rather than to call a function evaluate a model and calculate the residuals itself.
In addition, a Python wrapper class is needed which Python users call instead of the Matlab `multifit`.
This Python wrapper can then call the user model, calculate the residual and send it (at each iteration) to the Matlab `multifit`.

Thus, whilst the RCI uses the documented API (which should make it more stable and robust) 
it is very restrictive and requires significant changes to `multifit` (which will happen in any case). 
The `mex` option allows the current Matlab code to be used without modifications and is more flexible,
but can result in hard crashes (segmentation faults).
In addition, `mex` functions _cannot_ use non-Matlab (non-`Array` types) data as input or outputs.
Thus all data must be converted to/from Matlab from/to Python, which involves at least one data copy.
This restriction means that not all Python functions can be supported by this method 
(e.g. those which return non-convertible types such as Python classes).
This also means that the reference to the Python function cannot be passed directly to the `mex` function.
Rather, the Python code stores it in a global dictionary and the (string) key is passed to the `mex`.


## Decision

The decision was taken to use the `mex` method for compiled Matlab code to call Python functions.


## Consequences

User model functions written in Python (which includes Euphonic and Brille) cannot return non-convertible data.
That is, scalar values and standard containers (lists, tuples, dicts, numpy arrays) can be returned but Python objects cannot.
The current [mex implementation](https://github.com/mducle/hugo/blob/master/src/call_python.cpp) does not
handle `dict`s and string types but this can be implemented.
It may be possible to handle arbitrary Python objects using a global dictionary similarly to how function references are handled.
