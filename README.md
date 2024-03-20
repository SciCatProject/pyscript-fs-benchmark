# PyScript benchmark

The goal is to benchmark pyscript on file operations

## Generating data

Testing requires some files! A script is provided to generate empty files:

```sh
$ python generate_testdata.py --files=10K --size=30K data/
```

## Python benchmark

Benchmark reading all files with python:

```sh
$ python benchmark.py data/
Read 300000000 bytes from 10000 files in 0.9065102919994388s = 331MB/s
```

I suggest running a few times so the data is hot.

## PyScript benchmark

Start by serving the files in this directory. I use the VSCode 'Live Server' plugin, but
it would also work with nginx, apache, etc. Directly viewing `file://` urls will not
work because local file access requires a server.

Open [index.html](http://127.0.0.1:5500/index.html) using Chrome or Edge. *Firefox does
not support file access.* Select the data folder. Wait a few seconds, and you should see
the same benchmark results:

```
Read 300000000 bytes from 10000 files in 0.40560000000000684s = 740MB/s
```

## Bugs

The pyscript version reports unrealistically high speeds. I suspect that the 'mount'
operation loads the files into memory, making the actual parsing fast but at the
expense of high setup time. The benchmark should measure setup times, including loading
pyscript and mounting the directory

