<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48913536/182420556-a6d0abb6-0982-4206-af34-cf39fc0a6f2b.png"/>

# Import Images with Masks

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>

[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-images-with-masks)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/import-images-with-masks.png)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/import-images-with-masks.png)](https://supervisely.com)

</div>

## Overview

🗄️ Starting from version 1.0.11 the application supports the import of multiple projects at once. Each project should be placed in a separate directory with the correct structure (see below).

This app allows you to upload images with annotations in the format of PNG masks. Masks are 3-(1-)channel images containing only pixels that have the same values in all channels, to map pixels masks with appropriate class app requires `obj_class_to_machine_color.json` file to match classes and colors, otherwise app won't start.
App supports both semantic and instance segmentation masks. Backward compatible with [`export as masks`](https://github.com/supervisely-ecosystem/export-as-masks) app.

Images should be in the folder `"img"` and masks should be in one (or more) of the following folders below:

- `ann` - contains binary masks, you can place both semantic and instance segmentation here.
- `masks_machine` - contains semantic segmentation masks. Masks for semantic segmentation should have the same name as the original images (but may have a different extension e.g original image name: `cats_1.jpg` -> mask name `cats_1.png`).
- `masks_instance` - contains for instance segmentation masks. Masks for instance segmentation must be placed in the subdirectories that have the same name as the original images (but without extension e.g original image name: `cats_1.jpg` -> subdirectory name `cats_1`).
- `mask*` - you can create a directory with a custom name that should starts with "mask".

**Demo project ([download](https://github.com/supervisely-ecosystem/import-images-with-masks/releases/download/0.0.1/demo_project.zip))**

**`obj_class_to_machine_color.json`** example:

```json
{
  "Lemon": 170,
  "Kiwi": 85
}
```

**Semantic (machine) masks example**

In this configuration example all pixels in the mask which value **equal to 170** will be combined in one Bitmap figure and will be assigned to the class **"Lemon"** and **equal to 85** will be assigned to the class **"Kiwi"**.

![](https://i.imgur.com/a5cVpAB.png)

**Instance masks example**

For example we have an image with 2 cats on it placed in `dataset_name/img/**cats_1.jpg**` directory, and we have instance masks for them placed in `dataset_name/mask_instances/**cats_1**/cat_1.png` and `dataset_name/mask_instances/**cats_1**/cat_2.png`.
Subdirectories in `mask_instances` folder define to which original image this masks belong to. Masks names inside these subdirectories defines names of the class.
As a result we will have an image `cats_1.jpg` with 2 labels `cat` and `cat`.

<div align="center" markdown>
  <img src="https://user-images.githubusercontent.com/48913536/182435346-a57da6a0-15d0-4f24-a17d-9063bc962b57.png" width="500"/>
</div>

### ⚠️ Notice

If you just want to import semantic segmentation masks, just drag & drop original images, semantic segmentation masks and obj_class_to_machine_color.json file. Same for instance segmentation masks, you don't have to create all directories if this is unnessecary.

**Input data structure example:**

**1. Images in datasets (new dataset will be created for each folder in the root of imported data)**<br>
ℹ️ You can download the archive with data example [here](https://github.com/supervisely-ecosystem/import-images-with-masks/files/12546340/lemons-project.zip).

```text
Drag & Drop                                     From Team Files

.                                              directory_with_import_data
├── obj_class_to_machine_color.json            ├── obj_class_to_machine_color.json
├── cats                                       ├── cats
│   ├── img                                    │   ├── img
│   │   ├── cats_1.jpg                         │   │   ├── cats_1.jpg
│   │   ├── ...                                │   │   ├── ...
│   │   └── cats_9.jpg                         │   │   └── cats_9.jpg
│   ├── masks_human                            │   ├── masks_human
│   │   ├── cats_1.png                         │   │   ├── cats_1.png
│   │   ├── ...                                │   │   ├── ...
│   │   └── cats_9.png                         │   │   └── cats_9.png
│   ├── masks_instances                        │   ├── masks_instances
│   │   ├── cats_1                             │   │   ├── cats_1
│   │   │   ├── cat_1.png                      │   │   │   ├── cat_1.png
│   │   │   ├── ...                            │   │   │   ├── ...
│   │   │   └── cat_9.png                      │   │   │   └── cat_9.png
│   │   ├── ...                                │   │   ├── ...
│   │   └── cats_9                             │   │   └── cats_9
│   │       ├── cat_1.png                      │   │       ├── cat_1.png
│   │       ├── ...                            │   │       ├── ...
│   │       └── cas_9.png                      │   │       └── cat_9.png
│   └── masks_machine                          │   └── masks_machine
│       ├── cats_1.png                         │       ├── cats_1.png
│       ├── ...                                │       ├── ...
│       └── cats_9.png                         │       └── cats_9.png
└── dogs                                       └── dogs
    ├── img                                        ├── img
    │   ├── dogs_1.jpg                             │   ├── dogs_1.jpg
    │   ├── ...                                    │   ├── ...
    │   └── dogs_9.jpg                             │   └── dogs_9.jpg
    ├── masks_human                                ├── masks_human
    │   ├── dogs_1.png                             │   ├── dogs_1.png
    │   ├── ...                                    │   ├── ...
    │   └── dogs_9.png                             │   └── dogs_9.png
    ├── masks_instances                            ├── masks_instances
    │   ├── dogs_1                                 │   ├── dogs_1
    │   │   ├── dog_1.png                          │   │   ├── dog_1.png
    │   │   ├── ...                                │   │   ├── ...
    │   │   └── dog_9.png                          │   │   └── dog_9.png
    │   ├── ...                                    │   ├── ...
    │   └── dogs_9                                 │   └── dogs_9
    │       ├── dog_1.png                          │       ├── dog_1.png
    │       ├── ...                                │       ├── ...
    │       └── dog_9.png                          │       └── dog_9.png
    └── masks_machine                              └── masks_machine
        ├── dogs_1.png                                 ├── dogs_1.png
        ├── ...                                        ├── ...
        └── dogs_9.png                                 └── dogs_9.png
```

In this configuration example if we run app from Ecosystem without specified project:

- a new project will be created with 2 datasets: cats, dogs
- 2 classes: cat, dog. Images names in `mask_machine` directory must match original images names in `img` directory
- Subdirectories in `mask_instances` directory must match original images names in `img` directory without extensions
- Instance masks names define class name

**2. Only images with masks (all images will be placed in "ds0")**

```text
Drag & Drop                                     From Team Files
.                                               directory in team files with import data
├── obj_class_to_machine_color.json             ├── obj_class_to_machine_color.json
├── ann                                         ├── ann
│   ├── image_1.png                             │   ├── image_1.png
│   ├── image_2.png                             │   ├── image_2.png
│   └── image_3.png                             │   └── image_3.png
└── img                                         └── img
    ├── image_1.png                                 ├── image_1.png
    ├── image_2.png                                 ├── image_2.png
    └── image_3.png                                 └── image_3.png
```

## How To Run

### Run from Ecosystem:

**Step 1**: Locate the app in Ecosystem and run it

<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48913536/182564917-5f4fe6df-3c0a-4dcd-bffa-0bcf199fbf9c.png"/>
</div>

**Step 2**: Drag & drop your data, or select already uploaded folder with data from `Team Files`, select options in the modal window and press the `Run` button, you will be redirected to the `Workspace tasks` page.

<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48913536/182564940-12e22c6b-dda0-44b5-bd28-abd2a57aaccf.png" width="700px"/>
</div>

**Step 3**: Wait for the app to process your data, once done, link to your project will become available

<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48913536/182564948-521faa8f-4dce-4155-8b07-fed106290f54.png"/>
</div>

### Import to existing Images Project:

**Step 1**: Open context menu of images project -> `Run app` -> `Import` -> `Import images with masks`

<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48913536/182565103-f0cf16fd-b5ae-4032-b33c-db12d5d2da9a.png"/>
</div>

**Step 2**: Drag & drop your data, or select already uploaded folder with data from `Team Files`, select options in the modal window and press the `Run` button, you will be redirected to the `Workspace tasks` page.

<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48913536/182565113-a72d4168-464f-4ecc-ae53-4d40a5dd4565.png" width="700px"/>
</div>

**Step 3**: Wait for the app to process your data, once done, link to your project will become available

<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48913536/182565120-2ef09bd5-295c-4189-9a99-eff9009222d5.png"/>
</div>

### Import to existing Images Dataset:

**Step 1**: Open context menu of images dataset -> `Run app` -> `Import` -> `Import images with masks`

<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48913536/182565145-793fe6fd-a53d-44ba-913c-1ccc0d0ca9d4.png"/>
</div>

**Step 2**: Drag & drop your data, or select already uploaded folder with data from `Team Files`, select options in the modal window and press the `Run` button, you will be redirected to the `Workspace tasks` page.

<div align="center" markdown>
  <img src="https://user-images.githubusercontent.com/48913536/182565154-f42bbe0b-0c01-4308-8371-164e712a304d.png" width="700px"/>
</div>

**Step 3**: Wait for the app to process your data, once done, link to your project will become available

<div align="center" markdown>
  <img src="https://user-images.githubusercontent.com/48913536/182565161-e4c20736-7cd2-45cb-85e7-95e9d7522ed1.png"/>
</div>
