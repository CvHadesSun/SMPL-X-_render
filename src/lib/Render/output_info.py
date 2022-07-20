'''
Author: cvhades
Date: 2021-11-10 15:24:11
LastEditTime: 2022-01-26 16:15:21
LastEditors: cvhadessun
FilePath: /PG-engine/src/lib/Render/output_info.py
'''

from os.path import join
import numpy as np
from tools.file_op import mkdir_safe
import bpy

# to output the gt data.
class Label:
    def __init__(self,cfg,num_object,
                genders=None,
                shapes=None,
                poses=None) -> None:
        self.cfg = cfg

        # output dir
        self.output_dir=join(cfg.Engine.output_dir,cfg.Engine.output.labels.dir_name)
        mkdir_safe(self.output_dir)

        # set the num object
        self.num_obj = num_object
        self.poses = poses
        self.shapes = shapes
        self.genders = genders

        self.base_info = {}
        if cfg.Engine.output.labels.gender and genders is not None:
            self.base_info['gender'] = genders
        if cfg.Engine.output.labels.pose and poses is not None:
            self.base_info['pose'] = poses
        if cfg.Engine.output.labels.shape and shapes is not None:
            self.base_info['shape'] = shapes
            

    def label_generator(self,obj_list,num_frame):

        if self.cfg.Engine.output.labels.joints2D or self.cfg.Engine.output.labels.joints3D:
            # selected camera
            camera_list_all =[]
            camera_render = []
            num_camera = self.cfg.Engine.Renderer.camera.number_rank * self.cfg.Engine.Renderer.camera.number_per_rank 

            for i in range(1,num_camera+1):
                cam_name = "Camera.{:03}".format(i)
                camera_list_all.append(cam_name)
            if len(self.cfg.Engine.Renderer.camera.render_list)>1 or self.cfg.Engine.Renderer.camera.render_list[0]!=-1: 
                render_list = self.cfg.Engine.Renderer.camera.render_list
                for item in render_list:
                    index = int(item)-1
                    camera_render.append(camera_list_all[index])
            else:
                camera_render = camera_list_all

            scene = bpy.context.scene
            #get label
            for ob in scene.objects:
                if ob.type == 'CAMERA' and ob.name in camera_render:
                    extr = np.asarray(ob.matrix_world)
                    intr = self.get_calibration_matrix_K_from_blender(ob,scene)
                    label_path =  join(self.output_dir,ob.name+'_label.npz') 
                    label_2d=[]
                    label_3d=[]
                    for id in range(self.num_obj):
                        for frame_id in range(1,num_frame):
                            scene.frame_set(frame_id)
                            bones_2d,bones_3d=obj_list[id].get_bone_locs(scene,ob) #[N,2] [N,3]
                            label_2d.append(bones_2d)
                            label_3d.append(bones_3d)
                    l2d = np.concatenate(label_2d,axis=0).reshape(self.num_obj,num_frame-1,-1,2)
                    l3d = np.concatenate(label_3d,axis=0).reshape(self.num_obj,num_frame-1,-1,3)

                    
                    if self.cfg.Engine.output.labels.joints2D:
                        self.base_info['joints2D'] = l2d
                    if self.cfg.Engine.output.labels.joints3D:
                        self.base_info['joints3D'] = l3d
                    self.base_info['intrinsic'] = intr
                    self.base_info['extrinsic'] = extr
                    np.savez(label_path,**self.base_info)
        else:
            return 

    def get_calibration_matrix_K_from_blender(self,cam,scene):
        f_in_mm = cam.data.lens
        resolution_x_in_px = scene.render.resolution_x
        resolution_y_in_px = scene.render.resolution_y
        scale = scene.render.resolution_percentage / 100
        sensor_width_in_mm = cam.data.sensor_width
        sensor_height_in_mm = cam.data.sensor_height
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
        if (cam.data.sensor_fit == 'VERTICAL'):
            s_u = resolution_x_in_px * scale / sensor_width_in_mm / pixel_aspect_ratio 
            s_v = resolution_y_in_px * scale / sensor_height_in_mm
        else:
            pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
            s_u = resolution_x_in_px * scale / sensor_width_in_mm
            s_v = resolution_y_in_px * scale * pixel_aspect_ratio / sensor_height_in_mm
        alpha_u = f_in_mm * s_u
        alpha_v = f_in_mm * s_v
        u_0 = resolution_x_in_px*scale / 2
        v_0 = resolution_y_in_px*scale / 2
        skew = 0 # only use rectangular pixels
        K = np.array([[alpha_u,skew,u_0],[0,alpha_v,v_0],[0,0,1]])
        return K