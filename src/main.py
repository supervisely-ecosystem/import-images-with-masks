import os
import supervisely as sly

from supervisely import handle_exceptions

import functions as f
import globals as g


@sly.timeit
@handle_exceptions
def import_images_with_masks(api: sly.Api, task_id: int):
    if g.INPUT_PATH is None:
        raise Exception("Please, upload a directory with images and masks. Read more in app overview.")
    dir_info = api.file.list(g.TEAM_ID, g.INPUT_PATH)
    if len(dir_info) == 0:
        raise FileNotFoundError(f"There are no files in selected directory: '{g.INPUT_PATH}'")

    if g.PROJECT_ID is None:
        project_name = (
            f.get_project_name_from_input_path(g.INPUT_PATH)
            if len(g.OUTPUT_PROJECT_NAME) == 0
            else g.OUTPUT_PROJECT_NAME
        )
    else:
        project = api.project.get_info_by_id(g.PROJECT_ID)
        project_name = project.name

    download_path = f.download_project(api=api)

    uploaded = 0

    for directory in sly.fs.dirs_with_marker(download_path, g.COLOR_MAP_FILE_NAME):
        try:
            sly.logger.debug(f"Processing directory: {directory}")

            class_color_map = f.get_class_color_map(project_path=directory)

            sly.logger.debug("Class color map readed successfully...")

            project_meta = f.get_or_create_project_meta(
                api=api, project_path=directory, classes_mapping=class_color_map
            )

            sly.logger.debug("Project meta readed successfully...")

            converted_project_path = os.path.join(
                os.path.dirname(os.path.dirname(directory)), "converted"
            )

            sly.logger.debug(f"Will try to convert project to: {converted_project_path}...")

            project = f.convert_project(
                project_path=directory,
                new_project_path=converted_project_path,
                project_meta=project_meta,
                classes_map=class_color_map,
            )

            sly.logger.info(f"Project from directory: {directory} converted successfully...")

            f.upload_project(
                api=api,
                task_id=task_id,
                local_project=project,
                project_name=project_name,
                local_project_path=converted_project_path,
            )

            uploaded += 1

            sly.logger.info(f"Project from directory: {directory} uploaded successfully...")
        except Exception as error:
            sly.logger.warning(
                f"Project from directory: {directory} was not uploaded. Error: {error}"
            )

    sly.logger.info("Finished processing all directories")

    if not uploaded:
        raise RuntimeError("The input data doesn't contain any valid directories.")
    else:
        sly.logger.info(f"Succesfully uploaded {uploaded} projects.")


def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "context.teamId": g.TEAM_ID,
            "context.workspaceId": g.WORKSPACE_ID,
            "modal.state.slyFolder": g.INPUT_PATH,
        },
    )
    import_images_with_masks(g.api, g.TASK_ID)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
    try:
        sly.app.fastapi.shutdown()
    except KeyboardInterrupt:
        sly.logger.info("Application shutdown successfully")
