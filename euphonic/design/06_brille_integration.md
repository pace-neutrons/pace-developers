# Brille-Euphonic Integration

## Context

[Brille](https://github.com/brille/brille) is a library for symmetry operations
and linear interpolation within an irreducible part of the first Brillouin
zone. In the context of Euphonic it means that it can be used to linearly
interpolate phonon eigenvalues/vectors to calculate them more quickly. There
are 2 ways in which this could work. One is where Brille calls Euphonic, which
means it can be used for Horace cuts, and Euphonic doesn't get any added
complexity, but also means Euphonic standalone users don't get any of the
benefits. The other option is that Euphonic calls Brille, this would require
changes to Euphonic but would allow faster interpolation for both Horace and
Euphonic standalone users. However, these options are not necessarily exclusive
and it's possible that both could be implemented.

The purpose of this document is to assess the benefits and drawbacks of these
options and define any desired syntax, which will hopefully reveal any
potential issues. This document should also be considered in the context of
what the Brille-SpinW interface will look like, as it would be beneficial to
Horace users if they were somewhat similar.

### General Note on Syntax

There are two options for the syntax, one is to  try to keep the commands as
specific as possible so each command has fewer arguments and it is clearer what
they do. This has the benefit of reducing the chance of name clashes, making
arguments easier to manage and easier for the user to input. However, this will
generally lead to the user having to write more code as they will need one line
for reading force constants, one line for setting up Brille's grid, one line
for computing the lookup table etc. and could get very verbose. The other
option is to try to have as few calls as possible and try to encapsulate all
the options in arguments to one or two functions. This would be easy for a user
who is happy with default arguments, but could become very complicated as
more arguments and features are added (e.g. powder averaging).

## Calling Euphonic from Brille

### Use Case 1: Simulating Horace cuts
This would involve using Horace's simulation functions to call Brillem (which
calls BrillEu, which calls Brille and Euphonic).

**Example Syntax**

This syntax tries to keep the Brille/Euphonic arguments deliberate and
separate, however it could be confusing for some users (nested cell arrays)
and some settings you may want to apply for both Brille and Euphonic rather
than having to set them separately (e.g. if you want to use 4 threads in
Euphonic to create the lookup table, you probably also want to use 4 threads in
Brille to linearly interpolate the eigenvalues/vectors). In addition, with the
current Horace simulation functions the syntax splits arguments up into 'model
parameters' for fitting and 'extra parameters' for constant arguments. For now
I've made an example with the scaling factor as a fitting parameter.

```matlab
brille_init_args = {'grid', 'mesh'
                    'max_points', 10000,
                    'parallel', true};
euphonic_init_args = {'model_args', {'quartz.castep_bin'},
                      'interpolate_kwargs', {'asr', 'reciprocal',
                                             'use_c', true,
                                             'n_threads', 4}};

% This command needs to capture arguments for reading the force constants,
% setting Brille's grid, and interpolating phonons in Euphonic. I've tried
% to separate the Brille and Euphonic arguments, but actually do users need to
% know the distinction?
breu = brillem.Euphonic('brille_args', brille_init_args,
                        'euphonic_args', euphonic_init_args);


fit_params = [1.0]; % scale
pars = {fit_params,
        'interpolate_kwargs', {'threads', 4},
        'debye_waller_grid', [6,6,6],
        'temperature', 300.0,
        'conversion_mat', [1,0,0; 0,1,0; 0,0,-1], % Convert Horace Q -> Euphonic Q
        'chunk', 10000};

% This command needs to capture arguments for the structure factor calculation,
% and any Horace-specific arguments (e.g. calculation chunking, converting 
% Q-point coordinates)
sim_cut = disp2sqw_eval(exp_cut, @breu.horace_sqw, pars, fwhh);
```

**Advantages:**
 - Interface could be potentially similar to Brille-SpinW's - this would be
   easier for users to understand from horace side of things
 - This would be easier from standalone Euphonic's point of view, it doesn't
   need to know anything about Brille, but it also doesn't get any of the
   benefits of faster interpolation/use of symmetry

