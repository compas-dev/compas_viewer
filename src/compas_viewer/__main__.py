# ==========================================================================
# python -m compas_viewer -f "file path or directory path"
# ==========================================================================

import argparse
from pathlib import Path

from compas import json_load
from compas import json_loadz
from compas.scene.context import ITEM_SCENEOBJECT
from compas_viewer import Viewer


def validate_object(object):
    """Validate whether an object is supported by the viewer.

    Parameters
    ----------
    object
        Value to check against the registered viewer scene-object types.

    Returns
    -------
    bool
        Whether the object can be displayed by the viewer.

    """

    return isinstance(object, tuple(ITEM_SCENEOBJECT["Viewer"].keys()))


ap = argparse.ArgumentParser()
ap.add_argument(
    "-f",
    "--file",
    required=False,
    type=Path,
    help="""
    The compas.geometry's JSON file, or the compressed JSON file (ZIP).""",
)

ap.add_argument(
    "--files",
    required=False,
    type=Path,
    help="""
    The path to a folder containing the JSON files for the viewer to load.""",
)
ap.add_argument("-o", "--output", type=Path, help="Render the scene to an image without opening the viewer.")
ap.add_argument("--width", type=int, help="Output image width in pixels.")
ap.add_argument("--height", type=int, help="Output image height in pixels.")
ap.add_argument("--zoom-extents", action="store_true", help="Frame all visible objects before rendering the image.")

args = vars(ap.parse_args())


# ==========================================================================
# "-f" argument
# ==========================================================================

_geos = []
if args["file"]:
    if args["file"].suffix.lower() == ".json":
        _geos.append(json_load(args["file"]))
    elif args["file"].suffix.lower() == ".zip":
        _geos.append(json_loadz(args["file"]))
    else:
        raise ValueError(f"The file {args['file']} is not a JSON file or a compressed JSON file.")

# ==========================================================================
# "--files" argument
# ==========================================================================

if args["files"]:
    if not args["files"].is_dir():
        raise NotADirectoryError(args["files"])
    for file in sorted(args["files"].iterdir()):
        if not file.is_file():
            continue
        if file.suffix.lower() == ".json":
            _geos.append(json_load(file))
        elif file.suffix.lower() == ".zip":
            _geos.append(json_loadz(file))
        else:
            print(f"The file {file} in the folder {args['files']} is not a JSON file or a compressed JSON file.")


# ==========================================================================
# Validate Geometries
# ==========================================================================

# Viewer needs to be launched for validating the geometries.
viewer = Viewer()

geometries = {}
for _geo in _geos:
    if isinstance(_geo, list):
        for g in _geo:
            if validate_object(g):
                geometries[g] = g
            else:
                print(f"{g} is not supported by the viewer.")
    if isinstance(_geo, dict):
        for k, g in _geo.items():
            if validate_object(g):
                geometries[k] = g
            else:
                print(f"{g} is not supported by the viewer.")
    if validate_object(_geo):
        geometries[_geo] = _geo
    else:
        print(f"{_geo} is not supported by the viewer.")

# ==========================================================================
# Launch
# ==========================================================================

print("Welcome to COMPAS Viewer!")
print("Check out our page for more tutorials, documentations and api references: https://compas.dev/compas_viewer")


for name, geometry in geometries.items():
    viewer.scene.add(item=geometry, name=name)

if args["output"]:
    viewer.save_image(
        args["output"],
        width=args["width"],
        height=args["height"],
        zoom_extents=args["zoom_extents"],
    )
else:
    viewer.show()
