import os
import re
from os.path import basename, dirname, exists, isdir, isfile, join

import cv2
import magic
import numpy as np
import supervisely as sly
from supervisely.io.fs import get_file_name, get_file_name_with_ext
from supervisely.io.json import load_json_file

import globals as g
import download_progress


def get_project_name_from_input_path(input_path: str) -> str:
    full_path_dir = dirname(input_path)
    return basename(full_path_dir)


def download_project(api: sly.Api, input_path: str) -> tuple:
    remote_proj_dir = input_path
    original_project_path = f"{g.STORAGE_DIR}/original_data/"
    converted_project_path = f"{g.STORAGE_DIR}{remote_proj_dir}/"

    sizeb = api.file.get_directory_size(g.TEAM_ID, remote_proj_dir)
    progress_cb = download_progress.get_progress_cb(
        api, g.TASK_ID, f"Downloading {input_path.strip('/')}", sizeb, is_size=True
    )
    if not exists(original_project_path):
        api.file.download_directory(
            g.TEAM_ID,
            remote_path=remote_proj_dir,
            local_save_path=original_project_path,
            progress_cb=progress_cb,
        )
    return original_project_path, converted_project_path


def get_datasets(project_path: str) -> tuple:
    dataset_names = []
    dataset_paths = []
    for dataset_name in os.listdir(project_path):
        dataset_path = join(project_path, dataset_name)
        if isdir(dataset_path):
            dataset_names.append(dataset_name)
            dataset_paths.append(dataset_path)
    if any(item in dataset_names for item in g.MASK_DIRS):
        dataset_names = [g.DEFAULT_DS_NAME]
        dataset_paths = [project_path]
    return dataset_names, dataset_paths


def get_class_color_map(project_path: str) -> dict:
    class_color_map_path = join(project_path, g.COLOR_MAP_FILE_NAME)
    if not exists(class_color_map_path):
        raise FileNotFoundError(f"Classes mapping file: {g.COLOR_MAP_FILE_NAME} not found.")
    return load_json_file(class_color_map_path)


def merge_meta_and_classes_mapping(
    api: sly.Api, project_meta: sly.ProjectMeta, classes_mapping: dict
) -> sly.ProjectMeta:
    for cls_name in classes_mapping:
        obj_class = project_meta.get_obj_class(cls_name)
        if obj_class is None:
            obj_class = sly.ObjClass(name=cls_name, geometry_type=sly.Bitmap)
            project_meta = project_meta.add_obj_class(obj_class)
            api.project.update_meta(id=g.PROJECT_ID, meta=project_meta.to_json())
    return project_meta


def get_or_create_project_meta(api, project_path: str, classes_mapping: dict) -> sly.ProjectMeta:
    if g.PROJECT_ID is not None:
        project_meta_json = g.api.project.get_meta(id=g.PROJECT_ID)
        project_meta = sly.ProjectMeta.from_json(data=project_meta_json)
        return merge_meta_and_classes_mapping(
            api=api, project_meta=project_meta, classes_mapping=classes_mapping
        )

    project_meta_path = join(project_path, "meta.json")
    if exists(project_meta_path):
        meta_json = load_json_file(project_meta_path)
        return sly.ProjectMeta.from_json(meta_json)
    obj_class_collection = create_obj_class_collection(classes_mapping)
    return sly.ProjectMeta(obj_classes=obj_class_collection)


def create_obj_class_collection(classes_mapping: dict) -> sly.ObjClassCollection:
    cls_list = [sly.ObjClass(cls_name, sly.Bitmap) for cls_name in classes_mapping]
    return sly.ObjClassCollection(cls_list)


def get_custom_masks_dir_name(dataset_path: str) -> list:
    dirs = [
        dir_name
        for dir_name in os.listdir(dataset_path)
        if isdir(join(dataset_path, dir_name))
        and dir_name.startswith("mask")
        and dir_name != g.MASKS_MACHINE_DIR_NAME
        and dir_name != g.MASKS_INSTANCE_DIR_NAME
        and dir_name != g.MASKS_HUMAN_DIR_NAME
    ]
    return [join(dataset_path, dir_name) for dir_name in dirs]


def get_mask_dirs(dataset_path: str) -> list:
    mask_dirs = []
    ann_dir = join(dataset_path, g.ANNOTATION_DIR_NAME)
    if exists(ann_dir):
        mask_dirs.append(ann_dir)
    masks_machine = join(dataset_path, g.MASKS_MACHINE_DIR_NAME)
    if exists(masks_machine):
        mask_dirs.append(masks_machine)
    masks_instances = join(dataset_path, g.MASKS_INSTANCE_DIR_NAME)
    if exists(masks_instances):
        mask_dirs.append(masks_instances)
    masks_custom_dir_names = get_custom_masks_dir_name(dataset_path)

    return mask_dirs + masks_custom_dir_names


