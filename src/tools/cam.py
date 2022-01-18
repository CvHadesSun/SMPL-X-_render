'''
Author: cvhades
Date: 2021-11-10 15:10:24
LastEditTime: 2022-01-18 17:56:38
LastEditors: cvhadessun
FilePath: /PG-engine/src/tools/cam.py
'''


import bpy
import math
from mathutils import Matrix, Euler
import numpy as np
import mathutils

def set_camera(cam_dist=7, cam_height=1, zrot_euler=0):
    # set camera properties and initial position
    bpy.ops.object.select_all(action="DESELECT")
    cam_ob = bpy.data.objects["Camera"]  # scn.camera
    # bpy.context.scene.objects.active = cam_ob  # blender < 2.8x
    bpy.context.view_layer.objects.active = cam_ob

    rot_z = math.radians(zrot_euler)
    rot_x = math.atan((cam_height - 1) / cam_dist)
    # Rotate -90 degrees around x axis to have the person face cam
    cam_rot = Matrix(((1, 0, 0), (0, 0, 1), (0, 1, 0))).to_4x4()
    # Rotation by zrot_euler around z-axis
    cam_rot_z = Euler((0, rot_z, 0), "XYZ").to_matrix().to_4x4()
    cam_rot_x = Euler((rot_x, 0, 0), "XYZ").to_matrix().to_4x4()

    # Rotate around the object by rot_z with a fixed radius = cam_dist
    cam_trans = Matrix.Translation(
        [cam_dist * math.sin(rot_z), cam_dist * math.cos(rot_z), cam_height]
    )

    # cam_ob.matrix_world = cam_trans * cam_rot * cam_rot_z * cam_rot_x  # blender < 2.8x
    cam_ob.matrix_world = cam_trans @ cam_rot @ cam_rot_z @ cam_rot_x

    cam_ob.data.angle = math.radians(60)
    cam_ob.data.lens = 60
    cam_ob.data.clip_start = 0.1
    cam_ob.data.sensor_width = 32
    # print("Camera location {}".format(cam_ob.location))
    # print("Camera rotation {}".format(cam_ob.rotation_euler))
    # print("Camera matrix {}".format(cam_ob.matrix_world))
    return cam_ob



def create_cameras_array(H,R,number_rank,number_per_rank,ground_z):
    '''
    @input:
        H: the cameras array's height
        R: the cameras array's max circle radius
        number_rank: the number of different height cameras' circles
        number_per_rank: camera number of per cameras' circle 
        ground_z: z-axis location for ground, the height of camera array is 0.
    @return:
        camera_queue: the cameras array queue.
    '''
    context = bpy.context
    scene = context.scene
    coll = bpy.data.collections.new("CameraArray") # 
    scene.collection.children.link(coll) 

    camera_queue = []
    #
    def create_cam(h,r,num_camera,project_h,ith_rank):
        # create a camera circle. 
        # set camera and copy 
        angle_x = math.atan2(project_h-h,r) + math.radians(90.0)
        rot_loc=[angle_x,0,math.radians(90.0),r,0,h]
        # setupCamera(scene.camera,rot_loc)
        rot_mat = mathutils.Euler((rot_loc[0], rot_loc[1], rot_loc[2]), 'XYZ')
        rot_mat_np=np.array(rot_mat.to_matrix())
        world_matrix=np.eye(4)
        world_matrix[:-1,:-1] = rot_mat_np
        world_matrix[:-1,-1] = rot_loc[3:]

        # transfrom to Matrix
        world_matrix_math = Matrix(world_matrix)

        angle_interval = 360.0 // num_camera

        begin_angle = 0
        if ith_rank%2==0:
            begin_angle +=angle_interval/2
        for i in range(num_camera):
            cam_copy= scene.camera.copy()
            R = Matrix.Rotation(math.radians(angle_interval*i+begin_angle), 4, 'Z')
            cam_copy.matrix_world = R @ world_matrix_math
            coll.objects.link(cam_copy)
            camera_queue.append(cam_copy)

    # mean  height
    height_interval = (2*H) / number_rank 

    
    for i in range(number_rank):
        h= i*height_interval
        r=R
        if h>H:
            # r=pow(R**2-(h-H)**2,0.5)
            r = R*(4-h)/2
        h +=ground_z
        create_cam(h,r,number_per_rank,0,i)

    return camera_queue
        