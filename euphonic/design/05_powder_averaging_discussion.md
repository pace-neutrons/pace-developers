# Powder averaging

These notes were initially drawn up by Adam Jackson. They were
discussed and developed in a meeting on 5/3/20 with Greg Tucker, Duc
Le, Keith Refson and Rebecca Fair.
Further revisions were made by AJJ and reviewed via GitHub PR.

In this document **q** refers to a 3-dimensional momentum transfer
vector, while *q* refers to "mod q", a scalar value of momentum
transfer.

# Table of Contents

1.  [Related Issue pages](#github-issues)
2.  [Background](#org0814430)
3.  [Analytic method](#org7f363ce)
4.  [Numerical methods](#orgfd3e1f7)
    1.  [Premise](#org8788f90)
    2.  [Questions](#orgee1b867)
    3.  [Existing approaches](#org72cee07)
        1.  [Random sampling](#orgce0cfe3)
        2.  [Spherical sampling](#orgd1b667c)
        3.  [Unknown](#org93896a1)
5.  [Further questions](#orgf40d9b1)
6.  [Going forward](#orgcc884e6)


<a id="github-issues"></a>
# Related Issue pages

-   [#25 Euphonic Calculations: Powder averaging library](https://github.com/pace-neutrons/Pace-Project-Plan/issues/25)
    - The Issue directly leading to this discussion

- [#24 Euphonic Calculations: Overtones and Combinations (incoherent semi-analytic)](https://github.com/pace-neutrons/Pace-Project-Plan/issues/24)
  - Higher-level issue for implementation of CLIMAX-like analytic powder averaging
  - Leads to #67 (implementation in Euphonic) and #68 (refactoring Abins to use Euphonic)

<a id="org0814430"></a>

# Background

Powder averaging is appropriate to simulation of many neutron instrument measurements

-   Single-crystal samples are typical on MAPS, but powder measurements are also performed
-   Powdered crystalline samples are required on MARI
-   Weakly-bound polycrystalline/liquid (cooled from liquid/gas?)
    samples are typical on TOSCA. (Generally these are hydrogenous,
    leading to spectra dominated by incoherent scattering.)
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

-   This established method lacks a good consistent name. A complete
    name would be something like "analytic powder-averaging in the
    almost-anisotropic inherent-scattering approximation."

-   Fundamental spectrum:

    S<sub>i,k</sub> = Q<sup>2</sup> / 3 Tr(**B**) exp(-Q<sup>2</sup> / a);

    where a = 1/5(Tr(**A**) + 2(**B:A**)/Tr(**B**))

    -   Uses **B** (mode displacement) and **A** (sum over all mode displacements)
    -   Isotropic approximation -> use of traces, contraction (:), factor 1/3 for orientional average
    -   Incoherent approximation -> each atom's movement contributes independently
    -   Modified (more complex) expressions for higher-order terms
        -   (The derivations for these are difficult to track down
            which is creating difficulties for Abins)

-   Key references include Waddington (1982), Warner(1982), Tomkinson
    (1984), Mitchell (2005)
-   Key existing implementations include a-CLIMAX, Abins and OCLIMAX
    - Of these, only OCLIMAX currently provides a numerical method for
      comparison. It is quite possible that this method is applied
      inappropriately for simulation of some materials on TOSCA-like
      instruments.

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

## Design questions

### How do we correctly weight the samples to obtain the S(q,ω) corresponding to a powder experiment?

-   When sampling a regular sequence of spherical shells, it seems sufficient to average over the points taken at each *q*.
-   If our samples are placed arbitrarily in space, it is less obvious how to determine these weights

### How do we sample the space to ensure that all of 4-D space is included in the results (avoiding "blind spots")?
-   This is a known problem and is solved by sampling a lot of points
-   Consider the topology/features of the space; there are more
    features intersecting a spherical shell at large *q* than a
    smaller shell at low *q*. This implies that a greater number of
    samples is needed as we go further out in *q*.

### How can we do this efficiently?

-   Use symmetry!
    - The irreducible wedge of the Brillouin zone can be
      drastically smaller than the full space while containing all
      the unique information.
    - Don't try too hard to make origin shifts that squeeze a bit
      more efficiency from symmetry operations; these benefits
      diminish as the number of samples increases.
-   Use caching
    - The *q*-range in INS measurements passes through many cells
      of the reciprocal lattice. If possible, re-use computed
      frequency/qpts in extended zone scheme.
    - Brille solves some of these problems by transparently
      re-using appropriate data.
    - Would be nice to intentionally select long-range *q-points*
      that already have calculated frequencies so that only S
      needs recalculating. This might not be commensurate with the
      desired *q* bins, however.

### How can we check the convergence? Is a "fire-and-forget" approach feasible?

- This could be a substantial project in its own right. To progress
  the project we should get a baseline method in place and then
  experiment from there, rather than designing everything in theory
  first.
- Fundamentally the goal of the sampling exercise is to perform a
  numerical integration. In the numerical methods field there has been
  a lot of work on integration problems, including methods which use
  adaptive step sizes to obtain a consistent uncertainty when
  integrating arbitrarily complex functions.
- This function is not arbitrary and there should be some useful
  information lurking in the force constants data.


### Is the same sampling mesh suitable for the **A** matrix used in Debye-Waller calculation, or should this be a separate q-mesh?

- This point was not discussed in the meeting. It's worth observing
  that DW should only need sampling within a single Brillouin zone,
  while S reaches out further in reciprocal space. We'll probably stick with
  Monkhorst-Pack grids initially.


### Can we use statistical methods to quantify uncertainty in the convergence?

- Statistical methods, propogation of error approaches could provide
  some useful tools
- Experimentally we can examine uncertainty by comparing different
  detector contributions to the same abs(q) bin
  - e.g. different &phi; contributions from TOSCA's ring of detectors.
  - It is _possible_ to collect multiple measurements at same **q**
    but requires runs at multiple incident energies.
- We should be able to somehow examine the changing variance in S as more
  **q**-points are sampled.

<a id="org72cee07"></a>

## Existing approaches


<a id="orgce0cfe3"></a>

### Random sampling

-   This has been mentioned in PACE meetings. How much has it been
    used?
    - Random sampling on spherical shells seems more common that fully
      random sampling in **q**-space.
-   Has natural advantage of being uniform in space... eventually.
-   Convergence can be examined systematically, adding new points
    without removing old ones. A smoother process than replacing
    entire sampling meshes with different criteria.
-   Strictly we can sample (**q**,ω) randomly, *or* sample **q** randomly and search ω systematically at
    each **q**.
    - The former approach is applicable to codes like MDANSE that
      sample S(**q**,ω) in a response formalism from dynamic data.
    - The latter approach maps better to PACE; at each **q** we go to
      the force constants and get all the active ω. This has the
      advantage that every sample should find some signal, without the
      risk of hitting "empty space".


<a id="orgd1b667c"></a>

### Spherical sampling

-   SpinW seems to use a Fibonacci-related method for uniform
    sampling at spherical surfaces
    -   points per shell has to be a Fibonacci number
        - That's not a deal-breaker but could be annoying when exploring convergence
    -   or can sample *randomly* at *each* spherical shell surface
-   MDANSE requires the user to set up a q lattice for sampling,
    including a "spherical grid" option with a set range of "shells"
    and "vectors".
-   Another approach that doesn't seem to be in use but is perhaps
    a truer estimate of the integral is to sample _within a q bin_
    rather than exactly at the surface.


<a id="org93896a1"></a>

### Unknown

-   In OCLIMAX, TASK=1 allegedly performs a "full powder
    calculation" with coherent effects (as opposed to analytic
    inhoherent method). This is not affected by the user q-bin
    options, and neither manual nor paper gives any information
    about the sampling approach.


<a id="orgf40d9b1"></a>

# Further questions

-   There are two different possible objectives here: uniform sampling
    **at each q** and uniform sampling **over the spherical
    volume**. Which is more important?

-   Why do we pre-determine the mod(q) bins?
    -   easier to compare with instrument
    -   able to check convergence *at each bin* independently
    -   in Abins, the simulated *q* bins do not match the TOSCA
        instrument measurements, in which the bin size increases with
        *q*.
    -   With random/uniform q-sampling, we could re-sample to
        arbitrary/inconsistent q-bin sizes. This will need dense
        sampling relative to bin size.

-   Do we need to include a resolution function before/during powder
    averaging?
    -   Different instrument models need to apply resolution functions at different
        stages; it depends how the function was developed.
        -   As long as the powder-averaging functions accept/return
            appropriate Euphonic data types, we shouldn't need to make
            special allowances at this stage. This can be experimented
            with if/when new resolution function models are developed.

    -   Ideally one would build a combined output from every simulated pixel
        of the instrument. This doesn't seem feasible for instruments
        with thousands of detectors (e.g. MERLIN)
        -   This approach seems to map to the McVine package's goals
            better than Horace/Euphonic.
        -   McVine accounts for instrument design, but takes S(q,ω) as
            input; no support for 4-D data, which could be needed for such a model.
        -   The McVine package is somewhat intimidating; such work is
            not to be taken lightly.


<a id="orgcc884e6"></a>

# Going forward

-   We have not identified any complex interactions between with the
    analytic incoherent powder averaging and more general numerical
    methods; these are separate pieces of code using some of the same
    Euphonic data structures.
-   Intelligent methods could be developed for accurate integration in 4-D space, due to many-peaked nature of phonon band structure.
-   We would still want simple numerical sampling, which is quicker to
    develop/implement, so should begin by progressing that.
    -   No strong preference was identified between Fibonacci sampling and random sampling on spheres; both have some appeal/merits
    -   As they should be able to mostly share infrastructure, it is realistic to implement both.
-   Uniform sampling in 4-D space doesn't map well to PACE and can be disregarded
-   Uniform sampling in 3-D space (i.e. sampling values of **q** and obtaining all energy bands at those points) is less attractive than the spherical shell approach at this stage; harder to reason, inspect, converge
    - There is one significant advantage to this approach which is that it is possible to re-bin *q* after calculating the data. When working with regularly-spaced shells, one can only make the bins bigger!
    - We don't know how to appropriately weight such samples, and should investigate this problem.

-   We should consider the relationship between the *q* binning axis and the reciprocal lattice. If these are similar sizes, there could be aliasing problems as the reciprocal-space data appears to vary slowly in *q* because the *q* samples are too sparse.
    - To avoid this problem it may be necessary to place samples at a range of distances *within* the *q* bins.
    - If *q* samples are exactly commensurate with the reciprocal
      lattice, there is potential for efficiency gains by re-using
      previously calculated frequencies/eigenvectors. It is however
      important to be aware of the consequences for convergence and
      sampling quality.
    - If we can identify a representative maximum frequency component
      of dω/d*q*, then the Sampling Theorem would give us a maximum
      acceptable spacing for *q*-sampling that accurately captures the
      whole band structure.

High-priority independent work packages to be progressed are:

- Analytic method for incoherent scattering systems
- Spherical averaging on a requested sequence of *q* values, with options to
  - Sample in a uniform way (e.g. Fibonacci scheme)
  - Sample randomly

Further scoping work should be performed for:

- Sampling from an arbitrary collection points in **q**-space (not regular shells)
- Sampling within *q* bins (i.e. the link between this approach and spherical averaging.)

There are some longer-term projects that could be valuable but will
require basic infrastructure to be in place first:

- Explore the convergence properties of spherical averaging and random sampling methods
- Examine how this might be predicted from the force constants data
- Develop an algorithm for automatic convergence to a defined tolerance
- Consider appropriate statistical approaches for setting and interpreting that tolerance

# References

- Tomkinson, J., Warner, M., & Taylor, A. (1984). Powder averages for neutron spectroscopy of anisotropic molecular oscillators. Mol. Phys., 51(2), 381–392.
- Waddington, T. C., Howard, J., Brierley, K. P., & Tomkinson, J. (1982). *Chemical Physics*, 64(2), 193–201. [DOI:10.1016/0301-0104(82)87086-9](https://doi.org/10.1016/0301-0104(82)87086-9 "DOI link")
- Warner, M., Lovesy, S. W., & Smith, J. (1982). *RAL Technical Reports* RL-81-112. Retrieved from http://purl.org/net/epubs/work/22697
