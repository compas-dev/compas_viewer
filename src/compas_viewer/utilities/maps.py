from random import randint
from random import seed
from typing import Generator


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

    dim = 255
    seed(i)
    existed = []

    while True:
        n = randint(0, dim**3)

        if n in existed:
            continue

        existed.append(n)

        r = n // dim**2
        g = (n - r * dim**2) // dim
        b = n - r * dim**2 - g * dim

        yield (r, g, b)
