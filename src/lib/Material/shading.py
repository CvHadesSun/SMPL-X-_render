'''
Author: cvhades
Date: 2021-11-09 16:45:40
LastEditTime: 2022-01-18 17:38:33
LastEditors: cvhadessun
FilePath: /PG-engine/src/lib/Material/shading.py
'''
from tkinter.messagebox import NO
import bpy

# create_sh_material(material.node_tree, sh_dst, cloth_img_name)

class Material:
    def __init__(self,cfg) -> None:
        self.cfg=cfg
        # self.new_tree(cloth_img_name)

    def new_material_for_model(self,id,cloth_img_name=None):
        self.material = bpy.data.materials.new(name="Material_{}".format(id))
        self.material.use_nodes = True
        tree=self.material.node_tree

        # remove all nodes
        for n in tree.nodes:
            tree.nodes.remove(n)
        if cloth_img_name is not None:
            cloth_img = bpy.data.images.load(cloth_img_name)
            uv_im = tree.nodes.new("ShaderNodeTexImage")
            uv_im.location = 400, -400
            uv_im.image = cloth_img

        # normal map
        normal_map = tree.nodes.new("ShaderNodeNormalMap")
        normal_map.location = -400,400

        # PSDF
        bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled") #ShaderNodeBsdfPrincipled
        bsdf.location = 0,400

        # 
        mat_out = tree.nodes.new("ShaderNodeOutputMaterial")
        mat_out.location=200,200
        # 
        if cloth_img_name is not None:
            tree.links.new(uv_im.outputs[0],bsdf.inputs[0])
        tree.links.new(normal_map.outputs[0],bsdf.inputs['Normal'])
        tree.links.new(bsdf.outputs[0],mat_out.inputs[0])
    
    def new_material_for_env(self,material):
        pass


    def env_hdri(self,hdri_img):
        scn = bpy.context.scene
        # Get the environment node tree of the current scene
        node_tree = scn.world.node_tree
        tree_nodes = node_tree.nodes
        # Clear all nodes
        tree_nodes.clear()

        # Add Background node
        node_background = tree_nodes.new(type='ShaderNodeBackground')

        # Add Environment Texture node
        node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
        # Load and assign the image to the node property
        node_environment.image = bpy.data.images.load(hdri_img) # Relative path
        node_environment.location = -300,0

        # Add Output node
        node_output = tree_nodes.new(type='ShaderNodeOutputWorld')   
        node_output.location = 200,0

        # Link all nodes
        links = node_tree.links
        link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
        link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])


    def new_tree(self,cloth_img_name):
        self.material = bpy.data.materials.new(name="Material_{}".format(id))
        self.material.use_nodes = True
        sh_dst=self.cfg.Engine.Material.osl
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

            
        
