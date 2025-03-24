# GameDev Pipeline Toolkit 1.10

![Blender 3.0+](https://img.shields.io/badge/blender-3.0%2B-orange.svg)

**GameDev Pipeline Toolkit** is a premium Blender add-on designed to streamline your game development workflow. It offers a fully customizable folder structure, flexible triangulation options, seamless FBX export iterations for both Unity and Unreal Engine, Substance 3D naming conventions, duplicate suffix handling, and more. Ideal for both solo developers and larger teams, this toolkit enhances productivity and maintains organization throughout your pipeline.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Project Setup](#project-setup)
  - [Folder Structure Management](#folder-structure-management)
  - [Exporting Models](#exporting-models)
  - [Substance 3D Naming](#substance-3d-naming)
- [Triangulation Methods](#triangulation-methods)
- [Configuration](#configuration)
- [Purchase](#purchase)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- **Customizable Folder Structure:** Define and create a tailored folder hierarchy for your project.
- **Flexible Triangulation:** Choose between non-destructive and destructive triangulation methods.
- **FBX Export Iteration:** Automatically increment export filenames to keep track of versions.
- **Substance 3D Naming:** Apply consistent naming conventions with `_low` and `_high` suffixes.
- **Duplicate Suffix Handling:** Manage Blender’s automatic `.001`, `.002` suffixes with ease.
- **Seamless Integration:** Access all tools directly from the 3D View's N-Panel under the **GameDev Toolkit** tab.

## Installation



 **Download the Add-on:**
   - Download/clone the ZIP file.
     
 **Install in Blender:**
   - Open Blender.
   - Go to `Edit > Preferences > Add-ons`.
   - Click `Install...` and navigate to the downloaded ZIP file.
   - Select the ZIP file and click `Install Add-on`.
   - Enable the add-on by checking the box next to **GameDev Pipeline Toolkit**.

## Usage

Once installed and enabled, you can access the **GameDev Toolkit** from the N-Panel in the 3D View.

### Project Setup

 **Root Path:** Specify the directory where your main project folder will reside (e.g., your Unity or Unreal project directory).
 **Project Name:** Define the name of your project folder (e.g., `SciFiWeapon`).


 **Create Folder Structure:** Click the `Create Folder Structure` button to generate the predefined folders within your project directory.
 **Open Project Folder:** Easily open your project folder in your system's file explorer.

### Folder Structure Management

 **Subfolder List:** Manage your project's subfolders directly within the add-on preferences.
 **Add/Remove Folders:** Use the `+` and `-` buttons to add or remove folders from the list.
 **Reorder Folders:** Use the up and down arrows to arrange the folder order as needed.

### Exporting Models

#### Export for Unity

 **Select Objects:** Choose the mesh objects you wish to export.
 **Export Settings:** Configure export options such as export folder, base filename, and iteration settings.
 **Export:** Click the `Export for Unity` button to export your models with Unity-friendly FBX settings.

#### Export for Unreal

 **Select Objects:** Choose the mesh objects you wish to export.
 **Export Settings:** Configure export options specific to Unreal Engine.
 **Export:** Click the `Export for Unreal` button to export your models with Unreal-friendly FBX settings.

### Substance 3D Naming

 **Enable Naming:** In the add-on preferences, enable `Use Substance 3D Naming`.
 **Configure Suffixes:** Define the suffixes for low-poly (`_low`) and high-poly (`_high`) meshes.
 **Rename Objects:** Use the `Rename Selected (Low)` and `Rename Selected (High)` buttons in the N-Panel to apply naming conventions to selected objects.

## Triangulation Methods

Choose how meshes are triangulated during export:

- **Off:** No triangulation; export meshes as-is.
- **FBX Export Only:** Utilize Blender’s built-in FBX triangulation non-destructively.
- **Non-Destructive Duplication:** Duplicate and triangulate meshes without altering the originals.
- **Destructive:** Permanently triangulate selected meshes in the scene.

## Configuration

Access the add-on preferences to customize various settings:

- **Folder Structure:** Define the subfolders to be created within your project directory.
- **Export Settings:** Configure export directories, base filenames, and iteration preferences for both Unity and Unreal exports.
- **Triangulation Method:** Select your preferred triangulation approach.
- **Substance 3D Naming:** Enable and configure naming conventions for Substance 3D workflows.
- **Duplicate Suffix Handling:** Choose how to handle Blender’s automatic duplication suffixes.


## Acknowledgements

- Inspired by the need for a streamlined game development pipeline in Blender.
- Thanks to the Blender community for their continuous support and contributions.

---

*Happy Developing!*
