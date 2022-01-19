'''
Author: cvhades
Date: 2021-11-09 16:47:29
LastEditTime: 2022-01-19 16:10:18
LastEditors: cvhadessun
FilePath: /PG-engine/src/lib/Scene/scene.py
'''


import bpy
from lib.Render.compositing import RenderLayer
from tools.cam import create_cameras_array
from tools.light import new_light
from lib.Material.shading import Material

class Scene:
    def __init__(self, cfg,hdri_img=None) -> None:
        # init the scene in the blender.
        self.cfg=cfg
        # render engine setup
        self.render =  RenderLayer(cfg)
        self.mat = Material(cfg)
        self.render.init_renderer()

        # new light
        if cfg.Engine.Renderer.light.open:
            new_light(cfg.Engine.Renderer.light.radians,
                       cfg.Engine.Renderer.light.height)
                       
        # load HDRI env 
        if cfg.Engine.Renderer.HDRI.load and hdri_img is not None:
            self.mat.env_hdri(hdri_img)
            
    def create_camera_array(self,ground):
        # need the ground z value
        create_cameras_array(
            self.cfg.Engine.Renderer.camera.height,
            self.cfg.Engine.Renderer.camera.radians,
            self.cfg.Engine.Renderer.camera.number_rank,
            self.cfg.Engine.Renderer.camera.number_per_rank,
            ground
            )

    def reset_scene(self) -> None:
        bpy.ops.object.delete()
    
