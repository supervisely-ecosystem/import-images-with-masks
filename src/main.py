import os
import supervisely as sly

import functions as f
import globals as g


@g.my_app.callback("import-images-with-masks")
@sly.timeit
def import_images_with_masks(api: sly.Api, task_id, context, state, app_logger) -> None:
    f.download_project(api, g.DOWNLOAD_DIR)

    possible_dirs = [d for d in sly.fs.dirs_with_marker(g.DOWNLOAD_DIR, g.COLOR_MAP_FILE_NAME)]
    if len(possible_dirs) == 0:
        raise RuntimeError(
            f"Can't find any directories with '{g.COLOR_MAP_FILE_NAME}' file in the input data"
        )

    uploaded = 0
    for project_path in possible_dirs:
        try:
            if g.PROJECT_ID is None:
                project_name = (
                    f.get_project_name_from_input_path(project_path)
                    if len(g.OUTPUT_PROJECT_NAME) == 0
                    else g.OUTPUT_PROJECT_NAME
                )
            else:
                project = api.project.get_info_by_id(g.PROJECT_ID)
                project_name = project.name
            sly.logger.debug(f"Processing project_path: {project_path}")

            class_color_map = f.get_class_color_map(project_path=project_path)

            sly.logger.debug("Class color map readed successfully...")

            project_meta = f.get_or_create_project_meta(
                api=api, project_path=project_path, classes_mapping=class_color_map
            )

            sly.logger.debug("Project meta readed successfully...")

            converted_project_path = os.path.join(
                os.path.dirname(os.path.dirname(project_path)), "converted"
            )

            sly.logger.debug(f"Will try to convert project to: {converted_project_path}...")

            project = f.convert_project(
                project_path=project_path,
                new_project_path=converted_project_path,
                project_meta=project_meta,
                classes_map=class_color_map,
            )

            sly.logger.info(f"Project from project_path: {project_path} converted successfully...")

            f.upload_project(
                api=api,
                task_id=task_id,
                local_project=project,
                project_name=project_name,
                local_project_path=converted_project_path,
            )

            uploaded += 1

            sly.logger.info(
                f"Project from directory: {converted_project_path} uploaded successfully..."
            )
        except Exception as error:
            sly.logger.warning(
                f"Project from directory: {project_path} was not uploaded. Error: {error}"
            )

    if uploaded == 0:
        raise RuntimeError(
            "Failed to upload data. Read the app overview and prepare data correctly."
        )
    else:
        sly.logger.info(f"Succesfully uploaded images with masks.")
    g.my_app.stop()

def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "TASK_ID": g.TASK_ID,
            "TEAM_ID": g.TEAM_ID,
            "WORKSPACE_ID": g.WORKSPACE_ID,
        },
    )
    g.my_app.run(initial_events=[{"command": "import-images-with-masks"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main, log_for_agent=False)
