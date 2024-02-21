from typing import Generator

from numpy import arange
from numpy import random


def instance_colors(i: int = 0) -> Generator:
    """
    Generate a set of non-repetitive random colors for instance colors.

    Parameters
    ----------
    i : int, optional
        Seed for the random number generator. Default is ``0``.

    Yields
    ------
    tuple of int
        A tuple of three integers representing the RGB color of the instance.
    """
    random.seed(i)
    dim = 255

    n = arange(dim**3)
    random.shuffle(n)

    for i in range(dim**3):
        r = n[i] // dim**2
        g = (n[i] - r * dim**2) // dim
        b = n[i] - r * dim**2 - g * dim
        yield (r, g, b)
