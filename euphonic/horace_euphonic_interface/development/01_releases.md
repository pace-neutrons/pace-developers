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

# light_python_wrapper Release Process

## 1. Update the changelog

* Update the `Unreleased` title in `CHANGELOG.rst` and the associated Github
compare to the new version e.g.
```
`Unreleased <https://github.com/pace-neutrons/light_python_wrapper/compare/v0.2.2...HEAD>`_
----------
```
becomes:
```
`v0.3.0 <https://github.com/pace-neutrons/light_python_wrapper/compare/v0.2.2...v0.3.0>`_
------
```

* Add a new `Unreleased` line e.g.
```
`Unreleased <https://github.com/pace-neutrons/light_python_wrapper/compare/v0.3.0...HEAD>`_
----------
```
Note the compare in `Unreleased` now compares with the latest version v0.3.0
not v0.2.2

## 2. Commit changelog changes

## 3. Tag the latest commit
e.g.:

```
git tag v0.3.0
```

## 4. Push the tag to master
e.g.:
```
git push origin v0.3.0
```

## 5. Publish release
Go to https://github.com/pace-neutrons/light_python_wrapper/releases and
click 'Draft a new release'. Choose the tag you just pushed as the version,
and add the updates from `CHANGELOG.rst` to the release body.

# euphonic_sqw_models Release Process

## 1. Update the changelog
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

## 2. Commit and tag changes (don't push yet)
Commit the changes made to `CHANGELOG.rst` and tag the commit with the new
version e.g.:

```
git tag v0.2.0
```
Versioning is managed by
[versioneer](https://github.com/warner/python-versioneer) so once a
commit has been tagged, this will update `__version__`
automatically

## 3. Test Github release.py
Running `release.py` with the `--github` flag will check the Euphonic version
in `min_requirements.txt` and parse CHANGELOG.rst to generate a JSON payload that
can be posted to Github's release API. By default it will just print the payload,
this is useful to check the payload is being generated correctly. Make sure to
check the version/body etc. are all what you expect. If it's not what you expect,
now is the time to make any changes, as the commit/tag haven't been pushed yet,
the tag can still be deleted and reapplied once any fixes have been made.

## 4. Push the commit and tag
If you're happy with the Github test release, push the commit and tag to main

## 5. Actually release on Github
To actually post to Github run
`python release.py --github --notest`

For Github, this will create a release. To authenticate, it uses a Github
[personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
Set it as the `GITHUB_TOKEN` envronment variable and it will be used to
authenticate.

## 6. Test Github release
Check a release has actually been done on Github and looks sensible. Try
downloading the .zip and running tests.


# Horace-Euphonic-Interface Release Process

## 1. Update to release versions of submodules
Use `git submodule` to check the submodule versions, check they are release versions.
Then run `git status` to check that the release versions of the submodules have actually
been commited to horace-euphonic-interface master (if any submodules say `new commits`,
they have not been commited). If any are not release versions or git status says `new commits`, create a
new horace-euphonic-interface branch (e.g. `v0.3.0_release`) and update the
submodules to release versions. 

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

## 3. Update CITATION.cff

The 'version' and 'date-released' fields should be updated to the new version
and current date

## 4. Ensure tests pass
Make sure all CI tests are passing on the branch with the updated submodules. You
may have to create a PR for the tests to run.

## 5. Create a temporary tag to test release process (don't push the tag)
Tag the latest commit on the branch with the changes made to `CHANGELOG.rst`
and and update submodules, and tag the commit with the new
version e.g. `git tag v0.2.0`

## 6. Test Github release.py
Running `release.py` with the `--github` flag will create a .mltbx, and
generate a JSON payload that can be posted to Github's release API.
It will print the payload, make sure to check the version/body etc. are
all what you expect. Try installing the .mltbx and running tests, in
particular check the horace-euphonic-interface version, and the version
of Euphonic specified in `+euphonic/private/required_modules.m` are
as expected.

If anything is not what you expect, delete the tag, make any updates and
try again (as the tag hasn't been pushed yet).

## 7. Delete tag, merge branch, push new tag

Once you're happy with the test release, delete the local tag,
merge the branch into master, tag the latest master commit and
push the tag. e.g.:
```
git tag --delete v0.2.0
git checkout master
git merge v0.2.0_release
git push origin master
git tag v0.2.0
git push origin v0.2.0
```

## 8. Actually release on Github
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

## 9. Test Github release
Check a release has actually been done on Github and looks sensible. Try
downloading the .zip and installing and running tests.

## 10. Test MATLAB File Exchange release
The release may take around an hour to appear on the file exchange. Check
that the version has updated, it will install and tests pass.

## 11. Request DOI

A DOI will need to be requested for the new version, this can be obtained from
the Software Engineering Group in the Scientific Computing Department (contact
for this as of 1/12/22 is Antony Wilson). Alternatively, access can be
requested to mint your own DOIs at https://doi.stfc.ac.uk/mint. The form
should be filled in as follows:

- **DOI** 10.5286/software/horaceeuphonicinterface/{version}
- **URL** https://pace-neutrons.github.io/horace-euphonic-interface/versions/v{version}.html
- **Title** Horace-Euphonic-Interface {version}
- **Creator** Add authors and Orcids as in CITATION.cff
- **Abstract** Horace-Euphonic-Interface is a MATLAB Add-on to allow simulation of Horace cuts with Euphonic.
- **Publisher** STFC
- **Publication Year** YYYY
- **Resource Type** Software
- **Funder** None?
- **Subject** None?
- **Related Identifier** 10.5286/software/horaceeuphonicinterface - DOI - IsVersionOf
- **Version** {version}
- **Date** YYYY-MM-DD Issued
