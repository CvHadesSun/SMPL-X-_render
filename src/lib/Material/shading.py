'''
Author: cvhades
Date: 2021-11-09 16:45:40
LastEditTime: 2021-11-09 18:05:32
LastEditors: Please set LastEditors
FilePath: /PG-engine/src/lib/material/shading.py
'''
import bpy

# create_sh_material(material.node_tree, sh_dst, cloth_img_name)

class Material:
    def __init__(self,cfg,id) -> None:
        self.cfg=cfg
        self.material = bpy.data.materials.new(name="Material_{}".format(id))
        self.material.use_nodes = True
        self.new_tree()

    def new_tree(self,sh_dst,cloth_img_name):
        # clear default nodes
        tree=self.material.node_tree
        for n in tree.nodes:
            tree.nodes.remove(n)

        uv = tree.nodes.new("ShaderNodeTexCoord")
        uv.location = -800, 400

        uv_xform = tree.nodes.new("ShaderNodeVectorMath")
        uv_xform.location = -600, 400
        uv_xform.inputs[1].default_value = (0, 0, 1)
        # uv_xform.operation = 'AVERAGE'  # blender < 2.8x
        uv_xform.operation = "ADD"  # TODO

        cloth_img = bpy.data.images.load(cloth_img_name)
        uv_im = tree.nodes.new("ShaderNodeTexImage")
        uv_im.location = -400, 400
        uv_im.image = cloth_img

        rgb = tree.nodes.new("ShaderNodeRGB")
        rgb.location = -400, 200

        script = tree.nodes.new("ShaderNodeScript")
        script.location = -230, 400
        script.mode = "EXTERNAL"
        script.filepath = sh_dst  # 'spher_harm/sh.osl' #using the same file from multiple jobs causes white texture
        script.update()

        self.cfg.Engine.Material.osl=sh_dst

        # the emission node makes it independent of the scene lighting
        emission = tree.nodes.new("ShaderNodeEmission")
        emission.location = -60, 400

        mat_out = tree.nodes.new("ShaderNodeOutputMaterial")
        mat_out.location = 110, 400

        tree.links.new(uv.outputs[2], uv_im.inputs[0])
        tree.links.new(uv_im.outputs[0], script.inputs[0])
        tree.links.new(script.outputs[0], emission.inputs[0])
        tree.links.new(emission.outputs[0], mat_out.inputs[0])

    def upate_script(self,material_item,sh_coeffs):
        script=material_item.node_tree.nodes["Script"]
        script.filepath = self.cfg.Engine.Material.osl
        script.update()

        #assign the light.
        for ish, coeff in enumerate(sh_coeffs):
            script[ish+1].default_value = coeff

            
        
