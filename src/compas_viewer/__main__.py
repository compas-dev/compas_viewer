# ==========================================================================
# python -m compas_viewer -f "path/to/your/geometry.json"
# ==========================================================================

import argparse
from os import listdir
from os import path

from compas import json_load
from compas import json_loadz

from compas_viewer import Viewer

ap = argparse.ArgumentParser()
ap.add_argument(
    "-f",
    "--files",
    required=False,
    help="The compas.geometry's JSON file, or the compressed JSON file (ZIP), or a the path to a folder containing the JSON files for the viewer to load.",
)

args = vars(ap.parse_args())

# ==========================================================================
# "-f" argument
# ==========================================================================

geometries = []
if args["files"]:
    if path.isdir(args["files"]):
        file_names = listdir(args["files"])
        for file_name in file_names:
            if file_name.endswith(".json"):
                geometries.append(json_load(path.join(args["files"], file_name)))

    elif args["files"].endswith(".json"):
        geometries.append(json_load(args["files"]))
    elif args["files"].endswith(".zip"):
        geometries.append(json_loadz(args["files"]))
    else:
        raise ValueError("The file or directory is not valid.")

# ==========================================================================
# Launch
# ==========================================================================

print("Welcome to COMPAS Viewer!")
print("Check out our page for more tutorials, documentations and api references: https://compas.dev/compas_viewer")

viewer = Viewer()

for geometry in geometries:
    viewer.add(geometry)

viewer.show()
