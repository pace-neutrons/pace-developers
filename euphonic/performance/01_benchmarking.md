# Euphonic Performance Benchmarking

Euphonic's performance needs to be benchmarked for 3 main reasons:

1. To ensure its performance is competitive compared with other software that
performs similar computations (to ensure Euphonic has added value)
2. To ensure its performance is good enough to meet the requirements of PACE
3. To ensure its performance doesn't degrade over time

## 1. Comparison With Other Software

There are many pieces of software that perform parts of Euphonic's computation
(either interpolation or structure factor calculations) but there aren't
any<sup>[1](#1)</sup> that can perform the full pipeline of calculations, and
most of these aren't in Python so it may be hard to get a direct comparison. It
needs to be decided:

<a name="1">[1]</a> *Phonopy can interpolate, and has a structure factor
calculation, but the structure factor calculation is currently under testing*

### 1.1 Which software to benchmark against
Possibilities include:
 * CASTEP phonons tool interpolation against Euphonic interpolation
 * OClimax structure factor calculation against Euphonic's. OClimax can only be
 run in a Docker container so it may not be possible to get a fair comparison
 as we probably can't run on SCARF
 * Ab2tds structure factor calculation against Euphonic's. Ab2td's calculation
 must be done in multiple steps and stored in intermediate files (e.g. symmetry
 construction, Debye-Waller factor) so it may not be possible to get a fair
 comparison
 * Phonopy interpolation (and structure factor calculation?) compared with
 Euphonic

### 1.2 Which timing/benchmarking tools will be used in each case
How can we directly compare timing results with Euphonic? This depends on the
software being benchmarked. If in Python this should be fairly simple and the
tools available include:
 * timeit: simple and built-in, but need to manually time each part that you
 want to profile output it to a file
 * cProfile: built-in and automatically outputs to a file, but that file
 includes every function call so could be hard to parse, and is probably not
 suited to benchmarking
 * line_profiler: outputs a file with line-by-line timings of each function, you
 need to specifically add a decorator to whatever function you want to time
 * profilehooks: has both a profiling and timing option. Again need to add a
 decorator to each function and it can summarise results which can then be
 output to a file

For timing other tools on the CL the obvious choice would be Linux's `time`. But
how do we gather these results and is there anyting better out there?

### 1.3 Which cuts/q-points will be used for benchmarking
If we want to benchmark against Ab2tds/OClimax they would need to be cuts in a
single direction in Q (we could use Q-Q cuts for OClimax). Are the cuts we're
using for validation big enough? 

For CASTEP phonons/Phonopy benchmarking we could use a set of random q-points,
or would a 'fair' comparison use a regular grid to allow CASTEP/Phonopy to use
symmetry? How many q-points should we use? This will probably be limited by
.phonon file size.

### 1.4 Where benchmarking results will be stored
The benchmarking results themselves will be relatively small, so could be stored
in a Github repo in pace-neutrons (perhaps in the same repo as the validation
results). Any large files e.g. cuts may be likely to overlap with validation
cuts and can be stored on the SAN file server

## 2. Performance For PACE
This will require testing the whole pipeline `Horace -> (Brille?) -> Euphonic`.
This could form part of the testing framework for the Horace/Euphonic interface
e.g. short tests being run on each commit to Horace/Euphonic, and larger
performance tests being run once a week using cuts from the SAN storage.

Questions still to be answered:
* Where should the Euphonic Horace simulation function and its tests go? In a
separate repo? Inside Horace?
* What systems do we want to run the performance tests on? Is SCARF enough?
* What timing tools will we use? Matlab's timeit? Or is Jenkins job execution
time enough?


## 3. Euphonic Performance Over Time
To ensure Euphonic's performance is maintained or improves over time, a large
job interpolating tens of thousands of q-points could be run regularly
(e.g. once a week) as a performance test. This could be run on SCARF and compare
the pure Python with the C version, and different numbers of cores.

Would Jenkins job execution time be enough? If we want 'publishable' results
which tools do we use for timing (see 1.2 above) and how to we compare to other
software?