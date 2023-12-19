import os
from distutils.util import strtobool

import supervisely as sly
from dotenv import load_dotenv

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

my_app = sly.AppService()
api = sly.Api.from_env()

TASK_ID = int(os.environ["TASK_ID"])
TEAM_ID = int(os.environ["context.teamId"])
WORKSPACE_ID = int(os.environ["context.workspaceId"])

PROJECT_ID = None
DATASET_ID = None

if os.environ.get("modal.state.slyProjectId") is not None:
    PROJECT_ID = int(os.environ.get("modal.state.slyProjectId"))
if os.environ.get("modal.state.slyDatasetId") is not None:
    DATASET_ID = int(os.environ.get("modal.state.slyDatasetId"))

INPUT_FILE = sly.env.file(raise_not_found=False)
INPUT_DIR = sly.env.folder(raise_not_found=False)
INPUT_PATH = os.environ.get("modal.state.files", "")
if INPUT_PATH != "":
    # set env variable for future usage
    if INPUT_PATH.endswith("/"):
        os.environ["modal.state.slyFolder"] = INPUT_PATH
    else:
        os.environ["modal.state.slyFile"] = INPUT_PATH
elif INPUT_FILE is None and INPUT_DIR is None:
    raise RuntimeError("Please specify input file or directory")

IMAGE_DIR_NAME = "img"
ANNOTATION_DIR_NAME = "ann"
MASKS_MACHINE_DIR_NAME = "masks_machine"
MASKS_INSTANCE_DIR_NAME = "masks_instances"
MASKS_HUMAN_DIR_NAME = "masks_human"
MASK_DIRS = [
    IMAGE_DIR_NAME,
    ANNOTATION_DIR_NAME,
    MASKS_HUMAN_DIR_NAME,
    MASKS_INSTANCE_DIR_NAME,
    MASKS_MACHINE_DIR_NAME,
]

COLOR_MAP_FILE_NAME = "obj_class_to_machine_color.json"
DEFAULT_DS_NAME = "ds0"

OUTPUT_PROJECT_NAME = os.environ.get("modal.state.project_name", "")
REMOVE_SOURCE = bool(strtobool(os.getenv("modal.state.remove_source")))
MATCH_ALL = "__all__"

ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(ABSOLUTE_PATH)
sly.logger.debug(f"Absolute path: {ABSOLUTE_PATH}, parent dir: {PARENT_DIR}")

DOWNLOAD_DIR = os.path.join(PARENT_DIR, "images_project")
sly.fs.mkdir(DOWNLOAD_DIR, remove_content_if_exists=True)
sly.logger.info(f"App starting... DOWNLOAD_DIR: {DOWNLOAD_DIR}")
