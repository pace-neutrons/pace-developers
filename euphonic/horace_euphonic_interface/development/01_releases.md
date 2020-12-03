# Releases and Versioning

Horace-Euphonic-Interface follows [semantic versioning](https://semver.org/)
and releases on Github.

There is a script in the main Horace-Euphonic-Interface repo, `release.py` for
releasing on Github. They should always be uploaded through `release.py` and
**never** manually. If the release process needs to be changed changes should
be made to this script and committed so there is a record.

Currently releases are done from `master` rather than having a release branch.
This may change in the future as the project evolves.

Horace-Euphonic-Interface is also released on the
[MATLAB File Exchange](https://www.mathworks.com/matlabcentral/about/fx/)
via GitHub Releases. It has already been set up, and in theory will automatically pull all new releases from GitHub. It can be found [here](https://www.mathworks.com/matlabcentral/fileexchange/83758-horace-euphonic-interface)

# Release process
## 1. Ensure tests pass
Hopefully this should be obvious, make sure all CI tests are passing for all
architectures on master

## 2. Update the changelog
Update the `Unreleased` title in `CHANGELOG.rst` and the associated Github
compare to the new version e.g.
```
`Unreleased <https://github.com/pace-neutrons/horace-euphonic-interface/compare/v0.1.0...HEAD>`_
----------
```
becomes:
```
`v0.2.0 <https://github.com/pace-neutrons/Euphonic/compare/v0.1.0...v0.2.0>`_
------
```

## 3. Update the version
Update the contents of `get_hor_eu_interface.py` to the new version

## 4. Commit and tag changes (don't push yet)
Commit the changes made to `get_hor_eu_interface.py` and `CHANGELOG.rst` and tag the commit with the new
version e.g.:

```
git tag v0.2.0
```

## 5. Test Github release.py
Running `release.py` with the `--github` flag will generate a JSON payload that
can be posted to Github's release API (see the script for details on how it
generates this). By default it will just print the payload, this is useful to
check the payload is being generated correctly. Make sure to check the 
version/body etc. are all what you expect. If it's not what you expect, now
is the time to make any changes, as the commit/tag haven't been pushed yet,
the tag can still be deleted and reapplied once any fixes have been made.

## 6. Push the commit
If you're happy with the Github test release, push the commit/tag to master.

## 7. Actually release on Github
To actually post to Github run `python release.py --github --notest`

For Github, this will create a release. To authenticate, it uses a Github 
[personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
Set it as the `GITHUB_TOKEN` envronment variable and it will be used to
authenticate.

## 8. Test Github release
Check a release has actually been done on Github and looks sensible. Try
downloading the .zip and installing and running tests.

## 9. Test MATLAB File Exchange release
The release may take around an hour to appear on the file exchange. Check
that the version has updated, it will install and tests pass.

## 10. Post release: Changelog update
On the next update post release add a new `Unreleased` line to `CHANGELOG.rst`

e.g.
```
`Unreleased <https://github.com/pace-neutrons/Euphonic/compare/v0.2.0...HEAD>`_
----------
```
Note the compare in `Unreleased` now compares with the latest version v0.2.0
not v0.1.0

## 11. Post release: Version update
On the next update post release add `.dev` to `get_hor_eu_interface_version.py` e.g. `return '0.1.0.dev'`
