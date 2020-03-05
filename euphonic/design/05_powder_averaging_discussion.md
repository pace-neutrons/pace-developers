# Powder averaging

These notes were initially drawn up by Adam Jackson. They were
discussed and developed in a meeting on 5/3/20 with Greg Tucker, Duc
Le, Keith Refson and Rebecca Fair.

# Table of Contents

1.  [PACE project issues](#github-issues)
2.  [Background](#org0814430)
3.  [Analytic method](#org7f363ce)
4.  [Numerical methods](#orgfd3e1f7)
    1.  [Premise](#org8788f90)
    2.  [Questions](#orgee1b867)
    3.  [Existing approaches](#org72cee07)
        1.  [Random sampling](#orgce0cfe3)
        2.  [Spherical sampling](#orgd1b667c)
        3.  [Unknown](#org93896a1)
5.  [Observations](#orgf40d9b1)
6.  [Going forward](#orgcc884e6)


<a id="github-issues"></a>
# Related Issue pages

-   [#25 Euphonic Calculations: Powder averaging library](https://github.com/pace-neutrons/Pace-Project-Plan/issues/25)
    - The Issue directly leading to this discussion
-   Incoherent analytic overtones <https://github.com/pace-neutrons/Pace-Project-Plan/issues/24>


<a id="org0814430"></a>

# Background

-   Single-crystal samples are typical on MAPS
-   Powdered crystalline samples are required on MARI
-   Weakly-bound polycrystalline/liquid (cooled from liquid/gas?)
    samples are typical on TOSCA (especially hydrogenous)
-   There are many exceptions to these, so versatility is useful

-   Currently Euphonic computes
    -   4-D S(**q**,ω)
    -   for coherent scattering in a single crystal
    -   from force constants
-   Currently Abins computes
    -   1-D S(q,ω) per atom (along a fixed q,ω relationship)
    -   for the incoherent spectrum of an isotropic material
    -   from a set of frequencies and wavevectors


<a id="org7f363ce"></a>

# Analytic method

-   Key references include Waddington (1982), Warner(1983), Tomkinson
    (1984), Mitchell (2005)

-   Fundamental spectrum: S = Q<sup>2</sup> / 3 Tr(B) exp(-Q<sup>2</sup> / a); a = 1/5(Tr(A) + 2(B:A)/Tr(B))
    -   Uses B (mode displacement) and A (sum over all mode displacements)
    -   Isotropic approximation -> use of traces, contraction (:), factor 1/3
    -   Incoherent approximation -> each atom's movement contributes independently
    -   Modified (more complex) expressions for higher-order terms
        -   (Proving difficult to track down actually&#x2026;)


<a id="orgfd3e1f7"></a>

# Numerical methods


<a id="org8788f90"></a>

## Premise

-   Consider Euphonic as a black box that calculates contributions to
    crystalline 4-D S(**q**,ω) for given set of (**q**,ω)
-   To reduce to a 2-D S(q,ω), we can "flatten" a 4-D sampling to
    q=abs(**q**)
    -   This removes orientational information while sampling beyond a
        single high-symmetry line in BZ


<a id="orgee1b867"></a>

## Questions

-   How do we correctly weight the samples to obtain the S(q,ω)
    corresponding to a powder experiment?
    -   simple averaging is fine for regular shells

-   How do we sample the space to ensure that all of 4-D space is
    included in the results (avoiding "blind spots")?
    -   use a lot of points
    -   consider topology/features of the space

-   How can we do this efficiently?
    -   symmetry!
    -   work in irreducible wedge
    -   re-use computed frequency/qpts in extended zone scheme

-   How can we check the convergence? Is a "fire-and-forget"
    approach feasible?
    -   get a baseline method in place and then experiment from there,
        rather than designing everything in theory first

-   Is the same sampling mesh suitable for the **A** matrix used in
    Debye-Waller calculation, or should this be a separate q-mesh?

-   What about sampling statistics; propogation of error
    approach. Uncertainty estimates?
    -   experimentally we can compare different detector contributions
        to the same bin


<a id="org72cee07"></a>

## Existing approaches


<a id="orgce0cfe3"></a>

### Random sampling

-   Mentioned in PACE meetings. How much has this been used?
-   Has natural advantage of being uniform in space&#x2026; eventually.
-   Sample (**q**,ω) randomly, or sample **q** randomly and search ω at
    each **q**?


<a id="orgd1b667c"></a>

### Spherical sampling

-   SpinW seems to use a Fibonacci-related method for uniform
    sampling at spherical surfaces
    -   points per shell has to be a Fibonacci number
    -   or can sample *randomly* at *each* spherical shell
-   MDANSE requires the user to set up a q lattice for sampling,
    including a "spherical grid" option with a set range of "shells"
    and "vectors".


<a id="org93896a1"></a>

### Unknown

-   In OCLIMAX, TASK=1 allegedly performs a "full powder
    calculation" with coherent effects (as opposed to analytic
    inhoherent method). This is not affected by the user q-bin
    options, and neither manual nor paper gives any information
    about the sampling approach.


<a id="orgf40d9b1"></a>

# Observations

-   There are two different possible objectives here: uniform
    sampling **at each q** and uniform sampling **over the spherical volume**
-   Why do we pre-determing the mod(q) bins?
    -   easier to compare with instrument
    -   able to check convergence *at each bin*

-   Do we need to include a resolution function before/during powder
    averaging?
    -   Ideally would build simulated output from every simulated pixel
        of the instrument. This doesn't seem feasible for instruments
        with 000s of detectors (e.g. MERLIN)
    -   Different instrument models need to apply function at different
        stages
    -   McVine accounts for instrument design, but takes S(q,ω) as
        input; no support for 4-D data.


<a id="orgcc884e6"></a>

# Going forward

-   No complex interaction with 1D
-   Smart integration in 4-D space could be profitable due to features of space (peaked)
-   But we still want simple numerical sampling so progress that
    -   fibonacci sampling and random sampling on spheres both have some appeal
        -   should be able to mostly share infrastructure
-   Uniform sampling in 4-D space doesn't map well to PACE
-   Uniform sampling in 3-D space less attractive than spherical
    approach at this stage; harder to reason, inspect, converge
    -   resampling awkward from shells; can only make bins bigger!
-   Worth investigate <span class="underline">how</span> to weight non-shell schemes
-   aliasing is scary (sampling a periodic space with a regular sequence)

