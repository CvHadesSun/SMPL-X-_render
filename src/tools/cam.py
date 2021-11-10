'''
Author: cvhades
Date: 2021-11-10 15:10:24
LastEditTime: 2021-11-10 15:13:31
LastEditors: Please set LastEditors
FilePath: /PG-engine/src/tools/cam.py
'''


import bpy
import math
from mathutils import Matrix, Euler

def set_camera(cam_dist=7, cam_height=1, zrot_euler=0):
    # set camera properties and initial position
    bpy.ops.object.select_all(action="DESELECT")
    cam_ob = bpy.data.objects["Camera"]  # scn.camera
    # bpy.context.scene.objects.active = cam_ob  # blender < 2.8x
    bpy.context.view_layer.objects.active = cam_ob

    rot_z = math.radians(zrot_euler)
    rot_x = math.atan((cam_height - 1) / cam_dist)
    # Rotate -90 degrees around x axis to have the person face cam
    cam_rot = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0))).to_4x4()
    # Rotation by zrot_euler around z-axis
    cam_rot_z = Euler((0, rot_z, 0), "XYZ").to_matrix().to_4x4()
    cam_rot_x = Euler((rot_x, 0, 0), "XYZ").to_matrix().to_4x4()

    # Rotate around the object by rot_z with a fixed radius = cam_dist
    cam_trans = Matrix.Translation(
        [cam_dist * math.sin(rot_z), cam_dist * math.cos(rot_z), cam_height]
    )

    # cam_ob.matrix_world = cam_trans * cam_rot * cam_rot_z * cam_rot_x  # blender < 2.8x
    cam_ob.matrix_world = cam_trans @ cam_rot @ cam_rot_z @ cam_rot_x

    cam_ob.data.angle = math.radians(40)
    cam_ob.data.lens = 60
    cam_ob.data.clip_start = 0.1
    cam_ob.data.sensor_width = 32
    # print("Camera location {}".format(cam_ob.location))
    # print("Camera rotation {}".format(cam_ob.rotation_euler))
    # print("Camera matrix {}".format(cam_ob.matrix_world))
    return cam_ob