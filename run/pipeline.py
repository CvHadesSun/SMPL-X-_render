'''
Author: cvhades
Date: 2021-11-10 17:12:09
LastEditTime: 2022-01-18 19:25:14
LastEditors: cvhadessun
FilePath: /PG-engine/run/pipeline.py
'''

import os
import sys

from numpy.lib.arraysetops import isin
from numpy.lib.index_tricks import ogrid
from numpy.random.mtrand import f
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
from lib.Model.SMPL_X import SMPLX_Body
from lib.Render.compositing import RenderLayer
from tools.light import random_light
from tools.cam import set_camera
from tools.os_utils import *


# TODO: the pipeline of data generation

class PipeLine:
    def __init__(self, 
                cfg, 
                prefix, 
                num_model, 
                genders=None, 
                bg_img=None, 
                textures=None, 
                shape=None,
                HDRI_img=None) -> None:
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
        self.output = self.output_path
        # mdkir tmp path
        self.tmp_path = os.path.join(self.output, 'experimental')
        self.cfg.Engine.tmp_path=self.tmp_path
        mkdir_safe(self.tmp_path)
        #
        if  genders:
            self.genders = genders
        else:
            self.genders = gender_generator(num_model)
        self.num_object = num_model
        if isinstance(textures,type(None)):
            self.textures=[]
        else:
            self.textures = textures
        if bg_img is not None:
            self.bg_img = bg_img
        else:
            self.bg_img = pick_background(self.cfg.Engine.input.bg_images.dir,
                                          self.cfg.Engine.input.bg_images.txt)  # image dir/image_name.
    
        self.HDRI_img =HDRI_img
        self.shape = shape
        self.obj_list = []
        # init the scene
        self.init_scene()
        self.num_frames=0
        


    def init_scene(self):
        self.scene = Scene(self.cfg,self.HDRI_img)
        self.renderer = RenderLayer(self.cfg)
        self.mat = Material(self.cfg)           
        # init model
        self._init_model()

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
        # if not self.shape:
        if isinstance(self.shape,type(None)):
            self.shape=[]
            self.smpl_data = np.load(os.path.join(self.cfg.Engine.Model.SMPL.smpl_dir, self.cfg.Engine.Model.SMPL.smpl_data_filename))
        self.scene.reset_scene()
        for id in range(self.num_object):
            gender = self.genders[id]
            try:
                texture = self.textures[id]
            except:
                texture = pick_texture(self.cfg.Engine.input.uv_textures.clothing_option,
                                       self.cfg.Engine.input.uv_textures.dir,
                                       self.cfg.Engine.input.uv_textures.txt)
                self.textures.append(texture)
            
            self.mat.new_material_for_model(self.cfg, id,texture)
            if self.cfg.Engine.Model.selected == "SMPL":
                smpl = SMPL_Body(self.cfg, gender=self.genders[id], person_no=id)
            elif self.cfg.Engine.Model.selected == "SMPLX":
                smpl = SMPLX_Body(self.cfg, gender=self.genders[id], person_no=id)
            else:
                raise("model type no supported, please config the cfg.Engine.Model.selected.")

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
        if 'shape' in frame_info.keys():
            shape=frame_info['shape'] 
        else:
            shape=self.shape
        if 'expression' in frame_info.keys():
            expression=frame_info['expression']
        else:
            expression=np.zeros([self.num_object,10])
        

        for id in range(self.num_object):
            s=shape[id]
            p=pose[id]
            t=trans[id]
            e=expression[id]
            # apply the translation, pose and shape to the character
            self.obj_list[id].apply_trans_pose_shape(
                t, p, s,e,self.obj_list[0].original,frame=self.num_frames)
            
            bpy.context.view_layer.update()
        # cam_ob.animation_data_clear()
        self.num_frames +=1  #

        
    def render(self):
        #
        # for part, material in self.obj_list[0].materials.items():
        #     material.node_tree.nodes["Vector Math"].inputs[1].default_value[:2] = (0, 0)

        ground = self.obj_list[0].minz

        # 
        
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

    
            



        
        
