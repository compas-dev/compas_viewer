from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer_test import Viewer

if __name__ == "__main__":
    viewer = Viewer()

    # for i in range(5):
    #     for j in range(5):
    #         viewer.scene.add(
    #             Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
    #             show_points=False,
    #             show_lines=True,
    #             surfacecolor=Color(i / 10, j / 10, 0.0),
    #             name=f"Box_{i}_{j}",
    #         )
    #         print()
    
    viewer.show()

