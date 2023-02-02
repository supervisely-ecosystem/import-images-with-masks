import os
from distutils.util import strtobool
import supervisely as sly
from dotenv import load_dotenv


load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

api = sly.Api.from_env()

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
