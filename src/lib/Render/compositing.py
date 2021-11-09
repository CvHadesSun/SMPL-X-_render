'''
Author: cvhades
Date: 2021-11-09 16:46:50
LastEditTime: 2021-11-09 18:36:35
LastEditors: Please set LastEditors
FilePath: /PG-engine/src/lib/render/compositing.py
'''
from os.path import join
import bpy
from mathutils import Matrix, Euler
import math

class RenderLayer:
    
    def __init__(self,cfg) -> None:
        self.cfg=cfg
        self.res={}
        #
        self.set_output()

    def set_output(self):
        # set the output file name
        if self.cfg.Engine.output.segmentation:
            self.res['segm'] = join(self.cfg.Engine.tmp_path,"%05d_segm" %(self.cfg.Engine.idx))
        if self.cfg.Engine.output.depth:
            self.res['depth'] = join(self.cfg.Engine.tmp_path,"%05d_depth" %(self.cfg.Engine.idx))
        if self.cfg.Engine.output.depth:
            self.res['normal'] = join(self.cfg.Engine.tmp_path,"%05d_normal" %(self.cfg.Engine.idx))
        if self.cfg.Engine.output.fg:
            self.res['fg'] = join(self.cfg.Engine.tmp_path,"%05d_fg" %(self.cfg.Engine.idx))
        if self.cfg.Engine.output.gtflow:
            self.res['gtflow'] = join(self.cfg.Engine.tmp_path,"%05d_gtflow" %(self.cfg.Engine.idx))


    def init_tree_nodes(self,tree,bg_img_name=None):
        # clear default nodes
        for n in tree.nodes:
            tree.nodes.remove(n)

        # create node for foreground image
        layers = tree.nodes.new("CompositorNodeRLayers")
        layers.location = -300, 400

        # create node for background image
        bg_im = tree.nodes.new("CompositorNodeImage")
        bg_im.location = -300, 30
        if bg_img_name is not None:
            bg_img = bpy.data.images.load(bg_img_name)
            bg_im.image = bg_img
            print("Set the background image!")

        # create node for mixing foreground and background images
        mix = tree.nodes.new("CompositorNodeMixRGB")
        mix.location = 40, 30
        mix.use_alpha = True

        # create node for the final output
        composite_out = tree.nodes.new("CompositorNodeComposite")
        composite_out.location = 240, 30

        if self.cfg.Engine.output.depth:
            depth_out = tree.nodes.new("CompositorNodeOutputFile")
            depth_out.location = 40, 700
            depth_out.format.file_format = "OPEN_EXR"
            depth_out.base_path = self.res["depth"]

        if self.cfg.Engine.output.normal:
            normal_out = tree.nodes.new("CompositorNodeOutputFile")
            normal_out.location = 40, 600
            normal_out.format.file_format = "OPEN_EXR"
            normal_out.base_path = self.res["normal"]

        
        # create node for saving foreground image
        if self.cfg.Engine.output.fg:
            fg_out = tree.nodes.new("CompositorNodeOutputFile")
            fg_out.location = 170, 600
            fg_out.format.file_format = "PNG"
            fg_out.base_path = self.res["fg"]

        # create node for saving ground truth flow
        if self.cfg.Engine.output.gtflow:
            gtflow_out = tree.nodes.new("CompositorNodeOutputFile")
            gtflow_out.location = 40, 500
            gtflow_out.format.file_format = "OPEN_EXR"
            gtflow_out.base_path = self.res["gtflow"]

        
        # create node for saving segmentation
        if self.cfg.Engine.output.segmentation:
            segm_out = tree.nodes.new("CompositorNodeOutputFile")
            segm_out.location = 40, 400
            segm_out.format.file_format = "OPEN_EXR"
            segm_out.base_path = self.res["segm"]


        # merge fg and bg images
        tree.links.new(bg_im.outputs[0], mix.inputs[1])
        tree.links.new(layers.outputs["Image"], mix.inputs[2])

        tree.links.new(mix.outputs[0], composite_out.inputs[0])  # bg+fg image
        if self.cfg.Engine.output.fg:
            tree.links.new(layers.outputs["Image"], fg_out.inputs[0])  # save fg
        if self.cfg.Engine.output.depth:
            # 'Z' instead of 'Depth'  # blender < 2.8x
            tree.links.new(layers.outputs["Depth"], depth_out.inputs[0])  # save depth
        if self.cfg.Engine.output.normal:
            tree.links.new(layers.outputs["Normal"], normal_out.inputs[0])  # save normal
        if self.cfg.Engine.output.gtflow:
            # 'Speed' instead of 'Vector'  # blender < 2.8x
            tree.links.new(
                layers.outputs["Vector"], gtflow_out.inputs[0]
            )  # save ground truth flow
        if self.cfg.Engine.output.segmentation:
            tree.links.new(
                layers.outputs["IndexMA"], segm_out.inputs[0]
            )  # save segmentation

    
    def init_renderer(self):
        resx = self.cfg.Engine.Renderer.resx
        resy = self.cfg.Engine.Renderer.resy
        
        scn = bpy.context.scene
        scn.cycles.film_transparent = True
        # blender < 2.8x
        # scn.render.layers['RenderLayer'].use_pass_vector = True
        # scn.render.layers['RenderLayer'].use_pass_normal = True
        # scene.render.layers['RenderLayer'].use_pass_emit = True
        # scene.render.layers['RenderLayer'].use_pass_material_index = True
        vl = bpy.context.view_layer
        vl.use_pass_vector = True
        vl.use_pass_normal = True
        vl.use_pass_emit = True
        vl.use_pass_material_index = True

        # set render size
        scn.render.resolution_x = resy
        scn.render.resolution_y = resx
        scn.render.resolution_percentage = 100
        scn.render.image_settings.file_format = "PNG"

