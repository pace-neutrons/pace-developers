# Phonopy Reader

Phonopy documentation can be found [here](https://phonopy.github.io/phonopy/index.html).

User documentation and examples for interpolation and phonon handling are found 
[here](https://euphonic.readthedocs.io/en/latest/read_phonopy.html).

Euphonic only interfaces directly with CASTEP, but there are other modelling codes
available. It might not be worthwhile to reinvent the wheel and write interfaces for
each individually, so instead Phonopy has been used as a lingua franca to all
other calculators. See the Phonopy docs on 
[interfaces](https://phonopy.github.io/phonopy/interfaces.html#calculator-interfaces).

Changes to Euphonic:
- [Branch](https://github.com/pace-neutrons/Euphonic/tree/8_phonopy_interface_cp)
- Important files:
    - `euphonic/_readers/_phonopy.py`
    - `euphonic/data/interpolation.py`
    - `euphonic/data/phonon.py`
    - `test/test_interpolation_data_phonopy.py`
    - `test/test_phonon_data_phonopy.py`
    - `doc/source/read_phonopy.rst`

Changes to Phonopy:
- `--include-x` flags were added to Phonopy to facilitate sharing a single 
    summary file with complete data, though phonopy can output a range of files
    through options summarised in the user documentation. [Pull request](https://github.com/phonopy/phonopy/pull/108).
