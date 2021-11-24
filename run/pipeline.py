'''
Author: cvhades
Date: 2021-11-10 17:12:09
LastEditTime: 2021-11-24 18:01:34
LastEditors: Please set LastEditors
FilePath: /PG-engine/run/pipeline.py
'''

import os
import sys
import bpy
import numpy as np
import shutil
from mathutils import Vector

# cur_dir = os.path.dirname(os.path.abspath(__file__))
# root_dir = os.path.join(cur_dir, '..')
# sys.path.insert(0, os.path.join(root_dir, 'src'))

from tools.file_op import mkdir_safe
from tools.random_utils import pick_background, pick_texture, gender_generator, pick_shape_whole,pick_cam
from lib.Scene.scene import Scene
from lib.Material.shading import Material
from lib.Model.SMPL import SMPL_Body
from lib.Render.compositing import RenderLayer
from tools.light import random_light
from tools.cam import set_camera
from tools.os_utils import *


# TODO: the pipeline of data generation

class PipeLine:
    def __init__(self, cfg, prefix,name, num_model, genders=None, bg_img=None, textures=None, shape=None,sh_coeffs=None) -> None:
        '''
        output-|
                |--name
                    |--experimental
                    |--rgb
                    |--depth
                    |--label
        @genders: SMPL model class
        @bg_img: the background of scene
        @textures: the textures for SMPL model.
        '''
        self.cfg = cfg
        # set the output path
        # if cfg.Engine.output.root_dir is not None:
        #     self.output_path = cfg.Engine.output.output
        # else:
        self.output_path = os.path.join(cfg.Engine.output_dir, prefix)
        mkdir_safe(self.output_path)
        mkdir_safe(os.path.join(self.output_path, name))
        self.output = os.path.join(self.output_path, name)
        # mdkir tmp path
        self.tmp_path = os.path.join(self.output, 'experimental')
        self.cfg.Engine.tmp_path=self.tmp_path
        mkdir_safe(self.tmp_path)
        #cp osl into tmp dir
        osl=cfg.Engine.Material.osl
        shutil.copy(osl,os.path.join(self.tmp_path,'mat_osl.osl'))
        # update osl path
        self.cfg.Engine.Material.osl=os.path.join(self.tmp_path,'mat_osl.osl')
        #
        if  genders:
            self.genders = genders
        else:
            self.genders = gender_generator(num_model)
        self.num_object = num_model
        self.textures = textures
        self.bg_img = bg_img
        self.shape = shape

        if not sh_coeffs:
            self.sh_coeffs=random_light()
        else:
            self.sh_coeffs=sh_coeffs
        self.obj_list = []
        # assign the bg and textures
        self._set_bg()
        # init the scene
        self.init_scene()
        self.num_frames=0

    def _set_bg(self):
        if not self.bg_img:
            # random select from bg map
            self.bg_img = pick_background(self.cfg.Engine.input.uv_textures.dir,
                                          self.cfg.Engine.input.uv_textures.label)  # image dir/image_name.

    def init_scene(self):
        self.scene = Scene(self.cfg)
        self.renderer = RenderLayer(self.cfg)
        # init model
        self._init_model()
        # update the material scripts
        
        spherical_harmonics = []
        for mname, m in self.obj_list[0].materials.items():
            spherical_harmonics.append(m.node_tree.nodes["Script"])
            spherical_harmonics[-1].filepath = self.cfg.Engine.Material.osl
            spherical_harmonics[-1].update()

        for ish, coeff in enumerate(self.sh_coeffs):
            for sc in spherical_harmonics:
                sc.inputs[ish + 1].default_value = coeff

        #render
        self.renderer.init_tree_nodes(self.scene.scene.node_tree,self.bg_img)
        self.renderer.init_renderer()

        # set cam
        # random get cam params
        # cam_height, cam_dist = pick_cam(self.cfg.Engine.Renderer.camera.cam, cam_dist_range)
        cam_height = self.cfg.Engine.Renderer.camera.cam_height
        cam_dist = self.cfg.Engine.Renderer.camera.cam_dist
        self.cam_ob = set_camera(cam_dist=cam_dist, cam_height=cam_height, zrot_euler=self.cfg.Engine.Renderer.camera.zrot_euler)

        for id in range(self.num_object):
            self.obj_list[id].reset_joint_positions(
            self.shape[id], self.scene.scene, self.cam_ob
            )
        # smpl_body_list[person_no].arm_ob.animation_data_clear()
        self.cam_ob.animation_data_clear()



    def _init_model(self):
        #
        if not self.shape:
            self.shape=[]
            self.smpl_data = np.load(os.path.join(self.cfg.Engine.Model.SMPL.smpl_dir, self.cfg.Engine.Model.SMPL.smpl_data_filename))
        self.scene.reset_scene()
        for id in range(self.num_object):
            gender = self.genders[id]
            try:
                texture = self.textures[id]
            except:
                texture = pick_texture(self.cfg.Engine.input.bg_images.clothing_option,
                                       self.cfg.Engine.input.bg_images.dir,
                                       self.cfg.Engine.input.bg_images.txt)
                self.textures.append(texture)
            material = Material(self.cfg, id,texture)
            smpl = SMPL_Body(self.cfg, material.material, gender=self.genders[id], person_no=id)
            self.obj_list.append(smpl)

            try:
                shape = self.shape[id]
            except:
                shape = pick_shape_whole(self.smpl_data, gender)
            self.shape.append(shape)


    def apply_input(self,**frame_info):
        # input per frame info: pose and trans
        pose=frame_info['pose']  #[N,72]
        trans=frame_info['trans'] #[N,3]
        cam_ob=frame_info['cam'] 
        

        for id in range(self.num_object):
            s=self.shape[id]
            p=pose[id]
            t=trans[id]
            # apply the translation, pose and shape to the character
            self.obj_list[id].apply_trans_pose_shape(
                Vector(t), p, s, self.scene.scene, cam_ob, self.num_frames)
            
            bpy.context.view_layer.update()
        # cam_ob.animation_data_clear()
        self.num_frames +=1  #

        
    def render(self):
        #
        for part, material in self.obj_list[0].materials.items():
            material.node_tree.nodes["Vector Math"].inputs[1].default_value[:2] = (0, 0)
        
        # LOOP TO RENDER: iterate over the keyframes and render
        
        mkdir_safe(os.path.join(self.output,'rgb'))
        rgb_path=os.path.join(self.output,'rgb')
        # mkdir dir to output
        for seq_frame, i in enumerate(range(self.num_frames)):
            self.scene.scene.frame_set(seq_frame)
            self.scene.scene.render.filepath = os.path.join(rgb_path, "Image{:04d}.png".format(seq_frame))
            # disable render output
            old = disable_output_start()
            # Render
            bpy.ops.render.render(write_still=True)
            # disable output redirection
            disable_output_end(old)

    
            



        
        
