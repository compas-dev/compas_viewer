# ==========================================================================
# python -m compas_viewer -f "file path or directory path"
# ==========================================================================

import argparse
from os import listdir
from os import name
from os import path

from compas import json_load
from compas import json_loadz
from compas.scene.context import ITEM_SCENEOBJECT

from compas_viewer import Viewer


def validate_object(object):
    """Validate if the object is supported by the viewer."""

    return isinstance(object, tuple(ITEM_SCENEOBJECT["Viewer"].keys()))


ap = argparse.ArgumentParser()
ap.add_argument(
    "-f",
    "--file",
    required=False,
    help="""
    The compas.geometry's JSON file, or the compressed JSON file (ZIP).""",
)

ap.add_argument(
    "--files",
    required=False,
    help="""
    The path to a folder containing the JSON files for the viewer to load.""",
)

args = vars(ap.parse_args())


# ==========================================================================
# "-f" argument
# ==========================================================================

_geos = []
if args["file"]:
    if args["file"].endswith(".json"):
        _geos.append(json_load(args["file"]))
    elif args["file"].endswith(".zip"):
        _geos.append(json_loadz(args["file"]))
    else:
        raise ValueError(f"The file {args['file']} is not a JSON file or a compressed JSON file.")

# ==========================================================================
# "--files" argument
# ==========================================================================

if args["files"]:
    for file in listdir(args["files"]):
        if file.endswith(".json"):
            _geos.append(json_load(path.join(args["files"], file)))
        elif file.endswith(".zip"):
            _geos.append(json_loadz(path.join(args["files"], file)))
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
    viewer.add(item=geometry, name=name)

viewer.show()
