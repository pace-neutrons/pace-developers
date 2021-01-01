[<-previous](0011-use-mex-for-pyHorace-python-calls.md) | [next->]()

# 12. A Matlab wrapper for Python PACE projects

Date: 2021-Jan-01

## Status

Proposed


## Context

Both Euphonic and Brille are PACE projects with primarily a Python interface.
PACE, however, aims to provide both a Python and a Matlab interface to users,
and also to foster inter-operability between projects which are written both in Matlab and Python.
In particular, `pyHorace` ([prototype](https://github.com/mducle/hugo)), cannot use the standard
method for Matlab to run Python code, using the `py.*` namespace.


## Proposal

Thus it is proposed that the Matlab interface to Euphonic and Brille would be through a Python wrapper class.
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