**Disadvantages:**
 - Have to handle arguments for 2 different codes at once - Brille and
   Euphonic, keeping these up-to-date and avoiding name clashes and ugly
   syntax could be difficult. This gets even more complicated when adding
   powders. 
 - Use of Brille would be overkill for simple cuts - having to initialise a
   Brille object when they only want to use Euphonic seems strange. To get
   around this Euphonic would have to provide its own Horace interface (there
   is already a version [here](https://horace-euphonic-interface.readthedocs.io/en/latest/))
   but do we really want to maintain 2 interfaces to Horace?
 - In the current implementation of this there is some repetition of code to
   enable Brille to wrap a lot of Euphonic's functions, and get the additional
   symmetry information it needs. I'm not sure if this can be avoided for the 
   'calling Euphonic from Brille' case.


## Calling Brille from Euphonic

### Use case 1: Brille 'Force Constants' for Faster Interpolation

This would involve adding another object to Euphonic, for now I'll call it
`BrilleForceConstants` (although a better name might be needed) which would act
like `ForceConstants`, but would perform linear instead of Fourier
interpolation. To make the most of this the current `ForceConstants` in
Euphonic might have to be updated to enable direct calculation of structure
factors, debye waller etc. from `ForceConstants` (without intermediate
eigenvectors), although this might not be required if calculations are
appropriately chunked. Another update to make this integration easier would be
adding symmetry information to Euphonic's `Crystal` object (so that Brille
doesn't need to find it itself).

**Example Syntax**

From Python:

```python
from euphonic import ureg, ForceConstants
from euphonic.util import mp_grid

fc = ForceConstants.from_castep('quartz.castep_bin')

# Create BrilleForceConstants object
interpolate_kwargs = {'use_c': True, 'n_threads': 4, 'asr': 'reciprocal'}
bfc = fc.calculate_brille_force_constants(
    grid='mesh', max_points=10000, **interpolate_kwargs)

# Create DebyeWaller
dw_phonons = bfc.calculate_qpoint_phonon_modes(mp_grid([6,6,6]))
dw = dw_phonons.calculate_debye_waller(temperature=300*ureg('K'))

# Calculate StructureFactor
phonons = bfc.calculate_qpoint_phonon_modes(qpts, n_threads=4)
sf = phonons.calculate_structure_factor(dw)
```

From Matlab:

The question here is whether the interface should be 'Horace-like' with bespoke
functions to make it easier to simulate cuts, or whether it should more closely
mirror Euphonic's Python interface. The following example is somewhere
inbetween and assumes a Matlab wrapper has been written (named 'meuphonic').

```matlab
% Create ForceConstants and BrilleForceConstants using Euphonic-like syntax
fc = meuphonic.ForceConstants.from_castep('quartz.castep_bin');
kwargs = {'use_c', true, 'n_threads', 4};
bfc = fc.calculate_brille_force_constants( ...
    'grid', 'mesh', 'max_points', 10000, 'interpolate_kwargs', kwargs);

fit_params = [1.0]; % temperature, scale
pars = {fit_params,
        'force_constants', bfc,  % accepts fc or bfc
        'interpolate_kwargs', {'threads', 4}, % different depending on fc or bfc
        'debye_waller_grid', [6,6,6],
        'temperature', 300.0,
        'conversion_mat', [1,0,0; 0,1,0; 0,0,-1], % Convert Horace Q -> Euphonic Q
        'chunk', 10000};
sim_cut = disp2sqw_eval(exp_cut, @meuphonic.horace_sqw, pars, fwhh);
```

**Advantages:**
 - Would benefit both Horace and Euphonic users
 - Allows Horace users to skip a step depending on if they want to use brille
   or not

**Disadvantages:**
 - Would require additions to Euphonic's ForceConstants, and quite a few
   changes to Brille's existing repos before this option is feasible
 - The interface could end up being quite different to SpinW (does this
   matter?)

### Use case 2: Brille Q-point Mesh for BZ Integration
This would involve using Brille to produce a mesh of q-points and their weights
which Euphonic could use for Brillouin Zone integration (instead of naively
generating a Monkhorst-Pack grid using `mp_grid` as in previous examples, which
makes no use of symmetry). This is a much 'lighter' use of Brille and should in
theory be easy to implement. However, libraries that Euphonic already depends
on such as `spglib` can already generate weighted q-point Monkhorst-Pack grids,
so is there actually much to be gained from having a 'smarter' mesh generated
by Brille?

**Advantages:**
- Would be easy and quick to implement

**Disadvantages:**
- Would it be worth adding a dependency on Brille for what could be a small
  gain?

## Decision

Largely motivated by the ability to use Brille to improve the performance of
powder simulations from Python, it has been decided to call Brille from Euphonic.
(As of 05/05/22) Brille has been specified as an optional dependency, so it
would not affect other Euphonic users. Also, the `BrilleForceConstants` (now
named `BrilleInterpolator`) can be instead created with
`BrilleInterpolator.from_force_constants` syntax, so no changes to the current
`ForceConstants` class are required. The relevant PR for Euphonic is
[PR#104](https://github.com/pace-neutrons/Euphonic/pull/104).