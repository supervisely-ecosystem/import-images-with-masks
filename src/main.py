import os
import supervisely as sly
import functions as f
import globals as g


@sly.timeit
def import_images_with_masks(api: sly.Api, task_id: int):
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

    sly.logger.debug(f"Will download project to local storage: {g.INPUT_PATH}")

    original_project_path = f.download_project(api=api, input_path=g.INPUT_PATH)

    sly.logger.debug(f"Project downloaded to local storage: {original_project_path}")

    for directory in sly.fs.dirs_with_marker(original_project_path, g.COLOR_MAP_FILE_NAME):
        sly.logger.debug(f"Processing directory: {directory}...")
        try:
            class_color_map = f.get_class_color_map(project_path=directory)
            project_meta = f.get_or_create_project_meta(
                api=api, project_path=directory, classes_mapping=class_color_map
            )

            parent_directory = os.path.dirname(directory)
            converted_project_path = os.path.join(parent_directory, g.INPUT_PATH)
            sly.logger.debug(f"Converted project path: {converted_project_path}")

            project = f.convert_project(
                project_path=directory,
                new_project_path=converted_project_path,
                project_meta=project_meta,
                classes_map=class_color_map,
            )

            f.upload_project(
                api=api,
                task_id=task_id,
                local_project=project,
                project_name=project_name,
                local_project_path=converted_project_path,
            )
            sly.logger.info(f"Project {directory} was uploaded successfully")
        except Exception as e:
            sly.logger.info(f"Project {directory} wasn't uploaded. Error: {e}")

    sly.logger.info(f"Finished processing all directories in {g.INPUT_PATH}")


if __name__ == "__main__":
    sly.logger.info(
        "Script arguments",
        extra={
            "context.teamId": g.TEAM_ID,
            "context.workspaceId": g.WORKSPACE_ID,
            "modal.state.slyFolder": g.INPUT_PATH,
        },
    )

    import_images_with_masks(g.api, g.TASK_ID)
    try:
        sly.app.fastapi.shutdown()
    except KeyboardInterrupt:
        sly.logger.info("Application shutdown successfully")
