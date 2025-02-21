# Releases and Versioning

Euphonic follows [semantic versioning](https://semver.org/) and releases on
Github, PyPI and Conda (via the conda-forge channel).

The release process for Euphonic has been changed at the beginning of
2025 to be more streamlined and facilitate pre-releases or bugfixes on
historical releases. Most steps are performed by Github Actions
workflows; some of these use scripts located in the *build_utils/*.

The only thing that really cannot be fixed are the packages uploaded
to PyPI. If we upload a bad release to PyPI, the only solution is to
mark it as "yanked", increment the version number and release a new
version. The release workflow includes a lot of tests and
sanity-checks to reduce the likelihood of this scenario.

# Release process:
## 0. Consider tidying up metadata (CHANGELOG.rst, CITATION.cff)

If good practice has been followed, CHANGELOG.rst should already have
a presentable-looking "Unreleased" section; this will automatically be
used as notes for the new version.

> **NOTE:** pre-releases do not get a CHANGELOG update, as the new
> features are still officially "Unreleased".

Similarly, CITATION.cff _should_ have been updated with new
contributors when a significant contribution was made to the project.

There is no need to change the version number yet.

## 1. Update any new deprecated directives

Euphonic uses Numpy docstrings, which recommends use of Sphinx deprecated directives
https://numpydoc.readthedocs.io/en/latest/format.html#sections. When these are added,
this often requires guessing what the next release will be (deprecated since vx.y.z).
When a new release is made, a search should be made to ensure these directives are
accurate. e.g. if you are releasing v0.5.2, and you see a deprecated directive that
shows version v0.6.0, it should be corrected to v0.5.2 as that is the correct next
release after the deprecation

## 2. Create a release branch and wait for tests to pass.

Create a branch with "release" somewhere in the name and push to
GitHub. This will trigger a "run-tests" workflow which can be
monitored [here](https://github.com/pace-neutrons/Euphonic/actions).

> **NOTE:** unlike the automatic PR tests, this will include all
> supported platforms and python versions.
> A full test can also be run on a PR by using a manual dispatch
> of run-tests, targeting the appropriate branch.

## 3. Run the Release workflow

In the [Github Actions](https://github.com/pace-neutrons/Euphonic/actions)
sidebar choose "Create a release" (`release.yml`) workflow and run
specifying the release branch and proposed version number.

- Pre-releases should have text after the [semver number](https://packaging.python.org/en/latest/discussions/versioning/), such as "v1.4.1rc2".
- It should generally be safe to enable "Make release and push to PyPI" without a dry-run: the workflow will exit early if a step fails.

### Fixing a failed release workflow

- Small problems can be fixed on the release branch. Consider making a pull-request to `master` so these can be reviewed more easily; the branch can still be used to release.
- If something went wrong after the "Bump version number" step, you will need to delete the new git tag from https://github.com/pace-neutrons/Euphonic/tags
- If something went wrong after making a Github release, you will need to delete the release from https://github.com/pace-neutrons/Euphonic/releases
- If good packages were already uploaded to PyPI but something went wrong producing the landing page, you don't need to redo the release. Fix it directly on the gh-pages branch.
- When things are looking good, run the release workflow again.

## 4. Check versioned landing page
The release workflow should have called `create-landing-page.yml` to create
a versioned page e.g. https://pace-neutrons.github.io/Euphonic/versions/v0.6.2.html;
check it looks sensible.

## 5. Post-release testing: PyPI
There is a "Test PyPI release" (`test_release_release.yml`) workflow
that must be triggered manually with a workflow dispatch. Run the
workflow with the release version to check installation from PyPI
works and tests pass.

## 6. Update conda-forge package 
After the release hits PyPI, wait
for the conda-forge bot to open a PR in
https://github.com/conda-forge/euphonic-feedstock : this may take a few
hours. Make sure all the tests pass, and merge the PR.

## 7. Test conda-forge package
Once the PR has been merged and the triggered jobs have completed, Euphonic
should be available on the conda-forge channel. Run the "Test Conda-forge release"
 (`test_release.yml`) workflow in the Euphonic repo to check that the PyPI and conda packages
pass tests

## 8. Request DOI
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
