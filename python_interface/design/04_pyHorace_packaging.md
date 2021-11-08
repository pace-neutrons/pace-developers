# A description of the prototype pyHorace implementation
**2021-1-3**


# Background

`pyHorace` will be a Python module which bundles together PACE programs written in Matlab for use by Python users without a Matlab license.

This document describes the options for packaging it for distribution to users.


# pyHorace packaging options

There are a few ways to distribute `pyHorace` which we need to decide on:

1. OS-specific packaging system
2. The Python Package Index (PyPI)
3. The Anaconda (`conda`) system

Option 1 would be to create packages for specific OS (e.g. `msi` for Windows, `dmg` for Mac OS, `deb` for Debian/Ubuntu, `rpm` for Red Hat/CentOS etc.).
These packages would be installed by users as they would a non-Python program.
Options 2 and 3 are specifically for Python packages (or packages meant to be used with Python).

A further decision is whether we should "bundle" the MCR with the `pyHorace` distribution or not.
The MCR is a very large archive (~2.8GB for R2020b) because it basically contains the full Matlab distribution.
If we want to distribute the MCR with the package, we are restricted to option 1 and self-hosting.
This is because PyPI has a limit of 100MB per package and Anaconda has a limit of 1GB per package.

An alternative to bundling the MCR is to include a step to automatically download and install an MCR during installation or on first use.
Doing this during installation limits the options to 1 or possibly 3 
(PyPI/`pip` does not allow to execute a custom script during installation, whilst it _may_ be possible with `conda`).
Alternatively, the Python package can provide a installation commandline tool.
On import, if `pyHorace` detects that the MCR is not install it will fail with a `RuntimeError`
which will tell the user to run the commandline tool to install the MCR,
or to provide the path to where they installed it (if non-standard location)
 in the `LD_LIBRARY_PATH` (Linux) or `PATH` (Windows) environment variable.

Finally, because `pyHorace` is Python package it requires a version of Python to be installed.
However, there are many possible Python distributions which users can install, depending on their OS.
The advantage of option 2 and 3 over 1 is that they are tied to a specific Python installation,
whilst in option 1 we need to determine which Python to install to.
This is usually only a problem on Windows because on Linux there is usually a pre-installed system Python installation which can be used.
On Windows, on the other hand, users will usually not have Python installed or may have multiple different (conflicting) Python installations.
(This is the reason why Mantid bundles a version of Python with its Windows package).

### Option 1 (own packaging) pros and cons

- Most flexibility, easiest user experience. 
- Most developer effort needed (initial development and ongoing maintenance).
- Needs hosting infrastructure.
- May need to bundle own Python installation on Windows.

### Option 2 (PyPI) pros and cons

- Standard way to distribute Python packages.
- Relatively easy / little developer effort to set up. 
- Self-hosting not needed / minimal maintenance needed.
- Users need to download and install Matlab MCR themselves.
- Users need to have installed Python already themselves (mainly issue on Windows).

### Option 3 (Anaconda) pros and cons

- Widely used by scientific Python users (and probably most popular way to install Python on Windows).
- Relatively easy / little developer effort to set up. 
- Self-hosting not needed / minimal maintenance needed.
- Users need to download and install Matlab MCR themselves.
