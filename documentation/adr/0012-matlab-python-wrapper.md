[<-previous](0011-use-mex-for-pyHorace-python-calls.md) | [next->]()

# 12. A Matlab wrapper for Python PACE projects

Date: 2021-Jan-01

## Status

Proposed


## Context

Both Euphonic and Brille are PACE projects with primarily a Python interface.
PACE, however, aims to provide both a Python and a Matlab interface to users,
and also to foster inter-operability between projects which are written both in Matlab and Python.
In particular, `pyHorace` ([prototype](https://github.com/mducle/hugo)) cannot use the 
[standard method](https://uk.mathworks.com/help/matlab/call-python-libraries.html) for Matlab to run Python code, 
where calls to Python from Matlab are prefixed with `py.` followed by the full module specification.
For example, `r = py.numpy.random.rand(3)` uses `numpy` to generate a random number.
This is because such a call causes Matlab to 
[automatically spawn](https://uk.mathworks.com/help/matlab/ref/pyenv.html) a dependent Python interpreter,
which can be either created within the same process as the Matlab interpreter (`InProcess`)
or in an external process (`OutOfProcess`).
`pyHorace` already runs within a Python interpreter and the compiled Matlab library *must* be loaded in-process.
Thus, if Matlab spawns a second Python intepreter with the default `InProcess` execution mode,
the two Python interpreters will conflict causing memory errors and a crash.
We can force Matlab to launch the dependent Python interpreter `OutOfProcess`
but this imposes a significant performance penalty
(extensive testing was not done but Brille+SpinW runs about 10x slower than with `InProcess`). 


## Proposal

So, we propose that the Matlab interface to Euphonic and Brille would be through a Python wrapper class.
There would be two implementation of this class.
One (used by Matlab users) would call to `py.*` internally, whilst the other
(used by `pyHorace`) would use the mechanism described in the [python interface design](../../python_interface/design).
Most importantly, no Matlab code which would be compiled would have reference to `py.*`
which would cause a crash in `pyHorace`.

An important benefit of this Python wrapper class is that mimimal Matlab code would be needed
to expose Euphonic or Brille (or indeed any other Python program) to Matlab.
The [proposed wrapper](https://github.com/mducle/horace-euphonic-interface/blob/light_wrapper/%2Beuphonic/light_python_wrapper.m)
also handles data conversion and translation between Python and Matlab keyword arguments and some error checking.
Finally, the wrapper also exposes the `pydoc` documentation system
allowing users in Matlab to access the Python documentation transparently,
and to use tab-completion to access the properties and methods of the Python class or object.

To make it flexible (to allow for example the Euphonic Matlab interface to be more easily distributed on the File-Exchange),
we propose to make this Python wrapper class a separate github repository which is either included as a submodule
or purely in the build system (e.g. a cmake external project).


## Decision

A decision will be taken at a forthcoming meeting.


## Consequences

The current [`horace-euphonic-interface`](https://github.com/pace-neutrons/horace-euphonic-interface/) and
[`brillem`](https://github.com/brille/brillem/) code would need to be refactored to use the wrapper,
with open pull requests [for Euphonic](https://github.com/pace-neutrons/horace-euphonic-interface/pull/3)
and [brillem](https://github.com/brille/brillem/pull/4).
