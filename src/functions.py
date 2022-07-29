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


def get_project_name_from_input_path(input_path: str) -> str:
    full_path_dir = dirname(input_path)
    return basename(full_path_dir)


def download_project(api: sly.Api, input_path: str) -> tuple:
    remote_proj_dir = input_path
    original_project_path = f"{g.STORAGE_DIR}/original_data/"
    converted_project_path = f"{g.STORAGE_DIR}{remote_proj_dir}/"
    if not exists(original_project_path):
        api.file.download_directory(
            g.TEAM_ID,
            remote_path=remote_proj_dir,
            local_save_path=original_project_path,
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
    return dataset_names, dataset_paths


def get_class_color_map(project_path: str) -> dict:
    class_color_map_path = join(project_path, "classes_mapping.json")
    if not exists(class_color_map_path):
        raise FileNotFoundError("Classes mapping not found.")
    return load_json_file(class_color_map_path)


def get_or_create_project_meta(
    project_path: str, classes_mapping: dict
) -> sly.ProjectMeta:
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
    ann_dir = join(dataset_path, g.ANNOTATION_DIR_NAME)
    masks_machine = join(dataset_path, g.MASKS_MACHINE_DIR_NAME)
    masks_instances = join(dataset_path, g.MASKS_INSTANCE_DIR_NAME)
    masks_custom_dir_names = get_custom_masks_dir_name(dataset_path)
    return [ann_dir, masks_machine, masks_instances] + masks_custom_dir_names


def get_dataset_masks(dataset_path: str, images_names: list) -> dict:
    mask_dirs = get_mask_dirs(dataset_path)
    masks_map = {"semantic": [], "instance": []}
    mime = magic.Magic(mime=True)
    for mask_dir in mask_dirs:
        if len(os.listdir(mask_dir)) == 0:
            continue
        mask_dir_items = list(os.listdir(mask_dir))
        for item_name in mask_dir_items:
            item_path = join(mask_dir, item_name)
            if not isdir(item_path):
                mimetype = mime.from_file(item_path)

            # def validate_item(item_path):
            if get_file_name(item_name) not in images_names:
                continue

            if not mimetype.startswith("image"):
                sly.logger.warn(f"{item_path} is not an image (mimetype: {mimetype})")
                continue
            if isdir(item_path):
                instance_masks = sly.fs.list_files(item_path)
                masks_map["instance"].append({basename(item_path): instance_masks})
            if isfile(item_path):
                masks_map["semantic"].append({get_file_name(item_name): item_path})
    return masks_map


def get_mask_path(masks_map: dict, image_name: str) -> tuple:
    semantic_masks = masks_map["semantic"]
    for item in semantic_masks:
        for k, v in item.items():
            if k == image_name:
                semantic_masks = v
                break

    instance_masks = masks_map["instance"]
    for item in instance_masks:
        for k, v in item.items():
            if k == image_name:
                instance_masks = v
                break
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


def read_instance_labels(instance_masks_paths: list, obj_classes: list) -> list:
    labels = []
    for instance_mask_path in instance_masks_paths:
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
):
    project = sly.Project(directory=new_project_path, mode=sly.OpenMode.CREATE)
    project.set_meta(project_meta)
    dataset_names, dataset_paths = get_datasets(project_path=project_path)
    for dataset_name, dataset_path in zip(dataset_names, dataset_paths):
        dataset = project.create_dataset(dataset_name)

        img_dir = join(dataset_path, g.IMAGE_DIR_NAME)
        images_names = [get_file_name(file_name) for file_name in os.listdir(img_dir)]
        images_names_with_ext = [
            get_file_name_with_ext(file_name) for file_name in os.listdir(img_dir)
        ]
        images_paths = [join(img_dir, file_name) for file_name in os.listdir(img_dir)]
        masks_map = get_dataset_masks(dataset_path, images_names)

        progress = sly.Progress(
            "Dataset: {!r}".format(g.DEFAULT_DATASET_NAME), len(images_paths)
        )
        for image_name, images_name_with_ext, image_path in zip(
            images_names, images_names_with_ext, images_paths
        ):
            try:
                ann = sly.Annotation.from_img_path(image_path)
                semantic_mask_path, instance_masks_paths = get_mask_path(
                    masks_map, image_name
                )
                semantic_labels = read_semantic_labels(
                    semantic_mask_path, classes_map, project_meta.obj_classes
                )
                instance_labels = read_instance_labels(
                    instance_masks_paths, project_meta.obj_classes
                )
                labels = semantic_labels + instance_labels
                ann = ann.add_labels(labels)
                dataset.add_item_file(
                    item_name=images_name_with_ext, item_path=image_path, ann=ann
                )
            except Exception as e:
                exc_str = str(e)
                sly.logger.warn(
                    f"Input sample skipped due to error: {exc_str}",
                    exc_info=True,
                    extra={"exc_str": exc_str, "image": image_path},
                )

            progress.iter_done_report()

        if masks_map:
            masks_list = list(masks_map.values())
            sly.logger.warning(f"Images for masks doesn't exist. Masks: {masks_list}")