def get_dataset_masks(dataset_path: str, images_names: list) -> dict:
    mask_dirs = get_mask_dirs(dataset_path)
    masks_map = {"semantic": [], "instance": []}
    mime = magic.Magic(mime=True)
    is_warned_missing = False
    dataset_name = basename(dataset_path)
    if len(mask_dirs) == 0 and dataset_name != g.DEFAULT_DS_NAME:
        sly.logger.warn(
            f"There are no mask directories for dataset: {dataset_name}. It will be uploaded without masks."
        )
    for mask_dir in mask_dirs:
        if len(os.listdir(mask_dir)) == 0:
            continue
        mask_dir_items = list(os.listdir(mask_dir))

        if len(mask_dir_items) != len(images_names) and not is_warned_missing:
            mask_dir_items_names = [get_file_name(item_name) for item_name in mask_dir_items]
            missing_masks = ", ".join(map(str, list(set(images_names) - set(mask_dir_items_names))))
            sly.logger.warn(f"Masks for images: {missing_masks} are missing.")
            is_warned_missing = True

        for item_name in mask_dir_items:
            if get_file_name(item_name) not in images_names:
                continue
            item_path = join(mask_dir, item_name)
            if isfile(item_path):
                mimetype = mime.from_file(item_path)
                if not mimetype.startswith("image"):
                    sly.logger.warn(f"{item_path} is not an image (mimetype: {mimetype})")
                masks_map["semantic"].append({get_file_name(item_name): item_path})
            else:
                instance_masks = sly.fs.list_files(item_path)
                validated_masks = []
                for mask_path in instance_masks:
                    mimetype = mime.from_file(mask_path)
                    if mimetype.startswith("image"):
                        validated_masks.append(mask_path)
                    else:
                        sly.logger.warn(f"{mask_path} is not an image (mimetype: {mimetype})")
                    masks_map["instance"].append({basename(item_path): validated_masks})

    return masks_map


def get_mask_path(masks_map: dict, images_names: list, current_image_name: str) -> tuple:
    semantic_masks = masks_map["semantic"]
    for item in semantic_masks:
        if semantic_masks != masks_map["semantic"]:
            break
        for _ in images_names:
            if semantic_masks != masks_map["semantic"]:
                break
            for k, v in item.items():
                if k == current_image_name:
                    semantic_masks = v
                    break
    if len(semantic_masks) == 0 or semantic_masks == masks_map["semantic"]:
        semantic_masks = None

    instance_masks = masks_map["instance"]
    for item in instance_masks:
        if instance_masks != masks_map["instance"]:
            break
        for _ in images_names:
            if instance_masks != masks_map["instance"]:
                break
            for k, v in item.items():
                if k == current_image_name:
                    instance_masks = v
                    break

    if len(instance_masks) == 0 or instance_masks == masks_map["instance"]:
        instance_masks = None

    return semantic_masks, instance_masks


def read_semantic_labels(
    mask_path: str, classes_mapping: dict, obj_classes: sly.ObjClassCollection
) -> list:
    mask = cv2.imread(mask_path)[:, :, 0]
    labels_list = []
    for cls_name, color in classes_mapping.items():
        if color == g.MATCH_ALL:
            bool_mask = mask > 0
        elif isinstance(color, int):
            bool_mask = mask == color
        elif isinstance(color, list):
            bool_mask = np.isin(mask, color)
        else:
            raise ValueError(
                'Wrong color format. It must be integer, list of integers or special key string "__all__".'
            )

        if bool_mask.sum() == 0:
            continue

        bitmap = sly.Bitmap(data=bool_mask)
        obj_class = obj_classes.get(cls_name)
        labels_list.append(sly.Label(geometry=bitmap, obj_class=obj_class))
    return labels_list


def read_instance_labels(mask_paths: list, obj_classes: list) -> list:
    labels = []
    for instance_mask_path in mask_paths:
        obj_class_name = re.sub(r"_\d+", "", get_file_name(instance_mask_path))
        obj_class = obj_classes.get(obj_class_name)
        bitmap = sly.Bitmap.from_path(instance_mask_path)
        label = sly.Label(geometry=bitmap, obj_class=obj_class)
        labels.append(label)
    return labels


