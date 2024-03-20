"""Generate empty files as test data.

For example, run `generate_testdata.py --files=10K --size=30K data/` to make 300MB of data.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from tqdm import trange
except:
    trange = range

def parse_units(s: str) -> int:
    # Create a dictionary of SI prefixes and their magnitudes
    prefixes = {"K": 10**3, "M": 10**6, "G": 10**9, "T": 10**12, "P": 10**15}

    s = s.upper()

    if s[-1] in prefixes:
        # If it is, multiply the number part of the string with the corresponding magnitude
        return int(s[:-1]) * prefixes[s[-1]]
    else:
        # If it's not, just convert the string to an integer
        return int(s)

def generate(root, files, size):
    block = b"\0" * 1024

    for i in trange(1, files + 1):
        out = Path(root, f"{i}.txt")
        with out.open("wb") as f:
            for blk in range(size // len(block)):
                f.write(block)
            f.write(b"\0" * (size % len(block)))


def main(argv=None):
    # parse command line arguments using argparse module
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outputDir", default=os.getcwd())
    parser.add_argument("-f", "--files", default="1")
    parser.add_argument("-s", "--size", default="10K")
    args = parser.parse_args(argv)

    root = Path(args.outputDir)
    root.mkdir(exist_ok=True)

    files = parse_units(args.files)
    size = parse_units(args.size)

    generate(root, files, size)


if __name__ == "__main__":
    main()
