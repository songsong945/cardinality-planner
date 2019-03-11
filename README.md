# Pessimistic Cardinality Estimation: Tighter Upper Bounds for Intermediate Join Cardinalities

## Environment Setup Overview
There are two primary modules in this repository.

1. The first is the source code for a modified postgres instance.
The only real modification is in the `postgresql-9.6.6/src/backend/optimizer/path/costsize.c` file.
Specifically, in the `calc_joinrel_size_estimate` method.
Instead of returning the naive default postgres query optimizer cardinality estimates, we parse the `info.txt` file for join cardinality bounds which we use in place of the estimates.
If a bound is found for a subquery, then the bound is returned.
A bound will be returned for all sought after subqueries.
2. The second is a java module that decomposes queries and creates bounds for all necessary subqueries.
The module then populates the `info.txt` file which will then be able to be ingested by above modified postgres instance.

Following initial setup, one may simply run the java module which will execute each query in the desired workload.
For each query, we will populate `info.txt` with the necessary bounds.
Following this, each query is submitted to postgres.
It is also possible to simply run the queries using postgres' default cardinality estimates (this is done by simply leaving `info.txt` empty, a method for which is provided).

## Establishing Output Directories
We first wish to establish the output directories and sketch serialization directory paths.
In order to set up the paths across all necessary source files, we provide a shell script:
~~~~
./set_output_dir.sh
~~~~

## Modified Postgres Instance

### Postgres Installation
First, navigate to the postgres directory:
~~~~
cd postgresql-9.6.6/
~~~~

The modified postgres source code may be installed in the same manner as with a normal postgres instance.
We suggest finding a more comprehensive guide to building postgres from source that is specific to the reader's OS.
We found the following guides helpful:
- [Linux](https://www.postgresql.org/docs/9.6/install-short.html)
- [OSX](https://labs.wordtothewise.com/postgresql-osx/)
- [Windows](https://www.postgresql.org/docs/9.6/install-windows.html) [Note: the remainder of this guide will assume access to a unix command line]

Return to the home directory.
~~~~
cd ..
~~~~
Finally, we will also need to give ownership of the `info.txt` and `log.txt` files to the postgres default user.
Execute the following command:
~~~~
sudo chown -R postgres output
sudo chmod -R 777 output
~~~~

### Data Upload
One may clone our imdb database instance by first downloading the compressed database and unpacking.
The copressed data is available on [s3](https://s3-us-west-2.amazonaws.com/uwdbimdbsimple/imdb.dump.gz).
Readers are also welcome to use newer/older versions of the imdb dataset.
Bash script `populate_job.sh` will populate the imdb database or the reader may execute the commands separately.
~~~~
wget https://s3-us-west-2.amazonaws.com/uwdbimdbsimple/imdb.dump.gz
/usr/local/pgsql/bin/createdb imdb
gunzip -c imdb.dump.gz | psql imdb
~~~~

If using the provided imdb database snapashot, the reader should expect the database to take up 32GB of storage.
Data ingestion and setting up indexes should take approximately an hour. 
Please note that there are several static sketches saved in `BoundSketch/imdb_sketches/`.
These sketches comprise those sketches that would be populated and saved offline (as versus calculated at runtime) under the assumptions of the paper.
If the reader uses a snapshot of the imdb dataset that differs from the the provided snapshot, they should be sure to remove all files in the `BoundSketch/imdb_sketches/` directory to ensure correct statistics.
If recalculating statistics on a fresh/altered instance, the `getIMDBSketchPreprocessingTime()` method in `BoundSketch/src/Driver.java` will generate and serialize the static sketches.
In this scenario, this should be excuted before actual runtime experiments.

## Bound Generation Module
The purpose of this module is primarly to populate the `info.txt` file.
The Driver class is also set up to execute and run the join order benchmark.
Results for default postgres execution are written to `output/results/[DBName]/plan_execution_time_[budget].txt`.
For example, the result of running the join order benchmark with a hash budget of 4096 would be written to `output/results/imdb/plan_execution_time_4096.txt`.
We also include the sketch processing time which includes the additional runtime preprocessing penalty incurred by our method in `output/results/[DBName]/sketch_preprocessing_[budget].txt`.
We provide the postgres [EXPLAIN ANALYZE](https://www.postgresql.org/docs/9.6/sql-explain.html) output for each query in `output/raw/[DBName]/bound_[budget].txt`.
These include a detailed writeup of the physical join plan and the estimated versus observed intermediate join cardinalities.

Similarly, if one wishes to compare to default postgres execution, one will find these results, and physical plans in output`output/results/[DBName]/default.txt`, and `output/raw/[DBName]/default.txt`, respectively.

One may compile the java library using the following command (from the top level directory of the repo):
~~~~
javac -cp BoundSketch/src/.:BoundSketch/combinatoricslib3-3.2.0.jar:BoundSketch/jsqlparser-1.2-SNAPSHOT.jar:BoundSketch/postgresql-42.2.0.jar  BoundSketch/src/*.java
~~~~

One may execute the tests using the following command:
~~~~
java -cp BoundSketch/src/.:BoundSketch/combinatoricslib3-3.2.0.jar:BoundSketch/jsqlparser-1.2-SNAPSHOT.jar:BoundSketch/postgresql-42.2.0.jar Driver
~~~~
