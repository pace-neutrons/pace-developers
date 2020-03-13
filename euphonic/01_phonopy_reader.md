# Phonopy Reader

Phonopy documentation can be found [here](https://phonopy.github.io/phonopy/index.html).
User documentation and examples for interpolation and phonon handling are [here](https://euphonic.readthedocs.io/en/latest/read_phonopy.html)

Euphonic only interfaces directly with CASTEP, but there are other modelling codes
available. It might not be worthwhile to reinvent the wheel and write interfaces for
each individually, so instead Phonopy has been used as a lingua franca to all
other calculators. See the Phonopy docs on [interfaces](https://phonopy.github.io/phonopy/interfaces.html#calculator-interfaces)

Development notes:
    - All changes are made on project branch 8 (called `8_phonopy_interface_cp`)
    - `--include-x` parameters were added to Phonopy to facilitate sharing a 
        single file with complete data, though phonopy can output a range of files
        through options summarised in the user documentation.

TODO:
    - Update Phonopy file IO to generate unified hdf5 output file (currently yaml only)
        since hdf5 tends to make loading force constants ~10x times faster.
    - Phonopy handles unit cell/primitive cells inconsistently, Euphonic should detect 
        when the primitive cell was used to generate the force constants file.
