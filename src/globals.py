import os
from distutils.util import strtobool

import supervisely as sly
from fastapi import FastAPI
from supervisely.app.fastapi import create
from dotenv import load_dotenv

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

app = FastAPI()
sly_app = create()
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

INPUT_PATH = os.environ.get("modal.state.files", None)
if INPUT_PATH is None or INPUT_PATH == "":
    INPUT_PATH = os.environ.get("modal.state.slyFolder")

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

STORAGE_DIR = sly.app.get_data_dir()
