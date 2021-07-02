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

## 2. Update the changelog
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

## 3. Update CITATION.cff

The 'version' and 'date-released' fields should be updated to the new version
and current date

## 4. Update any new deprecated directives

Euphonic uses Numpy docstrings, which recommends use of Sphinx deprecated directives
https://numpydoc.readthedocs.io/en/latest/format.html#sections. When these are added,
this often requires guessing what the next release will be (deprecated since vx.y.z).
When a new release is made, a search should be made to ensure these directives are
accurate. e.g. if you are releasing v0.5.2, and you see a deprecated directive that
shows version v0.6.0, it should be corrected to v0.5.2 as that is the correct next
release after the deprecation

## 5. Commit and tag changes (don't push yet)
Commit the changes made to `CHANGELOG.rst` and tag the commit with the new
version e.g.:

```
git tag v0.2.3
```
Versioning is managed by
[versioneer](https://github.com/warner/python-versioneer) so once a
commit has been tagged, this will update `euphonic.__version__`
automatically

## 6. Test Github release.py
Running `release.py` with the `--github` flag will generate a JSON payload that
can be posted to Github's release API (see the script for details on how it
generates this). By default it will just print the payload, this is useful to
check the payload is being generated correctly. Make sure to check the 
version/body etc. are all what you expect. If it's not what you expect, now
is the time to make any changes, as the commit/tag haven't been pushed yet,
the tag can still be deleted and reapplied once any fixes have been made.

## 7. Test PyPI release.py
Running `release.py` with the `--pypi` flag will build and package Euphonic in
the `dist` directory (see script for specific commands). Check this runs with no
errors and Euphonic can be installed correctly from what is inside `dist` and any
tests pass. Again, as the commit/tag haven't been pushed yet, if anything is wrong
with the dist it can be fixed at this stage.

## 8. Push the commit
If you're happy with the Github/PyPI test releases, push the commit/tag to master.

## 9. Actually release on Github and PyPI
To actually post to Github/upload to PyPI run
`python release.py --github --pypi --notest`

For Github, this will create a release. To authenticate, it uses a Github 
[personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
Set it as the `GITHUB_TOKEN` envronment variable and it will be used to
authenticate.

For PyPI, it will then ask for a username and password with permission for the
Euphonic project on PyPI

## 10. Test Github/PyPI releases
Check a release has actually been done on Github and looks sensible. Try
downloading the .zip and installing and running tests.

Check the PyPI release using `pip`. Download and install from `pip` and run all
tests to ensure the install works. Do this on both Linux and Windows if
possible.

Check that the tag has run and been tested successfully on the Windows, Linux and Mac Jenkins pipelines.
