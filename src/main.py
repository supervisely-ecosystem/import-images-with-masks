import supervisely as sly
import time
import functions as f
import globals as g


@sly.timeit
def import_images_with_masks(api: sly.Api, task_id: int):
    # PART 1
    start_time = time.time()
    dir_info = api.file.list(g.TEAM_ID, g.INPUT_PATH)
    if len(dir_info) == 0:
        raise FileNotFoundError(f"There are no files in selected directory: '{g.INPUT_PATH}'")

    end_time = time.time()
    print(f"Part 1 | Time taken by: {end_time - start_time} seconds")
    sly.logger.debug(f"Part 1 | Time taken by: {end_time - start_time} seconds")

    # PART 2
    start_time = time.time()
    if g.PROJECT_ID is None:
        project_name = (
            f.get_project_name_from_input_path(g.INPUT_PATH)
            if len(g.OUTPUT_PROJECT_NAME) == 0
            else g.OUTPUT_PROJECT_NAME
        )
    else:
        project = api.project.get_info_by_id(g.PROJECT_ID)
        project_name = project.name

    original_project_path, converted_project_path = f.download_project(
        api=api, input_path=g.INPUT_PATH
    )
    class_color_map = f.get_class_color_map(project_path=original_project_path)
    project_meta = f.get_or_create_project_meta(
        api=api, project_path=original_project_path, classes_mapping=class_color_map
    )
    end_time = time.time()
    print(f"Part 2 | Time taken by: {end_time - start_time} seconds")
    sly.logger.debug(f"Part 2 | Time taken by: {end_time - start_time} seconds")

    # PART 3
    start_time = time.time()
    project = f.convert_project(
        project_path=original_project_path,
        new_project_path=converted_project_path,
        project_meta=project_meta,
        classes_map=class_color_map,
    )
    end_time = time.time()
    print(f"Part 3 | Time taken by: {end_time - start_time} seconds")
    sly.logger.debug(f"Part 3 | Time taken by: {end_time - start_time} seconds")

    # PART 4
    start_time = time.time()
    f.upload_project(
        api=api,
        task_id=task_id,
        local_project=project,
        project_name=project_name,
        local_project_path=converted_project_path,
    )
    end_time = time.time()
    print(f"Part 4 | Time taken by: {end_time - start_time} seconds")
    sly.logger.debug(f"Part 4 | Time taken by: {end_time - start_time} seconds")


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
