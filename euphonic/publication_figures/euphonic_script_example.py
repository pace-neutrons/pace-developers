import numpy as np

from euphonic import ForceConstants, ureg
from euphonic.util import mp_grid
from euphonic.plot import plot_2d

# Read CASTEP force constants
fc = ForceConstants.from_castep('La2Zr2O7.castep_bin')

# Create array of q-points in [H,-H,-2], with H from -8 to -4
qpts = np.zeros((1001, 3))
qpts[:, 0] = np.linspace(-8, -4, len(qpts))
qpts[:, 1] = -qpts[:, 0]
qpts[:, 2] = -2

# Calculate phonon frequencies and eigenvectors in [H,-H,2] direction
modes = fc.calculate_qpoint_phonon_modes(qpts)

# Create DebyeWaller object at 300K on 8x8x8 Monkhorst-Pack grid
dw_modes = fc.calculate_qpoint_phonon_modes(mp_grid([8, 8, 8]))
dw = dw_modes.calculate_debye_waller(300*ureg('K'))

# Calculate structure factors in [H,-H,2] with Debye-Waller
sf = modes.calculate_structure_factor(dw=dw)

# Calculate intensities using 1000 energy bins from 0 to 100 meV
ebins = np.linspace(0, 100, 1000)*ureg('meV')
sqw = sf.calculate_sqw_map(ebins)

# Broaden intensities by 1.5meV FWHM Gaussian in energy
sqwb = sqw.broaden(y_width=1.5*ureg('meV'))

# Set x-tick labels at H=-8, -7, -6, -5 and -4
sqwb.x_tick_labels = [(idx, str(qpts[idx, 0]))
                      for idx in np.linspace(0, len(qpts) - 1, 5, dtype=int)]

# Plot and show figure
fig = plot_2d(sqwb, vmax=5, y_label=f'Energy ({ebins.units:~P})')
fig.show()
