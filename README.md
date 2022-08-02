<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48913536/182420556-a6d0abb6-0982-4206-af34-cf39fc0a6f2b.png"/>

# Import Images with Masks

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>

[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/export-as-masks)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/export-as-masks)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/export-as-masks)](https://supervise.ly)

</div>

## Overview

Import images with binary masks as annotations. App supports both semantic and instance segmentation masks. App requires `obj_class_to_machine_color.json` file to match classes and colors, otherwise app won't start. Backward compatible with [`export as masks`](https://github.com/supervisely-ecosystem/export-as-masks) app.

**`obj_class_to_machine_color.json`** example:

```json
{
   "Lemon": 170,
   "Kiwi": 85
}
```

In this configuration example all pixels in the mask which value **equal to 170** will be combined in one Bitmap figure and will be assigned to the class **"Lemon"** and **equal to 85** will be assigned to the class **"Kiwi"**.

![](https://i.imgur.com/a5cVpAB.png)


**Import data structure:**

* img - contains original images.
* ann - contains binary masks, you can place both semantic and instance segmentation here.
* masks_machine - contains semantic segmentation masks.
* masks_instance - contains for instance segmentation masks.
* mask* - you can create a directory with a custom name that should starts with "mask".

**Instance masks structure**

For example we have an image with 2 cats on it placed in `dataset_name/img/**cats_1.jpg**` directory, and we have instance masks for them placed in `dataset_name/mask_instances/**cats_1**/cat_1.png` and `dataset_name/mask_instances/**cats_1**/cat_2.png`.
Subdirectories in `mask_instances` folder define to which original image this masks belong to. Masks names inside these subdirectories defines names of the class.
As a result we will have an image `cats_1.jpg` with 2 labels `cat` and `cat`.

<div align="center" markdown>
  <img src="https://user-images.githubusercontent.com/48913536/182435346-a57da6a0-15d0-4f24-a17d-9063bc962b57.png" width="500"/>
</div>

### ⚠️ Notice  
If you just want to import semantic segmentation masks, just drag & drop original images, semantic segmentation masks and obj_class_to_machine_color.json file. Same for instance segmentation masks, you don't have to create all directories if this is unnessecary.

Input data structure example:

```text
Drag & Drop                                     From Team Files
                                            
.                                              directory_with_import_data
├── obj_class_to_machine_color.json            ├── obj_class_to_machine_color.json
├── cats                                       ├── cats
│   ├── ann                                    │   ├── ann
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
* a new project will be created with 2 datasets: cats, dogs
* 2 classes: cat, dog. Images names in `mask_machine` directory must match original images names in `img` directory
* Subdirectories in `mask_instances` directory must match original images names in `img` directory without extensions
* Instance masks names define class name

## How To Run
### Run from Ecosystem:

**Step 1**: Add app to your team from [Ecosystem](https://app.supervise.ly/apps/ecosystem/export-as-masks) if it is not there

**Step 2**: Open context menu of images project -> `Download via App` -> `Export as masks` 

<img src="" width="500"/>

**Step 3**: Define export settings in modal window

### Run from Images Project:

**Step 1**: Add app to your team from [Ecosystem](https://app.supervise.ly/apps/ecosystem/export-as-masks) if it is not there

**Step 2**: Open context menu of images project -> `Download via App` -> `Export as masks` 

<img src="" width="500"/>

**Step 3**: Define export settings in modal window

### Run from Images Dataset:

**Step 1**: Add app to your team from [Ecosystem](https://app.supervise.ly/apps/ecosystem/export-as-masks) if it is not there

**Step 2**: Open context menu of images project -> `Download via App` -> `Export as masks` 

<img src="" width="500"/>

**Step 3**: Define export settings in modal window




# Import Images with Masks

This app allows you to upload images with annotations in the format of PNG masks. Masks are 3-(1-)channel images containing only pixels that have the same values in all channels. To map pixels masks with appropriate class you can use specific config:

#### Example 1.

```json
{
    "Lemon": 170,
    "Kiwi": 85
  }
```

In this configuration example all pixels in the mask which value **equal to 170** will be combined in one Bitmap figure and will be assigned to the class **"Lemon"** and **equal to 85** will be assigned to the class **"Kiwi"**.

![](https://i.imgur.com/a5cVpAB.png)

##### Result:

![](https://i.imgur.com/s2MWqFF.png)


#### Example 2.

```json
{
  "classes_mapping": {
    "Fruits": [85, 170],
    "Car": 3
  }
}
```

In this case all pixels in the mask which value **equal to 85 or 170** will be combined in one Bitmap figure and will be assigned to the class **"Fruits"** and all pixels **equal to 3** will be assinged to the class **"Car"**.

#### Example 3.

```json
{
  "classes_mapping": {
    "objects": "__all__"
  }
}
```

In this case all pixels in the mask which value **greater than 0** will be combined in one Bitmap figure and will be assigned to the class "objects":

![](https://i.imgur.com/fCL4lSN.png)

Also you don't have to specify any configs, in this case default config will be used:

```json
{
  "classes_mapping": {
    "untitled": "__all__"
  }
}
```

Images should be in the folder `"img"` and mask should be in the folder `"ann"` and should have the same name as the images(but may have a different extension). All images will be  placed in dataset **ds**.

File structure that can be uploaded by this plugin should look like this:

```
.
├── ann
│   ├── image_1.png
│   ├── image_2.png
│   └── image_3.png
└── img
    ├── image_1.png
    ├── image_2.png
    └── image_3.png

```
