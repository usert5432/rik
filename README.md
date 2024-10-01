# rik (Recursive Integrity Keeper)

## Overview

`rik` (Recursive Integrity Keeper) is a Python wrapper around the
[par2cmdline](https://github.com/Parchive/par2cmdline)
tool. It allows recursive calculation and verification of
[Reed-Solomon](https://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction)
error correction codes for your files. These codes can be used to restore file
content in case of damage, making `rik` particularly useful for long-term
archiving.

To create error correction codes, run `rik create -i par2 ./` in your
directory. `rik` will recursively process the directory contents, generating
Reed-Solomon codes for each file it encounters. To verify the integrity of your
files with the generated codes, use the command `rik verify -i par2 ./`.
At the end, the comprehensive summary of results will be printed. If any
corrupted files are found, the generated Reed-Solomon codes can be used to
restore them.


## Installation

### Prerequisites

`rik` uses [par2cmdline](https://github.com/Parchive/par2cmdline) as its
backend. Ensure that `par2cmdline` is installed and available in your system's
PATH before proceeding.

### Development version

To install the development version of `rik`, use the following commands:

```bash
git clone https://github.com/usert5432/rik
cd rik
python3 -m pip install -e .
```

### PyPI version

Alternatively, `rik` can be installed from the PyPI repository:

```bash
python3 -m pip install rik
```


## Usage

### 1. Creating Reed-Solomon Codes

To calculate Reed-Solomon codes for a directory `DIR`, run:

```bash
rik create -i par2 DIR
```

This command will recursively process the contents of the directory tree
starting from `DIR`. For each file encountered, it will calculate Reed-Solomon
error correction codes and save them in a `.par2` subdirectory next to the
original file.


### 2. Verifying File Integrity

To verify file integrity using previously calculated Reed-Solomon codes for a
directory `DIR`, one can use:

```bash
rik verify -i par2 DIR
```

A comprehensive summary of the verification process will be printed at the end.


### 3. Customizing Redundancy Level

You can pass arguments directly to the `par2cmdline` command. For instance, it
is possible to to specify redundancy level with:

```bash
rik create -i par2 DIR -- -r10
```

This argument will make `par2cmdline` create 10% redundancy.


### 4. Filtering Files

`rik` supports several filters to include/exclude files based on their paths
and sizes. For example,

- Calculate error correction codes only for files smaller than 100 MB:

```bash
rik create -i par2 -s '<100M' DIR
```

- Calculate error correction codes only for files outside of `.cache`
directories:

```bash
rik create -i par2 --exclude .cache DIR
```


## License

This project is distributed under the BSD 2-Clause License - refer to the the
LICENSE file for details.


