# Scripts testing strategy

## optimise_eta.py

The script delegates most of it's work to euphonic and other python packages, it's job is simply to find the eta that is optimal in terms of calculating dipole corrections. As such the aim of the testing is to ensure the returned eta is the optimal eta.

The testing is split into unit and integration testing. As is usual with unit testing the packages that the script is dependent on are mocked out. We simulate time with mocking of the python time.time() function in the actual dipole correction calculations. One of the integration tests tests the same outcome but without mocking and uses an actual castep_bin file. Both unit and integration tests carry this out with various permutation of arguments.

The use of unit and integration tests should reveal whether an issue is in the script or in a dependency. The marking of tests as unit or integration allows one to run unit tests very quickly without the slowness of the actual calculation used in the integration tests (not that this is extremely slow, but if all tests were to do the same it would increase the number greatly).

Additionally the integration tests include a regression test. At the time of the initial testing, the optimal eta for the chosen castep_bin file is reliably and repeatedly 0.75. The test simply checks that upon calculation this is still the case. The aim of ths regression testing is to ensure code changes do not impact the existing functionality in the script.

## dos.py and dispersion.py

The rationale for testing dos.py and dispersion.py is different to optimise_eta.py, their outputs are matplotlib graphs or files containing a plot or "grace". The unit testing focuses on ensuring the correct dependencies are called to produce the plots. The aim of this is to catch the case where the script logic changes and a mistake is made resulting in a call not being made at the correct time or an argument not being respected by the script.

After having a read up on testing matplotlib I found the image_comparison testing facility. However, on further research I found that this is brittle and often gives failures for unimportant factors such as font differences ([https://stackoverflow.com/questions/27948126/how-can-i-write-unit-tests-against-code-that-uses-matplotlib](https://stackoverflow.com/questions/27948126/how-can-i-write-unit-tests-against-code-that-uses-matplotlib)). Instead as per the suggestions in the link I have extracted the matplotlib data and tested that it matches the data that is produced at the time of writing this. This regression testing aims to ensure any code changes do not impact the existing functionality of the scripts.
