# PACE framework


## Introduction

PACE comprises several independent programs which may interact with each other.
This document defines how each program is expected to call the others, and especially the interfacing layers between the programs.

The main PACE programs considered here are:

* [Horace](https://github.com/pace-neutrons/Horace)
    - This is the combined Horace and Herbert distribution
* [Euphonic](https://github.com/pace-neutrons/euphonic)
* [Brille](https://github.com/brille/brille)
* [SpinW](https://github.com/spinw/spinw)

These programs are generally not dependent on each other, except for some limited functionalities, which are:

1. Horace calling Euphonic or SpinW to calculate INS spectra.
    - This uses the Horace [third-party API](../../optimisation/design/Third_Party_API_Design.md)
2. Euphonic or SpinW calling Brille.
    - This is done internally within Euphonic or SpinW to call Brille directly.

An additional complication is that Horace and SpinW are Matlab programs whilst Euphonic and Brille are Python modules.
Despite this, amongst the core aims of the PACE project are that:

* Users must be able to run all these programs from *either* Matlab *or* Python. 
* Users must be able to model spectra in Horace using the following as computation engines:
    - Euphonic, alone or in conjunction with Brille.
    - SpinW, alone or in conjunction with Brille.


## Horace calling Euphonic or SpinW

The [Horace third-party API](../../optimisation/design/Third_Party_API_Design.md)
essentially requires a model *function* that accepts the q-vector (`hkl`) coordinates as input
and returns either a list (cell array) of mode energies and intensities or intensity at a give q-vector and energy.
That is either one of:

```matlab
[energies, intensities] = disp_fun(qh, qk, ql, parameters, args);
sqw = sqw_fun(qh, qk, ql, energy, parameters, args);
```

where `qh`, `qk`, `ql` and `energy` are vectors of equal length, `parameters` is a vector, and `args` is a cell array.
`energies` and `intensities` are cell arrays with `n_mode` elements, each element is a vector the same size as `qh` etc.
`sqw` is a vector the same size as `qh`.

**The sole purpose of the `euphonic_horace` program is to provide this model function for Horace to use Euphonic.**
It must be written in Python in order to allow both Python and Matlab users to run the combination of Horace + Euphonic.
This is due to restrictions on calling Python from Matlab using a compiled Matlab module.
`euphonic_horace` provides a class `CoherentCrystal` which wraps the necessary Euphonic classes
(`ForceConstants`, `DebyeWaller` and `QPointPhononModes`) and provides a `horace_disp` function as a class method.
There is [debate](#euphonic_horace) as to whether this is necessary as a separate program (see below).

The equivalent functionality for SpinW is included in the SpinW codebase itself, in the form of the `horace_sqw` method.


## SpinW or Euphonic calling Brille

[ADR #9](../adr/0009-brille-integration.md) decided that integration of Euphonic or SpinW with Brille
should be done within the Euphonic or SpinW codebase themselves rather than through an interface program.
In both cases it involves constructing a `BrillouinZone` object and then a q-point interpolation grid from this.
The `interpolate_at()` or `ir_interpolate_at()` methods of the grid are then used for interpolation.
The `create_bz()` and `create_grid()` Python functions which are part of `brillem`
makes the `BrillouinZone` and grid construction easier.


## Interface layers for Matlab users to run Python

Matlab has a built-in facility to run Python programs.
Thus users can run Euphonic or Brille (which are Python modules) directly as long as they have those and Python installed.
The syntax is quite longwinded, however,
so the aim of the `euphonic_matlab` and `brillem` programs is to provide an *easy* interface
for Matlab users to run Euphonic and Brille.

Both programs use the `light_python_wrapper` library which is an abstract base class
providing a Matlab object-oriented ("dot-notation") syntax to Python classes.

In addition to generic class wrapping, `euphonic_matlab` explicitly defines wrappers
for the `ForceConstants` and `CoherentCrystal` Python classes (with the same Matlab name).

`brillem` serves the same functionality for Matlab users to run Brille,
and also for SpinW to run Brille.
`brillem` includes both Python and Matlab code.
The Python code wraps the different grid classes and constructors into a single Python class
[as described above](#spinw-or-euphonic-calling-brille).
The Matlab code is a light wrapper providing a more Matlab-like syntax.
**The SpinW-Brille interface explicitly uses `brillem` and will not work without it installed.**


## Interface layers for Python users to run Matlab

The `pace-python` distribution is a Python module of compiled Matlab versions of Horace, Herbert and SpinW
together with interface code which allows a very similar syntax to Matlab for Python users.
In addition, `pace-python` currently also packages the Python part of `brillem`
(it cannot use the Matlab part of `brillem`).


## Call-graph

![PACE project call-graph](diagrams/pace_framework.svg)

The above diagram shows the call graphs between the PACE and interface programs.
Arrows point from the caller to the callee (e.g. Horace calls `euphonic_matlab`),
and the text beside the lines indicate the called function or method.
Purple background indicates major PACE packages.

The code is organised such that each (yellow-background) file in the graph is a separate git repository,
except for the "compiled" versions included in `pace-python` which are all in a single
[repository](https://github.com/pace-neutrons/pace-python/).


## `euphonic_horace`

The `euphonic_horace` module is thought to be a little superfluous and it has been proposed to remove it.
This could be done in a few different ways:

* Remove `euphonic_horace`, splitting and duplicating the code in  `pace-python` and Horace.
    - Pro: one less package which can confuse users, and perhaps simplify the integration pipeline.
    - Con: code duplication
    - Con: Horace is a large program with a long test time, changes to the Euphonic interface would require more developer effort 
      than in a separate repository.
* Remove `euphonic_horace`, putting the code into `euphonic_matlab`.
    - Pro: one less package which can confuse users, and perhaps simplify the integration pipeline.
    - Con: `euphonic_matlab` would have both Python and Matlab code and needs two different versions for each language.
        + git allows only a single version tag so would need to enfore a mechanism where Matlab code changes
          would change the subminor version number whilst Python code changes increment the minor or major version number.
    - Con: `pace-python` would download the `euphonic_matlab` package and extract the Python code (it does not need the Matlab code).
        + makes the build script slightly more complex (but not much).
* Remove `euphonic_horace`, moving the current Python code into `pace-python` and resurrect/reimplement a Matlab equivalent in `euphonic_matlab`.
    - Pro: one less package which can confuse users, and perhaps simplify the integration pipeline.
    - Con: code duplication (have different Python and Matlab implementations of the same functionality)
    

## Naming

Some project names, particularly `pace-python`, `euphonic_horace` and `euphonic_matlab` are thought to be lacking.
Some suggested alternatives are:

* For `pace-python`: `snakeskin`, `pacy`, `pace-neutron`
* For `euphonic_horace`: `euphonic_horace_interface_python`, `euphonic_sqw`, `euphonic_horace_driver`
* For `euphonic_matlab`: `euphonic_horace_interface_matlab`, `euphonium`, `meuphonic`

Added Nov 2021: It was decided to leave the naming unchanged. That is

* `euphonic_matlab` is still [`horace-euphonic-interface`](https://github.com/pace-neutrons/horace-euphonic-interface/).
  This is because it is registered in the
  [Matlab File Exchange](https://uk.mathworks.com/matlabcentral/fileexchange/83758-horace-euphonic-interface) under that name.
* `euphonic_horace` is named [`euphonic_sqw_models`](https://github.com/pace-neutrons/euphonic_sqw_models/) with the
  intention that a powder S(Q,w) model will be added in future to the existing `CoherentCrystal` model.
