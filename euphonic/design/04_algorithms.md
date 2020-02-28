# Euphonic Algorithms Design


## 1. Interpolation of the force constants matrix

Phonon frequencies/eigenvectors can be calculated at any wavevector q from a
force constants matrix via Fourier interpolation ([1]). The force
constants matrix is defined as:

<p><img align="center" src="http://chart.apis.google.com/chart?cht=tx&chl=\phi_{\alpha{\alpha}'}^{\kappa{\kappa}'}=\frac{\delta^{2}E}{{\delta}u_{\kappa\alpha}{\delta}u_{{\kappa}'{\alpha}'}}"/> (1.1)</p>

The Dynamical matrix at q is calculated by:

<p><img align="center" src="http://chart.apis.google.com/chart?cht=tx&chl=D_{\alpha{\alpha}'}^{\kappa{\kappa}'}(q) =\frac{1}{\sqrt{M_{\kappa}M_{\kappa '}}}\sum_{a}\phi_{\alpha\alpha'}^{\kappa\kappa'}e^{-iq{\cdot}r_a}"/> (1.2)</p>

The dynamical matrix at q can be diagonalised to obtain the phonon frequencies
and eigenvectors at q. The eigenvalue equation is:

<p><img align="center" src="http://chart.apis.google.com/chart?cht=tx&chl=D_{\alpha{\alpha}'}^{\kappa{\kappa}'}(q) \varepsilon_{q\nu\kappa\alpha}=\omega_{q\nu}^{2} \varepsilon_{q\nu\kappa\alpha}"/> (1.3)</p>

Where &nu; runs over phonon modes, &kappa; runs over atoms, &alpha; runs over
the Cartesian directions, a runs over unit cells in the supercell,
u<sub>&kappa;&alpha;</sub> is the displacement of atom &kappa; in direction
&alpha;, M<sub>&kappa;</sub> is the mass of atom &kappa;, r<sub>a</sub> is the
vector to the origin of cell a in the supercell,
&epsilon;<sub>q&nu;&kappa;&alpha;</sub> are the eigevectors, and
&omega;<sub>q&nu;</sub><sup>2</sup> are the frequencies squared.

If the material is polar (has non-zero Born charges) there is a long-range
component of the force constants matrix due to long-ranged dipole-dipole
interactions within the material. This can be accounted for by applying a
(computationally expensive) correction to the dynamical matrix. This calculation
is relatively complex and detailed in [2], and a shorter summary can be found in
[3]. There is also a non-analytical correction that is applied to the dynamical
matrix at the gamma point which takes into account the q-direction of approach
to gamma and results in LO-TO splitting. This is also described in [2] and [3].


## 2. Calculation of the crystal structure factor

The crystal structure factor describes how phonons in the material scatter
incident neutrons. It is calculated for each Q (note: capital Q is neutron
momentum transfer, small q is phonon wavevector) and phonon mode &nu; by [4]:

<p><img align="center" src="http://chart.apis.google.com/chart?cht=tx&chl=F_{Q\nu}=\sum_{\kappa}{\sqrt{\frac{\hbar{b_{\kappa}^{2}}}{M_{\kappa}\omega_{q\nu}}}Q{\cdot}\varepsilon_{q\nu\kappa\alpha}e^{Q{\cdot}r_{\kappa}}e^{-W}}"/> (2.1)</p>

Where b<sub>&kappa;</sub> is the coherent scattering length of atom &kappa;,
r<sub>&kappa;</sub> is the ionic coordinate of atom &kappa;, and e<sup>-W</sup>
is the Debye-Waller factor (see section 3).

The crystal structure factor can be binned in energy, taking into account phonon
creation and annihilation:

<p><img align="center" src="http://chart.apis.google.com/chart?cht=tx&chl=S_{QE}}=\sum_{\nu}{\mid}F_{Q\nu}{\mid}^{2}(n_{\nu}%2B\frac{1}{2}\pm\frac{1}{2})\delta(E\mp\hbar{\omega}_{q\nu})"/> (2.2)</p>

Where n<sub>&nu;</sub> is the Bose population factor:

<p><img align="center" src="http://chart.apis.google.com/chart?cht=tx&chl=n_\nu=\frac{1}{e^{\frac{\hbar\omega_\nu}{\kappa_BT}}-1}"/> (2.3)</p>

&kappa;<sub>B</sub> is the Boltzmann constant and T is the temperature


## 3. Calculation of the Debye-Waller factor

The full anisotropic Debye-Waller factor can be defined as ([5]):

<p><img align="center" src="http://chart.apis.google.com/chart?cht=tx&chl=e^{-W}=e^{-{\sum_{\alpha\beta}}{W_{\alpha\beta}^{\kappa}}Q_{\alpha}Q_{\beta}}"/> (3.1)</p>

Where &kappa; runs over atoms, and &alpha;,&beta; run over the Cartesian
directions. As Q can be factored out,
W<sup>&kappa;</sup><sub>&alpha;&beta;</sub> only needs to be calculated once for
all Q (resulting in a 3x3 matrix for each atom), which will be referred to as
the Debye-Waller exponent:

<p><img align="center" src="http://chart.apis.google.com/chart?cht=tx&chl=W_{\alpha\beta}^{\kappa}=\frac{\hbar}{4N_qM_{\kappa}}\sum_{BZ}\frac{e_{q\nu\kappa\alpha}e^{*}_{q\nu\kappa\beta}}{\omega_{q\nu}}coth(\frac{\omega_{q\nu}}{2\kappa_BT})"/> (3.2)</p>

### References

[1] M. T. Dove, *Introduction to Lattice Dynamics*, Cambridge University Press, Cambridge, 1993, 83-87

[2] X. Gonze, C. Lee, *Phys. Rev. B*, 1997, **55(16)**, 10355-10368

[3] X. Gonze, C. Lee, D. C. Allan, M. P. Teter, *Phys. Rev. B*, 1994, **50(17)**, 13035-13038

[4] M. T. Dove, *Structure and Dynamics*, Oxford University Press, Oxford, 2003, 225-226

[5] G. L. Squires, *Introduction to the Theory of Thermal Neutron Scattering*, Dover Publications, New York, 1996, 34-37