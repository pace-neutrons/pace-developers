# Releases and Versioning

Horace-Euphonic-Interface follows [semantic versioning](https://semver.org/).
Release of Horace-Euphonic-Interface is a little complex as it has 2 submodules,
[light_python_wrapper](https://github.com/pace-neutrons/light_python_wrapper)
and [euphonic_sqw_models](https://github.com/pace-neutrons/euphonic_sqw_models)
which should be released and updated to a release version before
releasing Horace-Euphonic-Interface.

Horace-Euphonic-Interface releases on Github, as the source will not include
the submodules a .mltbx is also created as a release asset, which allows it
to be published with its submodules on the
[MATLAB File Exchange](https://www.mathworks.com/matlabcentral/about/fx/#Why_GitHub).

## light_python_wrapper Release Process

## 1. Tag the latest commit
e.g.:

```
git tag v0.2.0
```

## 2. Push the tag
Push the tag to master

## 3. Publish release
Go to https://github.com/pace-neutrons/light_python_wrapper/releases and
click 'Draft a new release'. Choose the tag you just pushed as the version,
and add any important updates in the release body.

# euphonic_sqw_models Release Process

## 1. Update min_requirements.txt and CHANGELOG.rst and push the commit
Update the euphonic line to be compatible with a specific Euphonic release, this
should probably be the latest Euphonic release e.g.
```
euphonic>0.4.0
```
becomes:
```
euphonic>=0.5.0
```

CHANGELOG.rst should also be updated (if it hasn't been already) to specify the
new euphonic dependency

## 2. Ensure tests pass
The above commit should trigger tests to run against the newly defined Euphonic version,
ensure they pass on all architectures

## 3. Update the changelog
* Update the `Unreleased` title in `CHANGELOG.rst` and the associated Github
compare to the new version e.g.
```
`Unreleased <https://github.com/pace-neutrons/euphonic_sqw_models/compare/v0.1.0...HEAD>`_
----------
```
becomes:
```
`v0.2.0 <https://github.com/pace-neutrons/euphonic_sqw_models/compare/v0.1.0...v0.2.0>`_
------
```

* Add a new `Unreleased` line e.g.
```
`Unreleased <https://github.com/pace-neutrons/euphonic_sqw_models/v0.2.0...HEAD>`_
----------
```
Note the compare in `Unreleased` now compares with the latest version v0.2.0
not v0.1.0

## 4. Commit and tag changes (don't push yet)
Commit the changes made to `CHANGELOG.rst` and tag the commit with the new
version e.g.:

```
git tag v0.2.0
```
Versioning is managed by
[versioneer](https://github.com/warner/python-versioneer) so once a
commit has been tagged, this will update `__version__`
automatically

## 5. Test Github release.py
Running `release.py` with the `--github` flag will check the Euphonic version
in `min_requirements.txt` and parse CHANGELOG.rst to generate a JSON payload that
can be posted to Github's release API. By default it will just print the payload,
this is useful to check the payload is being generated correctly. Make sure to
check the version/body etc. are all what you expect. If it's not what you expect,
now is the time to make any changes, as the commit/tag haven't been pushed yet,
the tag can still be deleted and reapplied once any fixes have been made.

## 6. Push the commit
If you're happy with the Github test release, push the commit/tag to main

## 7. Actually release on Github
To actually post to Github run
`python release.py --github --notest`

For Github, this will create a release. To authenticate, it uses a Github
[personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
Set it as the `GITHUB_TOKEN` envronment variable and it will be used to
authenticate.

## 8. Test Github release
Check a release has actually been done on Github and looks sensible. Try
downloading the .zip and running tests.


# Horace-Euphonic-Interface Release Process

## 1. Update to release versions of submodules
Use `git submodule` to check the submodule versions. If any are not release versions,
create a new horace-euphonic-interface branch (e.g. `v0.3.0_release`) and update the
submodules to release versions

## 2. Update the changelog
* On the same branch, update the `Unreleased` title in `CHANGELOG.rst` and the associated Github
compare to the new version e.g.
```
`Unreleased <https://github.com/pace-neutrons/horace-euphonic-interface/compare/v0.1.0...HEAD>`_
----------
```
becomes:
```
`v0.2.0 <https://github.com/pace-neutrons/horace-euphonic-interface/compare/v0.1.0...v0.2.0>`_
------
```

* Add a new `Unreleased` line e.g.
```
`Unreleased <https://github.com/pace-neutrons/horace-euphonic-interface/v0.2.0...HEAD>`_
----------
```
Note the compare in `Unreleased` now compares with the latest version v0.2.0
not v0.1.0

## 3. Ensure tests pass
Make sure all CI tests are passing on the branch with the updated submodules

## 4. Create a temporary tag to test release process (don't push the tag)
Tag the latest commit on the branch with the changes made to `CHANGELOG.rst`
and and update submodules, and tag the commit with the new
version e.g. `git tag v0.2.0`

## 5. Test Github release.py
Running `release.py` with the `--github` flag will create a .mltbx, and
generate a JSON payload that can be posted to Github's release API.
It will print the payload, make sure to check the version/body etc. are
all what you expect. Try installing the .mltbx and running tests, in
particular check the horace-euphonic-interface version, and the version
of Euphonic specified in `+euphonic/private/required_modules.m` are
as expected.

If anything is not what you expect, delete the tag, make any updates and
try again (as the tag hasn't been pushed yet).

## 6. Delete tag, merge branch, push new tag

Once you're happy with the test release, delete the local tag,
merge the branch into master, tag the latest master commit and
push the tag.

## 7. Actually release on Github
To actually post to Github run `python release.py --github --notest`

This will create a Matlab toolbox, create a release and upload the
toolbox as an asset. To authenticate, it uses a Github
[personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
Set it as the `GITHUB_TOKEN` envronment variable and it will be used to
authenticate.

Note that if there is a delay between creating the Github
release and uploading the .mltbx, the MATLAB File Exchange may only
pick up the source code .zip, and not the .mltbx, see
[here](https://www.mathworks.com/matlabcentral/answers/614428-file-exchange-not-using-mltbx-file-from-github-release)

## 8. Test Github release
Check a release has actually been done on Github and looks sensible. Try
downloading the .zip and installing and running tests.

## 9. Test MATLAB File Exchange release
The release may take around an hour to appear on the file exchange. Check
that the version has updated, it will install and tests pass.

## 10. Request DOI
A DOI will need to be requested for the new version (from the Software Engineering Group in SCD), of the form
10.5286/SOFTWARE/HORACEEUPHONICINTERFACE/{version} which points to
https://pace-neutrons.github.io/horace-euphonic-interface/versions/v{version}.html
