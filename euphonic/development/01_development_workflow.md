# Euphonic Development Workflow

**Starting Development:**
1. Check if an issue for the bug/feature you want to fix/develop already exists
2. If not, create an issue for that bug/feature, if it is appropriate
3. Create a development branch off master with a sensible name describing
development. If it is associated with an issue, prefix the branch with the issue
number, e.g. `git checkout -b 5_refactor_classes`
4. Do all development for that feature on that branch
5. Write tests for that feature/bugfix, and update any existing tests that may
affected by the change
6. Update the CHANGELOG.rst with a summary describing the change
6. Once development is finished, run all the tests. Run 
`python -munittest discover -v test` from the `Euphonic/test` directory and make
sure they pass

**Getting changes accepted:**

Changes are accepted onto master via pull requests. It is preferred to rebase
onto master rather than merging from master before making a pull request. The
process is:
1. Rebase your branch to master. When on your branch do `git rebase master` and
fix any merge conflicts. If you're not comfortable with rebasing yet, before
rebase you can make a copy of your branch e.g.
`git branch 5_refactor_classes_copy` 
2. Run the tests again `python -munittest discover -v test` from `Euphonic/test`
3. Force push the rebased version of your branch upstream, e.g.
`git push --force-with-lease origin 5_refactor_classes`
4. Create a pull request for your branch

