import cv2
import numpy as np
import os

from os.path import join
from PIL import Image
from typing import List, Dict

import supervisely as sly
from supervisely.io.json import load_json_file

import globals as g


def get_project_name_from_input_path(input_path: str) -> str:
    full_path_dir = os.path.dirname(input_path)
    return os.path.basename(full_path_dir)


def download_project(api, input_path):
    remote_proj_dir = input_path
    original_project_path = f"{g.STORAGE_DIR}/original_data/"
    converted_project_path = f"{g.STORAGE_DIR}{remote_proj_dir}/"
    api.file.download_directory(
        g.TEAM_ID, remote_path=remote_proj_dir, local_save_path=original_project_path
    )
    return original_project_path, converted_project_path


def get_datasets(project_path):
    dataset_names = []
    dataset_paths = []
    for dataset_name in os.listdir(project_path):
        dataset_path = os.path.join(project_path, dataset_name)
        if os.path.isdir(dataset_path):
            dataset_names.append(dataset_name)
            dataset_paths.append(dataset_path)
    return dataset_names, dataset_paths


def get_class_color_map(project_path):
    class_color_map_path = os.path.join(project_path, "classes_mapping.json")
    if not os.path.exists(class_color_map_path):
        raise FileNotFoundError("Classes mapping not found.")
    return load_json_file(class_color_map_path)


def get_or_create_project_meta(project_path, classes_mapping):
    project_meta_path = os.path.join(project_path, "meta.json")
    if os.path.exists(project_meta_path):
        return load_json_file(project_meta_path)
    obj_class_collection = create_obj_class_collection(classes_mapping)
    return sly.ProjectMeta(obj_classes=obj_class_collection)



def create_obj_class_collection(classes_mapping: Dict) -> sly.ObjClassCollection:
    cls_list = [sly.ObjClass(cls_name, sly.Bitmap) for cls_name in classes_mapping.keys()]
    return sly.ObjClassCollection(cls_list)


def read_mask_labels(mask_path: str, classes_mapping: Dict, obj_classes: sly.ObjClassCollection) -> List[sly.Label]:
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
                'Wrong color format. It must be integer, list of integers or special key string "__all__".')

        if bool_mask.sum() == 0:
            continue

        bitmap = sly.Bitmap(data=bool_mask)
        obj_class = obj_classes.get(cls_name)
        labels_list.append(sly.Label(geometry=bitmap, obj_class=obj_class))
    return labels_list


def convert_masks_to_anns(project_path, project_meta, classes_map):
    dataset_names, dataset_paths = get_datasets(project_path=project_path)
    for dataset_path in dataset_paths:
        img_dir = join(dataset_path, g.IMAGE_DIR_NAME)
        ann_dir = join(dataset_path, g.ANNOTATION_DIR_NAME)
        masks_machine = join(dataset_path, g.MASKS_MACHINE_DIR_NAME)
        masks_instances = join(dataset_path, g.MASKS_INSTANCE_DIR_NAME)
        # masks_etc = join(dataset_path, g.ANNOTATION_DIR_NAME)

        class_color_map_path = os.path.join(project_path, "classes_mapping.json")
        tasks_settings = load_json_file(class_color_map_path)

        classes_mapping = g.DEFAULT_CLASSES_MAPPING
        if g.CLASSES_MAPPING_KEY in tasks_settings:
            classes_mapping = tasks_settings[g.CLASSES_MAPPING_KEY]
        else:
            sly.logger.warn(f'Classes mapping not found. Set to default: {str(g.DEFAULT_CLASSES_MAPPING)}')



        # pr = sly.Project(converted_project_path, sly.OpenMode.CREATE)
        # obj_class_collection = create_obj_class_collection(classes_mapping)
        # pr_meta = sly.ProjectMeta(obj_classes=obj_class_collection)
        # pr.set_meta(pr_meta)
        # ds = pr.create_dataset(g.DEFAULT_DATASET_NAME)

        images_pathes = sly.fs.list_files(img_dir)
        masks_pathes = sly.fs.list_files(ann_dir)
        masks_map = {sly.fs.get_file_name(mask_p): mask_p for mask_p in masks_pathes}

        progress = sly.Progress('Dataset: {!r}'.format(g.DEFAULT_DATASET_NAME), len(images_pathes))
        for img_fp in images_pathes:
            full_img_fp = join(img_dir, img_fp)
            try:
                image_name = os.path.basename(full_img_fp)
                sample_name = sly.fs.get_file_name(full_img_fp)
                ann = sly.Annotation.from_img_path(full_img_fp)
                mask_name = masks_map.pop(sample_name, None)
                if mask_name is None:
                    sly.logger.warning(f"Mask for image {sample_name} doesn\'t exist.")
                else:
                    full_mask_fp = join(ann_dir, mask_name)
                    labels = read_mask_labels(full_mask_fp, classes_mapping, obj_class_collection)
                    ann = ann.add_labels(labels)

                ds.add_item_file(image_name, full_img_fp, ann=ann)
            except Exception as e:
                exc_str = str(e)
                sly.logger.warn(f'Input sample skipped due to error: {exc_str}', exc_info=True,
                                extra={'exc_str': exc_str, 'image': full_img_fp})

            progress.iter_done_report()

        if masks_map:
            masks_list = list(masks_map.values())
            sly.logger.warning(f"Images for masks doesn\'t exist. Masks: {masks_list}")