def convert_project(
    project_path: str,
    new_project_path: str,
    project_meta: sly.ProjectMeta,
    classes_map: dict,
) -> sly.Project:
    project = sly.Project(directory=new_project_path, mode=sly.OpenMode.CREATE)
    project.set_meta(project_meta)
    dataset_names, dataset_paths = get_datasets(project_path=project_path)
    ds_progress = sly.Progress("Processing Datasets", len(dataset_names))
    for dataset_name, dataset_path in zip(dataset_names, dataset_paths):
        dataset = project.create_dataset(dataset_name)
        img_dir = join(dataset_path, g.IMAGE_DIR_NAME)
        images_names = [get_file_name(file_name) for file_name in os.listdir(img_dir)]
        images_names_with_ext = [
            get_file_name_with_ext(file_name) for file_name in os.listdir(img_dir)
        ]
        images_paths = [join(img_dir, file_name) for file_name in os.listdir(img_dir)]
        masks_map = get_dataset_masks(dataset_path, images_names)

        progress = sly.Progress("Dataset: {!r}".format(dataset_name), len(images_paths))
        for image_name, image_name_with_ext, image_path in zip(
            images_names, images_names_with_ext, images_paths
        ):
            try:
                ann = sly.Annotation.from_img_path(img_path=image_path)
                semantic_mask_path, instance_masks_paths = get_mask_path(
                    masks_map=masks_map,
                    images_names=images_names,
                    current_image_name=image_name,
                )
                semantic_labels = []
                if semantic_mask_path is not None:
                    semantic_labels = read_semantic_labels(
                        mask_path=semantic_mask_path,
                        classes_mapping=classes_map,
                        obj_classes=project_meta.obj_classes,
                    )
                instance_labels = []
                if instance_masks_paths is not None:
                    instance_labels = read_instance_labels(
                        mask_paths=instance_masks_paths,
                        obj_classes=project_meta.obj_classes,
                    )
                ann = ann.add_labels(labels=semantic_labels + instance_labels)
                dataset.add_item_file(item_name=image_name_with_ext, item_path=image_path, ann=ann)

            except Exception as e:
                exc_str = str(e)
                sly.logger.warn(
                    f"Input sample skipped due to error: {exc_str}",
                    exc_info=True,
                    extra={"exc_str": exc_str, "image": image_path},
                )
            progress.iter_done_report()
        ds_progress.iter_done_report()
    return project


def upload_project(
    api: sly.Api,
    task_id: int,
    local_project: sly.Project,
    project_name: str,
    local_project_path: str,
) -> None:
    if g.PROJECT_ID is None:
        project_id, project_name = sly.upload_project(
            dir=local_project_path,
            api=api,
            workspace_id=g.WORKSPACE_ID,
            project_name=project_name,
            log_progress=True,
        )
        api.task.set_output_project(
            task_id=task_id, project_id=project_id, project_name=project_name
        )
    elif g.DATASET_ID is not None:
        datasets = local_project.datasets
        dataset_name = g.api.dataset.get_info_by_id(g.DATASET_ID).name
        for dataset in datasets:
            all_images_names = dataset.get_items_names()
            progress = sly.Progress(
                message=f"Upload images to dataset: {dataset_name}",
                total_cnt=len(all_images_names),
            )
            batch_upload(
                api=api,
                task_id=task_id,
                ds_images_names=all_images_names,
                dataset=dataset,
                dst_dataset_id=g.DATASET_ID,
                project_name=project_name,
                progress=progress,
            )

    else:
        datasets = local_project.datasets
        for dataset in datasets:
            dst_dataset = g.api.dataset.create(
                project_id=g.PROJECT_ID, name=dataset.name, change_name_if_conflict=True
            )
            all_images_names = dataset.get_items_names()
            progress = sly.Progress(
                message=f"Upload images to dataset: {dst_dataset.name}",
                total_cnt=len(all_images_names),
            )
            batch_upload(
                api=api,
                task_id=task_id,
                ds_images_names=all_images_names,
                dataset=dataset,
                dst_dataset_id=dst_dataset.id,
                project_name=project_name,
                progress=progress,
            )


def batch_upload(
    api: sly.Api,
    task_id: int,
    ds_images_names: list,
    dataset: sly.Dataset,
    dst_dataset_id: int,
    project_name: str,
    progress: sly.Progress,
) -> None:
    for batch in sly.batched(ds_images_names):
        batched_images_names = []
        batched_images_paths = []
        batched_anns_paths = []
        for image_name in batch:
            batched_images_names.append(image_name)
            batched_images_paths.append(dataset.get_img_path(image_name))
            batched_anns_paths.append(dataset.get_ann_path(image_name))
        images_infos = g.api.image.upload_paths(
            dataset_id=dst_dataset_id,
            names=batched_images_names,
            paths=batched_images_paths,
        )
        images_ids = [image_info.id for image_info in images_infos]
        g.api.annotation.upload_paths(img_ids=images_ids, ann_paths=batched_anns_paths)
        progress.iters_done_report(len(batch))

    api.task.set_output_project(task_id=task_id, project_id=g.PROJECT_ID, project_name=project_name)
