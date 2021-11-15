'''
Author: cvhades
Date: 2021-11-10 17:12:09
LastEditTime: 2021-11-12 11:25:44
LastEditors: Please set LastEditors
FilePath: /PG-engine/run/pipeline.py
'''

import os
import sys
import bpy
import numpy as np

cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(cur_dir, '..')
sys.path.insert(0, os.path.join(root_dir, 'src'))

from tools.file_op import mkdir_safe
from tools.random_utils import pick_background, pick_texture, gender_generator, pick_shape_whole
from lib.Scene.scene import Scene
from lib.Material.shading import Material
from lib.Model.SMPL import SMPL_Body
from lib.Render.compositing import RenderLayer
import random


# TODO: the pipeline of data generation

class PipeLine:
    def __init__(self, cfg, name, num_model, genders=None, bg_img=None, textures=None, shape=None) -> None:
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
        if cfg.Engine.output.output is not None:
            self.output_path = cfg.Engine.output.output
        else:
            self.output_path = os.path.join(root_dir, 'output')
        mkdir_safe(self.output_path)
        mkdir_safe(os.path.join(self.output_path, name))
        self.output = os.path.join(self.output_path, name)
        # mdkir tmp path
        self.tmp_path = os.path.join(self.output_path, 'experimental')
        self.cfg.Engine.tmp_path=self.tmp_path
        mkdir_safe(self.tmp_path)
        #
        if not genders:
            self.genders = genders
        else:
            self.genders = gender_generator(num_model)
        self.num_object = num_model
        self.textures = textures
        self.bg_img = bg_img
        self.shape = shape
        self.obj_list = []
        # assign the bg and textures
        self._set_bg()
        self._set_obj_cloth_imgs()
        # init the scene
        self.init_scene()

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
        sh_coeffs=self.random_light()
        spherical_harmonics = []
        for mname, m in self.obj_list[0].materials.items():
            spherical_harmonics.append(m.node_tree.nodes["Script"])
            spherical_harmonics[-1].filepath = self.cfg.Engine.Material.osl
            spherical_harmonics[-1].update()

        for ish, coeff in enumerate(sh_coeffs):
            for sc in spherical_harmonics:
                sc.inputs[ish + 1].default_value = coeff

        #render
        self.renderer.init_tree_nodes(self.scene.node_tree,self.bg_img)
        self.renderer.init_renderer()





    def random_light(self):
        # Random light
        sh_coeffs = 0.7 * (2 * np.random.rand(9) - 1)
        # Ambient light (first coeff) needs a minimum  is ambient. Rest is uniformly distributed, higher means brighter.
        sh_coeffs[0] = 0.5 + 0.9 * np.random.rand()
        sh_coeffs[1] = -0.7 * np.random.rand()
        return sh_coeffs

    def _init_model(self):
        #
        self.smpl_data = np.load(self.cfg.Engine.Model.SMPL.smpl_dir, self.cfg.Engine.Model.SMPL.smpl_data_filename)
        for id in range(self.num_object):
            gender = self.genders[id]
            try:
                texture = self.textures[id]
            except:
                texture = pick_texture(self.cfg.Engine.input.bg_images.clothing_option,
                                       self.cfg.Engine.input.bg_images.dir,
                                       self.cfg.Engine.input.bg_images.txt)
                self.textures.append(texture)
            material = Material(self.cfg, id)
            smpl = SMPL_Body(self.cfg, material.material, gender=self.genders[id], person_no=id)
            self.obj_list.append(smpl)

            try:
                shape = self.shape[id]
            except:
                shape = pick_shape_whole(self.smpl_data, gender)
            self.shape.append(shape)

    # def _pose_shape_gen(self):
    #     if self.online:
    #         print('need to implement.')
    #     else:
    #         # input the pose and shape data info.
    #         pass

    def apply_input(self, name):
        pass
