# Benchmark data handling

Here are details on how to handle data produced by the weekly performance benchmarking builds on Anvil Jenkins.

Scripts have been tested on python 3.6 and 3.8.

## Copying from Jenkins to SAN

The data from the builds are stored in performance_benchmarks.json files as Jenkins artefacts. This data is produced by the pytest-benchmark plugin and has speedup data calculated and added to it. We have decided a better place to store the data is in the SAN storage. However, it cannot be directly sent from Jenkins to the SAN storage as Jenkins has read only access to SAN.

The solution created is a python script that pulls artefacts from Jenkins using the API and writes them to the SAN storage. The script can be found in the euphonic codebase at `tests_and_analysis/performance_benchmarking/artifact_handling/copy_benchmark_artifacts.py`. If you are connecting to a network location e.g. the SAN, then you may need to be on the VPN or connected to the relevant network. To use the script you need as few parameters:

- `-u` or `--user-id` Jenkins user ID from Anvil
  - On the Jenkins instance click on your username in the top right hand corner and the user ID should be displayed on that page
  - This user needs admin privileges to PACE-neutrons which may need to be requested from ANVIL@stfc.ac.uk
- `-t` or `--token` Jenkins user token
  - You can create a token on the Jenkins instance by clicking on your username in the top right hand corner, going to configure and clicking 'Create new API token'
- `-c` or `--copy-to-location` A location to copy the files to
  - It is likely you will be copying to the SAN storage (though you can pass anything here), but for security reasons this is being kept off GitHub so you will have to find it and type it yourself

There are also two optional parameters which may help in running the script

- `-j` or `--jenkins-job-url` The url of the Jenkins job
  - This defaults to the correct url for the current Jenkins job at the time of writing
- `r` or `--range` The range of Jenkins job builds to copy (inclusive)
  - This defaults to all of the Jenkins job builds found at the given url
  - You must pass two integer arguments

Example runs:

- `python copy_benchmark_artifacts.py -u my_id -t my_token -c my_dir`
- `python copy_benchmark_artifacts.py -u my_id -t my_token -c my_dir -r 1 9`

## Visualisation

The performance_benchmarks.json files are useful for keeping data to track performance regressions over time. But visualising them makes it easier to understand, so there is a script that creates matplotlib plots to visualise performance at `tests_and_analysis/performance_benchmarking/visualise.py`.

This script can create 3 types of plots depending on what arguments are parsed: performance over time, speedups over time and speedups for a particular file.

### Performance over time

Used by parsing the `-p` or `--performance` parameter with a directory e.g. `python visualise.py -p my_dir`. These plots shows how the median performance of functions on given architectures has changed over the course of time in the performance_benchmarks.json files stored in `my_dir`. The functionality searches for nested files in the directory. Multiple plots may be spawned depending on which functions have been tested and which architectures the tests have been run on.

## Speedups over time

Used by parsing the `-st` or `--speedup-over-time` parameter with a directory e.g. `python visualise.py -st my_dir`. This plot shows how speedups (the effect on performance from the utilisation of parallelisation) has changed over the course of time in the performance_benchmarks.json files stored in `my_dir`. The functionality searches for nested files in the directory. Multiple plots may be spawned depending on which functions have been tested and which architectures the tests have been run on.

## Speedups for a particular file

Used by parsing the `-sf` or `--speedup-file` parameter with a performance_benchmarks.json file e.g. `python visualise.py -sf my_dir\performance_benchmarks.json`. This plots shows how effective the utilisation of parallelisation has been in the test runs stored in the given file by plotting speedup against threads. Multiple plots may be spawned depending on what test functions speedups were calculated for in the file.
