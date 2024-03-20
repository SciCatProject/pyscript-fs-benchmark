"""Benchmark reading files
"""

import argparse
import itertools
import math
import os
import sys
import timeit
from pathlib import Path

blocksize = 1024


# Patch timeit to save the return value
timeit.template = """
def inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    for _i in _it:
        retval = {stmt}
    _t1 = _timer()
    return _t1 - _t0, retval
"""


def read_files(files):
    size = 0
    for p in files:
        with p.open("rb") as f:
            while blk := f.read(blocksize):
                size += len(blk)
    return size


def loground(x: float, base=1000, sigfigs=1) -> (int, int):
    """Rounds x on a log scale to the nearest power.

    For `mantissa, exponent = loground(x, base)`,

        x ≈ mantissa * base ** exponent

    Args:
    - x: input number.
    - base: Base of the log scale. Defaults to 1000 to give thousands, millions, billions, etc.
    - sigfigs: Number of significant figures

    Returns:
    Tuple with the mantissa and exponent

    """
    if sigfigs < 1:
        raise ValueError("Require strictly positive sigfigs")

    if abs(x) <= base**-8:  # effective 0
        return (0, 0)

    # Choose log function for numeric stability
    if base % 10 == 0:  # probably power of 10

        def logB(xx):
            return math.log10(xx) / math.log10(base)

    else:  # probably power of 2

        def logB(xx):
            return math.log2(xx) / math.log2(base)

    exponent = math.floor(logB(abs(x)))  # chosen so mantissa is in [1, base]
    mantissa = round(x * base ** (sigfigs - 1 - exponent)) * base ** (1 - sigfigs)

    # For negative numbers, floor and round might be opposite directions
    if abs(mantissa) >= base:
        # Example: autoUnit_loground(-99.9, base=10, sigfigs=2)
        mantissa //= base
        exponent += 1

    assert 1.0 <= abs(mantissa) < base, mantissa

    return (mantissa, exponent)


def metricunit(x: int, base=1000, sigfigs=1) -> str:
    """Converts x to a compact string using metric units

    Metric units are used irrespective of the base (e.g. 'k' for the first power of base)

    Args:
    - x: input number.
    - base: Base of the log scale. Defaults to 1000 to give thousands, millions, billions, etc.
    - sigfigs: Number of significant figures

    Returns:
    A string with the rounded number followed by a metric prefix (k, M, G, T, etc).

    Raise: IndexOutOfBounds if `abs(x)` is outside the range of supported prefixes.
    """
    prefixes = " kMGTPEZYyzafpµmcd"  # wraps around, so need to check bounds

    mantissa, exponent = loground(x, base, sigfigs)

    if abs(exponent) > 8:
        raise ValueError(
            "Rounded number outside range. No prefix for {}**{}".format(base, exponent)
        )

    prefix = prefixes[exponent] if exponent != 0 else ""
    return "{:.{}f}{}".format(mantissa, sigfigs - 1, prefix)

def benchmark(root, filenum=0, number=1):
    files = sorted(f for f in root.iterdir() if f.is_file())
    if filenum > 0:
        files = files[:filenum]

    t = timeit.Timer(lambda: read_files(files))
    elapsed, size = t.timeit(number=number)
    msg = f"Read {size} bytes from {len(files)} files in {elapsed}s = {metricunit(size/elapsed)}B/s"
    
    return elapsed, size, msg

def main(argv=None):
    # parse command line arguments using argparse module
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dir", default=os.getcwd())
    parser.add_argument("-f", "--files", type=int, default=0)
    parser.add_argument("-n", "--number", type=int, default=1)
    args = parser.parse_args(argv)

    root = Path(args.dir)
    if not root.exists():
        parser.error(f"Directory doesn't exist: {args.dir}")

    filenum = args.files
    number = args.number
    elapsed, size, msg = benchmark(root, filenum, number)

    print(msg)


if __name__ == "__main__":
    main()
