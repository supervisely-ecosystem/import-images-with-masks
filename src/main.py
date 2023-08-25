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

    sly.logger.debug(
        f"Starting iteration over {g.INPUT_PATH} to find directories with {g.COLOR_MAP_FILE_NAME}"
    )

    idx = processed = 0
    for directory in sly.fs.dirs_with_marker(g.INPUT_PATH, g.COLOR_MAP_FILE_NAME):
        sly.logger.info(f"Working with directory: {directory}, index: {idx}...")

        original_project_path, converted_project_path = f.download_project(
            api=api, input_path=g.INPUT_PATH, idx=idx
        )

        sly.logger.debug(
            f"Original project path: {original_project_path}, "
            f"converted project path: {converted_project_path}"
        )

        class_color_map = f.get_class_color_map(project_path=original_project_path)

        sly.logger.debug("Readed class color map...")

        project_meta = f.get_or_create_project_meta(
            api=api, project_path=original_project_path, classes_mapping=class_color_map
        )

        sly.logger.debug("Readed project meta...")

        project = f.convert_project(
            project_path=original_project_path,
            new_project_path=converted_project_path,
            project_meta=project_meta,
            classes_map=class_color_map,
        )

        sly.logger.debug("Converted project, will upload it...")

        f.upload_project(
            api=api,
            task_id=task_id,
            local_project=project,
            project_name=project_name,
            local_project_path=converted_project_path,
        )

        sly.logger.info(f"Uploaded project: {project_name}")

        idx += 1
        processed += 1

    sly.logger.info("Processed all directories, will stop the application...")


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
