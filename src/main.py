import os
import supervisely as sly
import globals as g
import functions as f


class MyImport(sly.app.Import):
    def is_path_required(self) -> bool:
        return False

    def process(self, context: sly.app.Import.Context):
        dir_info = g.api.file.list(context.team_id, g.INPUT_PATH)
        sly.logger.info(f"77777777777777777777777777777777777777777    {g.INPUT_PATH}")
        if len(dir_info) == 0:
            raise FileNotFoundError(f"There are no files in selected directory: '{g.INPUT_PATH}'")

        if context.project_id is None:
            project_name = (
                f.get_project_name_from_input_path(g.INPUT_PATH)
                if len(g.OUTPUT_PROJECT_NAME) == 0
                else g.OUTPUT_PROJECT_NAME
            )
        else:
            project = g.api.project.get_info_by_id(context.project_id)
            project_name = project.name

        original_project_path = context.path
        sly.logger.info(f"77777777777777777777777777777777777777777    {original_project_path}")
        if original_project_path is None or original_project_path == "":
            original_project_path = os.environ.get("modal.state.slyFolder")
        converted_project_path = f"{g.STORAGE_DIR}{g.INPUT_PATH}"
        sly.logger.info(f"77777777777777777777777777777777777777777    {original_project_path}")
        class_color_map = f.get_class_color_map(project_path=original_project_path)
        project_meta = f.get_or_create_project_meta(
            api=g.api,
            project_path=original_project_path,
            classes_mapping=class_color_map,
            project_id=context.project_id,
        )
        project = f.convert_project(
            project_path=original_project_path,
            new_project_path=converted_project_path,
            project_meta=project_meta,
            classes_map=class_color_map,
        )
        f.upload_project(
            api=g.api,
            local_project=project,
            project_name=project_name,
            local_project_path=converted_project_path,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            dataset_id=context.dataset_id,
        )


app = MyImport()
app.run()
