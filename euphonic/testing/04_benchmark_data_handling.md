# Benchmark data handling

Here are details on how to handle data produced by the weekly performance benchmarking builds on Anvil Jenkins.

Scripts have been tested on python 3.6 and 3.8.

## Copying from Jenkins to SAN

A job ("Handle Artifacts") is triggered by the "Performance Benchmarking" Jenkins job to copy the performance_benchmarks.json file to the SAN. This couldn't be handled by the "Performance Benchmarking" job, because it has to be a freestyle job using the slurm plugin and we can't access the SAN in this manner. The "Handle Artifacts" job copies the last artifacts from the "Performance Benchmarking" job. This involved identifying the performance_benchmarks.json artifacts and then using the SAN path secret text robocopies the performance_benchmarks.json file to a directory with a name of formatted date and time. 

## Visualisation

The performance_benchmarks.json files are useful for keeping data to track performance regressions over time. But visualising them makes it easier to understand, so there is a script that creates matplotlib plots to visualise performance at `tests_and_analysis/performance_benchmarking/visualise.py`.

This script can create 3 types of plots depending on what arguments are parsed: performance over time, speedups over time and speedups for a particular file.

### Performance over time

Used by parsing the `-p` or `--performance` parameter with a directory e.g. `python visualise.py -p my_dir`. These plots shows how the median performance of functions on given architectures has changed over the course of time in the performance_benchmarks.json files stored in `my_dir`. The functionality searches for nested files in the directory. Multiple plots may be spawned depending on which functions have been tested and which architectures the tests have been run on.

## Speedups over time

Used by parsing the `-st` or `--speedup-over-time` parameter with a directory e.g. `python visualise.py -st my_dir`. This plot shows how speedups (the effect on performance from the utilisation of parallelisation) has changed over the course of time in the performance_benchmarks.json files stored in `my_dir`. The functionality searches for nested files in the directory. Multiple plots may be spawned depending on which functions have been tested and which architectures the tests have been run on.

## Speedups for a particular file

Used by parsing the `-sf` or `--speedup-file` parameter with a performance_benchmarks.json file e.g. `python visualise.py -sf my_dir\performance_benchmarks.json`. This plots shows how effective the utilisation of parallelisation has been in the test runs stored in the given file by plotting speedup against threads. Multiple plots may be spawned depending on what test functions speedups were calculated for in the file.
