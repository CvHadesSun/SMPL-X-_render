'''
Author: cvhades
Date: 2021-11-09 16:47:29
LastEditTime: 2021-11-16 14:31:09
LastEditors: Please set LastEditors
FilePath: /PG-engine/src/lib/scene/scene.py
'''

import bpy


class Scene:
    def __init__(self, cfg) -> None:
        # init the scene in the blender.
        self.scene = bpy.data.scenes["Scene"]
        self.scene.render.engine = cfg.Engine.Renderer.engine  # "CYCLES"
        self.scene.cycles.shading_system = True
        self.scene.use_nodes = True
        self.scene.render.film_transparent = True

    def get_scene(self):
        return self.scene

    def reset_scene(self) -> None:
        bpy.ops.object.delete()
