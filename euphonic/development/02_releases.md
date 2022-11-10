# Releases and Versioning

Euphonic follows [semantic versioning](https://semver.org/) and releases on
Github, PyPI and Conda (via the conda-forge channel).

There is a script in the main Euphonic repo,`release.py` for releasing on Github,
new releases should automatically trigger a workflow to release on PyPI, which
will trigger a new PR for the Conda release in
https://github.com/conda-forge/euphonic-feedstock.

Currently releases are done from `master` rather than having a release branch.
This may change in the future as the project evolves.

# Release process
## 1. Ensure tests pass on all Python versions
By default Euphonic tests only run on the lowest and highest supported Python
versions (e.g. 3.7 and 3.10) for each commit. Before a release, all
intermediate versions should also be tested (e.g. 3.8, 3.9). To run tests on
the intermediate versions, a
[workflow dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch)
can be used to manually run the tests on the master branch, this will run for
all supported Python verisons. Make sure these all pass before moving on to
the next step.

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

## 7. Push the commit
If you're happy with the Github test release, push the commit/tag to master.

## 8. Actually release on Github
To actually post to Github run
`python release.py --github --notest`

This will create a release. To authenticate, it uses a Github 
[personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
Set it as the `GITHUB_TOKEN` envronment variable and it will be used to
authenticate.

This should start a Github actions workflow `build_upload_pypi_wheels.yml`
which will build and upload a source and various wheels to PyPI. It
should also start a workflow `create-landing-page.yml` which should
publish a new version page to the `gh-pages` branch

## 9. Test PyPI releases
There is a `test_release.yml` workflow that must be triggered manually with
a workflow dispatch. Run the workflow with the release version to check all
the PyPI builds succeed. The Conda builds may fail if a Conda release hasn't
been made yet

## 10. Test versioned landing page
The above mentioned  `create-landing-page.yml` workflow should have created
a versioned page e.g. https://pace-neutrons.github.io/Euphonic/versions/v0.6.2.html,
check it looks sensible

## 11. Update conda-forge package
Wait for the conda-forge bot to open a PR in https://github.com/conda-forge/euphonic-feedstock,
this may take a few hours. Make sure all the tests pass, and merge the PR.

## 12. Test conda-forge package
Once the PR has been merged and the triggered jobs have completed, Euphonic
should be available on the conda-forge channel. Run the `test_release.yml`
workflow in the Euphonic repo to check that the PyPI and conda packages
pass tests

## 13. Request DOI
A DOI will need to be requested for the new version, this can be obtained from
the Software Engineering Group in the Scientific Computing Department (contact
for this as of 10/11/22 is Antony Wilson). Alternatively, access can be
requested to mint your own DOIs at https://doi.stfc.ac.uk/mint. The form
should be filled in as follows:

- **DOI** 10.5286/software/euphonic/{version}
- **URL** https://pace-neutrons.github.io/Euphonic/versions/v{version}.html
- **Title** Euphonic {version}
- **Creator** Add authors and Orcids as in CITATION.cff
- **Abstract** Euphonic is a Python package for efficient simulation of phonon bandstructures, density of states and inelastic neutron scattering intensities from force constants.
- **Publisher** STFC
- **Publication Year** YYYY
- **Resource Type** Software
- **Funder** None?
- **Subject** None?
- **Related Identifier** 10.5286/software/euphonic - DOI - IsVersionOf
- **Version** {version}
- **Date** YYYY-MM-DD Issued
