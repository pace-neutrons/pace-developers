# Releases and Versioning

Euphonic follows [semantic versioning](https://semver.org/) and releases on
Github and PyPI should be synchronised.

There is a script in the main Euphonic repo,`release.py` for releasing on Github
and PyPI. Releases should **always** be compiled, tagged and uploaded through
`release.py` and **never** manually. If the release process needs to be changed,
changes should be made to this script and committed so there is a record.

Currently releases are done from `master` rather than having a release branch.
This may change in the future as the project evolves.

# Release process
## 1. Ensure tests pass
Hopefully this should be obvious, make sure all CI tests are passing for all
architectures on master

## 2. Update versions
To prepare a release some changes need to be made:
* Update the `__version__` variable in `euphonic/__init__.py` to the new version
* Update the `Unreleased` title in `CHANGELOG.rst` and the associated Github
compare to the new version e.g.
```
`Unreleased <https://github.com/pace-neutrons/Euphonic/compare/v0.2.2...HEAD>`_
----------
```
becomes:
```
`v0.2.3 <https://github.com/pace-neutrons/Euphonic/compare/v0.2.2...v0.2.3>`_
------
```

* Add a new `Unreleased` line e.g.
```
`Unreleased <https://github.com/pace-neutrons/Euphonic/compare/v0.2.3...HEAD>`_
----------
```
Note the compare in `Unreleased` now compares with the latest version v0.2.3
not v0.2.2

## 3. Test Github release.py
Running `release.py` with the `--github` flag will generate a JSON payload that
can be posted to Github's release API (see the script for details on how it
generates this). By default it will just print the payload, this is useful to
check the payload is being generated correctly. Make sure to check the 
version/body etc. are all what you expect.

## 4. Test PyPI release.py
Running `release.py` with the `--pypi` flag will build and package Euphonic in
the `dist` directory (see script for specific commands). Check this runs with no
errors and the `dist` looks sensible

## 5. Actually release on Github and PyPI
To actually post to Github/upload to PyPI run
`python release.py --github --pypi --notest`

For Github, this will create a release. To authenticate, it uses a Github 
[personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
Set it as the `GITHUB_TOKEN` envronment variable and it will be used to
authenticate.

For PyPI, it will then ask for a username and password with permission for the
Euphonic project on PyPI. An access token could also be used for this, this will
be tested next release.

## 6. Test Github/PyPI releases
Check a release has actually been done on Github and looks sensible. Try
downloading the .zip and installing and running tests.

Check the PyPI release using `pip`. Download and install from `pip` and run all
tests to ensure the install works. Do this on both Linux and Windows if
possible.

These could potentially be made into a CI job, one to think about.