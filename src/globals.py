import os
import sys
from distutils.util import strtobool

import supervisely as sly
from fastapi import FastAPI
from supervisely.app.fastapi import create

app_root_directory = os.path.dirname(os.getcwd())
sys.path.append(app_root_directory)
sys.path.append(os.path.join(app_root_directory, "src"))
print(f"App root directory: {app_root_directory}")
sly.logger.info(f'PYTHONPATH={os.environ.get("PYTHONPATH", "")}')

# order matters
# from dotenv import load_dotenv
# load_dotenv(os.path.join(app_root_directory, "secret_debug.env"))
# load_dotenv(os.path.join(app_root_directory, "debug.env"))

app = FastAPI()

sly_app = create()

api = sly.Api.from_env()

TASK_ID = int(os.environ["TASK_ID"])
TEAM_ID = int(os.environ["context.teamId"])
WORKSPACE_ID = int(os.environ["context.workspaceId"])

INPUT_PATH = os.environ.get("modal.state.files", None)
if INPUT_PATH is None or INPUT_PATH == "":
    INPUT_PATH = os.environ.get("modal.state.slyFolder")

IMAGE_DIR_NAME = "img"
ANNOTATION_DIR_NAME = "ann"
MASKS_MACHINE_DIR_NAME = "masks_machine"
MASKS_INSTANCE_DIR_NAME = "masks_instances"
MASKS_HUMAN_DIR_NAME = "masks_human"

COLOR_MAP_FILE_NAME = "obj_class_to_machine_color.json"

OUTPUT_PROJECT_NAME = os.environ.get("modal.state.project_name", "")
REMOVE_SOURCE = bool(strtobool(os.getenv("modal.state.remove_source")))
MATCH_ALL = "__all__"

STORAGE_DIR = sly.app.get_data_dir()
