# Powder averaging: exploration of convergence properties

These notes were drawn up by Adam Jackson following a meeting on
2021-02-02 with Rebecca Fair, Dominik Jochym, Duc Le, Toby Perring,
Keith Refson, David Voneshen

## Background/methodology
   - We intend to provide user-friendly orientational-averaging tools to
     users, primarily for the computation of coherent S(|q|,ω) maps of
     powdered systems.

     - Spherical averaging functions are now included in Euphonic, with
        grid-based, random and quasirandom sampling schemes.

     - Optional parameters include the number of q-point samples,
       Gaussian/Lorentzian broadening width, and addition of
       jitter in phi/theta directions

   - Currently no tool is provided to apply such average over a sweep
     of |q| values; plots presented in this meeting were generated
     with scripts in an open Git branch targeting pace-developers:
     https://github.com/pace-neutrons/pace-developers/commit/a39b842abb3fb4d15bf23541c493423ce3264f27

  - Error is estimated by comparing computed spectra with those
    computed using at least one order-of-magnitude more
    q-points. Convergence with npts is quite smooth on this scale, so
    this should give a reasonable indicator of quality.

  - User-friendliness is identified as having

    - A robust method capable of delivering accurate results
    - A minimal number of adjustable parameters
    - Good defaults for any adjustable parameters

## Rejected approach (for now)

   - Consider the possibility of adaptive sampling which computes
     property with varying q-point meshes and automatically
     terminates when spectrum appears converged.
   - Concern about stability with respect to _small_ changes in number
     of samples, and cost effectiveness with respect to _large_ steps
     in number of samples.
   - Subsampling/progressive sampling does not play well with the
     sampling schemes implemented so far in Euphonic
     - Regular grids alias and are inefficient
     - Quasirandom "golden" sampling cannot be systematically subsampled

   - TP suggests investigation of Sobol sampling method, which allows
     progressive quasirandom sampling with blue noise-like distribution.

## Sampling parameter sensitivity tests
   - "Golden" quasirandom sphere sampling (as used in SpinW) is very
     effective, convincingly out-performing random, grid and
     jittered-grid methods.

   - Broadening is performed _after_ the spectrum is collected by
     q-point sampling. The RMS error values are drastically better for
     spectra that are heavily smoothed.

     - This suggests some coupling with instrumental broadening steps
       will be appropiate for efficient performance.

     - KR suggests that broadening can also be used within the
       sampling process, with an adaptive width based on the problem.
       This approach is also used for electronic structure DOS in
       OptaDOS and uses additional information about sampled points.

     - Qualitatively we see that low-quality broadened sampling can
       still display spurious features which have not yet been
       "averaged out" by other features. So RMS may not be an entirely
       trustworthy measure of quality; spurious correlations matter.

## q-dependence and system-dependence

   - The sampled spectrum drastically changes at different |q| values,
     and so does the corresponding sampling error.
   - At a fixed number of samples per sphere surface (npts), error
     tends to increase over a range of several reciprocal unit cells.

     - This trend is somewhat transferable across systems when |q| is
       normalised to a geometric mean of reciprocal lattice vectors.

     - DV, KR and TP expressed concern about extremely non-cubic cells
       such as layered materials. Perhaps it is better to use
       max() or min() than any average.

   - At long range (|q| > 3 * (|b1||b2||b3|)^1/3 ) there is no clear
     q-dependence and the error is quite erratic.

   - At very long range (|q| > 6 * (|b1||b2||b3|)^1/3 ) dispersive
     features are not very visible in the 2D spectrum and it is
     unlikely that any valuable information is being obtained by
     sampling more q-points.

   - At intermediate range, the error-vs-|q| trend can be somewhat flattened by allowing
     npts to follow |q|^2; i.e. sampling at a consistent _area density_.


## Suggested strategy

   - A multi-segment scheme in which minimum/maximum npts are set, and
     in-between npts is a multiple of |q|^2 (where |q| is somehow
     normalised to the reciprocal lattice).
   - This model has three parameters (a bit high) but they are all easily understood:
     - minimum qpts (used near the Gamma-point)
     - maximum qpts (used at long-range)
     - qpts density at sphere surface (in qpts Å^2 or, inequivalently
       but perhaps more intuitively, in qpts / (1/Å radius sphere))

   - Consider an analytic or simplified method for long-range where
     sphere can be considered good average of BZ.

     - DV raised that this may not be consistent with the generally
       rigorous approach taken to accuracy in this project; general
       agreement that such assumptions should be theoretically
       justified and backed-up empirically.

     - Another cost-saver would be the use of Brille for Brillouin zone (BZ)
        interpolation.
       - In this case, Euphonic would be used to calculate the phonon eigenvalues
         and eigenvectors on a grid in the first (or first irreducible) BZ.
       - An arbitrary qpt is transformed by the symmetry operations of the space group
         into the equivalent point in the first BZ, and the phonon eigenvalue/vector
         at the qpt can be obtained by linear interpolation in the first BZ.
       - The structure factor is calculated as normal from the eigenvalues/vectors
       - There is the overhead of first computing the grid in the first BZ, and the
         optimum grid size or point density should also be tested for convergence.

# Incidental observations
  - The calculations were quite slow to run (even with
    multithreading), which could negatively impact the end-user
    experience.

    - It has not yet been determined whether this was due to poor
      optimisation of the coherent sphere-averaging tools or is a
      limitation in the underlying spectrum calculation

    - One severe issue that can be addressed was memory usage when
      computing large numbers of qpts; this could be reduced by some
      kind of serial batching/chunking to reduce the size of arrays.

# Summary of decisions
  - A basic implementation of numerical powder-averaging should be
    included in the upcoming research paper and corresponding Euphonic
    release.
  - Investigation of smarter approaches and Brille integration will need to wait.

# Actions

## High-priority
   - Profile powder-averaging script to identify sources of
     poor performance (AJJ & RF)
   - Investigate possibility of limiting memory usage by sampling in batches of q-points. (AJJ & RF)
   - Examine impact of jitter in r-direction; does this clear up outliers? (AJJ)
   - Implement user API and scripts to make use of proposed 3-parameter powder-averaging scheme.
     - Try min/max instead of geometric mean

## Longer-term
   - Look into Sobol sampling (AJJ)
   - Consider powder-averaging at large q as a good
     application/demonstration of Brille-Euphonic interface
     (Euphonic-Brille team)
   - Look into fully volumetric sampling (AJJ)
   - Consider interactions between powder-averaging and instrumental
     resolution functions in overall design (TP)
