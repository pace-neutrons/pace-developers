# Jenkins setup

Most setup for the Windows and Linux Anvil Jenkins builds has been completed through the creation of Jenkinsfiles stored in the `tests_and_analysis` folder in the euphonic codebase, under LinuxJenkinsfile and WindowsJenkinsfile. However, some further manual setup is required to get these jobs running on a Jenkins instance.

To start with the Jenkins instance needs linux agents with the label `sl7` and windows agents with the label `PACE Windows (Private)`.

## Linux

This is set up as a multibranch pipeline. The multibranch pipeline detects branches of the repository with the file `tests_and_analysis\LinuxJenkinsfile` and creates the branches own pipeline from the multibranch pipeline's settings and the Jenkinsfile.

To set up the multibranch pipeline we need to declare the 'Branch Sources' to which we add a GitHub source. This source includes a repository https url of https://github.com/pace-neutrons/Euphonic and Jenkins credentials can be found or created for the pace-builder account. These Jenkins credentials need to be of the username and password type, but you can replace the password with a relevant GitHub API token. In the same section we need to set some 'Behaviours'. Click add and select 'Discover branches (all branches)' and do the same for 'Discover tags', 'Clean before checkout' and 'Wipe out repository & force clone'.

You must also set the 'Build Configuration' with the mode 'by Jenkinsfile' and the 'Script Path' as `tests_and_analysis\LinuxJenkinsfile`.

For branches to be automatically detected rather than having to force a scan of the repository we must set up 'Scan Repository Triggers'. I would suggest setting a periodic scan (I have set it to once a day) and a 'Scan by webhook'. The input to the webhook field is the name of a Jenkins secret text credential that has access to the repository e.g. pace-builder. I also tend to set up discarding of old items with a maximum number of 10 old items to keep.

Then click save and it is set up, the repository should be scanned and tests run.

## Windows

This set up is much the same as the Linux multibranch pipeline. However, we will not set up the 'Branch Sources' as a GitHub repository, but as a Git repository (this avoids having data sent back to GitHub on whether the pipeline fails or not, which we are avoiding as the Windows node often fails for odd reasons not related to the code being tested). In the Git branch source setup input the same credentials, repository and behaviour as the Linux pipeline.

In 'Build Configuration' again select the 'by Jenkinsfile' mode and this time set the 'Script path to `tests_and_analysis/WindowsJenkinsfile`.

Set the triggers and discarding item strategies to be the same as the Linux builds. Then click save and it is set up, the repository should be scanned and tests run.
