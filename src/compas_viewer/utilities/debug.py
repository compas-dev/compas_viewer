from matplotlib import colors
from matplotlib import pyplot as plt


def display_instance_map_grid(instance_map):
    """Display the instance map as a grid of colors.

    Parameters
    ----------
    instance_map : :class:`numpy.ndarray`
        The instance map.
    """

    cmap = colors.ListedColormap(["Blue", "red"])
    plt.figure(figsize=(6, 6))
    plt.pcolor(self.render.instance_map[::-1], cmap=cmap, edgecolors="k", linewidths=3)
    plt.show()
