from pathlib import Path

from compas_viewer import Viewer
from compas_viewer.scene import Tag

viewer = Viewer()


def find_sys_font(font_name: str) -> Path | None:
    from matplotlib import font_manager

    for font in font_manager.fontManager.ttflist:
        if font.name == font_name:
            return Path(font.fname)


# By default, the text is rendered using the FreeSans font from the library.
t = Tag("EN", (0, 0, 0), height=50)
viewer.scene.add(t)

# Font specified is possible.
t = Tag("EN", (3, 0, 0), height=50, font=find_sys_font("Times New Roman"))
viewer.scene.add(t)

# Multi-language text is possible if the machine has the font installed.
t = Tag("中文 CN", (3, 3, 0), height=50, font=find_sys_font("DengXian"))
viewer.scene.add(t)

viewer.show()
