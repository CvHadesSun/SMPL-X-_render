'''
Date: 2021-12-29 10:30:16
LastEditors: cvhadessun
LastEditTime: 2021-12-29 10:46:48
FilePath: /PG-engine/run/demo/smplx_add_on.py
'''
#
# Copyright 2021 Perceiving Systems, Max Planck Institute for Intelligent Systems
#
# Version: 20210421
#

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Blender
import bpy
import bmesh
from mathutils import Vector

# Python
import argparse
from math import radians
import numpy as np
import os
from pathlib import Path

# SMPLX
if os.name == "nt":
    import sys
    smplx_in_syspath = False
    for syspath in sys.path:
        if "smplx-blender" in syspath:
            smplx_in_syspath = True
            break
    if not smplx_in_syspath:
        sys.path.append(os.path.join(os.environ["USERPROFILE"], ".virtualenvs", "smplx-blender", "Lib", "site-packages"))

import smplx
from smplx.joint_names import JOINT_NAMES
import torch


######################################################################
# Main
######################################################################
def main(model_folder, gender, single_shapekeys=True):
    
    print(f"Loading model: {gender}, {model_folder}")

    # flat_hand_mean = True : flat hand pose
    # use_pca = False : use only joints for posing hand
    model = smplx.create(model_folder, model_type="smplx",
                         gender=gender, use_face_contour=False,
                         ext="npz", flat_hand_mean=True, use_pca=False)
    
    uv_template_path = os.path.join(cwd(), "data", "smplx_uv.obj")
    
    skeletal_mesh_object = create_skeletal_mesh(model, gender, single_shapekeys, uv_template_path)

######################################################################
# Create skeletal mesh from model
######################################################################
def create_skeletal_mesh(model, gender, single_shapekeys, uv_template_path=""):


    num_betas_shape = model.num_betas
    num_expressions_shape = 10
    num_posedirs = len(model.posedirs) # 486 (54 * 9)

    if single_shapekeys:
        max_beta_shape = 1.0
        slider_min = -5
        slider_max = 5
    else:
        max_beta_shape = 5.0
        
    # Create main mesh    
    betas = torch.tensor([[0.0] * model.num_betas])
    expression = torch.tensor([[0.0] * model.num_expression_coeffs])
    
    (vertices, faces) = blender_mesh_from_model(model, betas, expression)

    print("Creating average mesh (vertices=%d, faces=%d)" % (len(vertices), len(faces)))
    name = "SMPLX-shapes-" + gender
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    obj = bpy.data.objects.new("SMPLX-mesh-" + gender, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.select_set(True)

    # Setup UV map
    if uv_template_path != "":
        create_uv(obj, uv_template_path)

    # Create material
    create_material(obj, gender)

    # Add shape keys
    obj.shape_key_add(name = "Base", from_mix=False)

    # Create shape deformations
    print("Creating shape blend shapes: %d, range=+/- %f" % (num_betas_shape, max_beta_shape))
    for beta in range(0, num_betas_shape):
        print("Generating blend shape for beta shape: " + str(beta))
        for direction in ["pos", "neg"]:

            if single_shapekeys and (direction=="neg"):
                continue

            # Load shape deformation
            value = max_beta_shape
            if direction == "neg":
                value = -value

            betas = torch.tensor([[0.0] * model.num_betas])
            betas[0, beta] = value

            (vertices, faces) = blender_mesh_from_model(model, betas, expression)

            shape_mesh = bpy.data.meshes.new("%s_%03d%s" % (name, beta, direction))
            shape_mesh.from_pydata(vertices, [], faces)
            obj.shape_key_add(from_mix=False)

            current_shape_key = obj.data.shape_keys.key_blocks[len(obj.data.shape_keys.key_blocks) - 1]
            
            if single_shapekeys:
                current_shape_key.name = "Shape%03d" % (beta)
                current_shape_key.slider_min = slider_min
                current_shape_key.slider_max = slider_max
            else:
                obj.data.shape_keys.key_blocks[len(obj.data.shape_keys.key_blocks) - 1].name = "Shape%03d_%s" % (beta, direction)

            # Apply shape deformation in edit mode to current shape key
            bpy.context.view_layer.objects.active = obj
            obj.active_shape_key_index = obj.active_shape_key_index + 1
            bpy.ops.object.mode_set(mode="EDIT")
            mesh = bpy.context.edit_object.data
            bm = bmesh.from_edit_mesh(mesh)
            for index, vertex in enumerate(bm.verts):
                v = vertices[index]
                vertex.co = v
            bpy.ops.object.mode_set(mode="OBJECT")

    # Create face expression deformations
    print("Creating face expression blend shapes: %d" % num_expressions_shape)
    name = "SMPLX-expressions-" + gender
    for exp_index in range(num_expressions_shape):
        print("Generating blend shape for expression shape: " + str(exp_index))
        for direction in ["pos", "neg"]:

            if single_shapekeys and (direction=="neg"):
                continue

            # Load shape deformation
            value = max_beta_shape
            if direction == "neg":
                value = -value

            betas = torch.tensor([[0.0] * model.num_betas])
            expression = torch.tensor([[0.0] * num_expressions_shape])
            expression[0, exp_index] = value            
            
            (vertices, faces) = blender_mesh_from_model(model, betas, expression)

            exp_mesh = bpy.data.meshes.new("%s_%03d%s" % (name, exp_index, direction))
            exp_mesh.from_pydata(vertices, [], faces)
            obj.shape_key_add(from_mix=False)

            current_shape_key = obj.data.shape_keys.key_blocks[len(obj.data.shape_keys.key_blocks) - 1]
            
            if single_shapekeys:
                current_shape_key.name = "Exp%03d" % (exp_index)
                current_shape_key.slider_min = -3
                current_shape_key.slider_max = 3
            else:
                obj.data.shape_keys.key_blocks[len(obj.data.shape_keys.key_blocks) - 1].name = "Exp%03d_%s" % (exp_index, direction)

            # Apply shape deformation in edit mode to current shape key
            bpy.context.view_layer.objects.active = obj
            obj.active_shape_key_index = obj.active_shape_key_index + 1
            bpy.ops.object.mode_set(mode="EDIT")
            mesh = bpy.context.edit_object.data
            bm = bmesh.from_edit_mesh(mesh)
            for index, vertex in enumerate(bm.verts):
                v = vertices[index]
                vertex.co = v
            bpy.ops.object.mode_set(mode="OBJECT")
    
    print("Creating pose corrective blend shapes: %d" % num_posedirs)
    # Get rest pose vertices    
    output=model(betas=None, expression=None, return_verts=True)
    vertices_rest = output.vertices.detach().cpu().numpy().squeeze()

    for posedir_index in range(0, num_posedirs):
        print("Generating blend shape for pose corrective shape: " + str(posedir_index))
        for direction in ["pos", "neg"]:
            
            if single_shapekeys and (direction=="neg"):
                continue            

            # Reset model            
            betas = torch.tensor([[0.0] * model.num_betas])

            (vertices, faces) = blender_mesh_from_posedir(model, vertices_rest, posedir_index)

            if single_shapekeys:
                pose_corrective_mesh = bpy.data.meshes.new("Pose_%03d" % posedir_index)
            else:
                pose_corrective_mesh = bpy.data.meshes.new("Pose_%03d%s" % (posedir_index, direction))
                                
            pose_corrective_mesh.from_pydata(vertices, [], faces)
            obj.shape_key_add(from_mix=False)

            current_shape_key = obj.data.shape_keys.key_blocks[len(obj.data.shape_keys.key_blocks) - 1]

            if single_shapekeys:
                current_shape_key.name = "Pose%03d" % (posedir_index)
                current_shape_key.slider_min = slider_min
                current_shape_key.slider_max = slider_max                
            else:        
                current_shape_key.name = "Pose%03d_%s" % (posedir_index, direction)

            # Apply shape deformation in edit mode to current shape key
            bpy.context.view_layer.objects.active = obj
            obj.active_shape_key_index = obj.active_shape_key_index + 1
            bpy.ops.object.mode_set(mode="EDIT")
            mesh = bpy.context.edit_object.data
            bm = bmesh.from_edit_mesh(mesh)
            for index, vertex in enumerate(bm.verts):
                v = vertices[index]
                vertex.co = v
            bpy.ops.object.mode_set(mode="OBJECT")

    # Create armature
    armature_object = create_armature(model, gender)

    # Bind mesh to armature (skinning)
    obj.select_set(True)
#    bpy.context.scene.collection.objects.link(armature_object)
#    scene.objects.active = armature_object
    bpy.context.view_layer.objects.active = armature_object
    bpy.ops.object.parent_set(type="ARMATURE_NAME") # Create empty vertex groups

    # Remove root vertex group
    bpy.context.view_layer.objects.active = obj
    obj.vertex_groups.active_index = 0
    bpy.ops.object.vertex_group_remove()

    # Set skin weights
    bpy.context.view_layer.objects.active = obj
    lbs_weights = model.lbs_weights
    for index, vertex_weights in enumerate(lbs_weights):
        for joint_index, joint_weight in enumerate(vertex_weights):
#            if joint_index == 0:
#                continue
            if joint_weight > 0.0:
                # Get vertex group for joint and add vertex index with weight
                vg = obj.vertex_groups[JOINT_NAMES[joint_index]]
                vg.add([index], joint_weight, "REPLACE")

    # Use smooth normals
    obj.select_set(True)
#    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

    # Armature is now the main object and skinned mesh is child of it
    return armature_object

######################################################################
# Create UV map
######################################################################
def create_uv(target, uv_template_path=""):
    print("Creating UV map from UV template: " + uv_template_path)
    bpy.ops.import_scene.obj(filepath=uv_template_path)
    uv_template = bpy.context.selected_objects[0]

    bpy.context.view_layer.objects.active = uv_template
    target.select_set(True)
    bpy.ops.object.join_uvs()

    # Delete template object from scene
    target.select_set(False)
    uv_template.select_set(True)
    bpy.ops.object.delete()
    target.select_set(True)
    bpy.context.view_layer.objects.active = target

    return

######################################################################
# Create material
######################################################################
def create_material(target, gender, texture_path=""):

    material_name = f"SMPLX-{gender}"

    if material_name in bpy.data.materials:
        mat = bpy.data.materials[material_name]
        target.data.materials.append(mat)
        return
            
    # Create material    
    mat = bpy.data.materials.new(name=material_name)
    target.data.materials.append(mat)

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    for node in nodes:
        nodes.remove(node)

    # BSDF Principled shader is needed for proper material export to glTF
    node = nodes.new("ShaderNodeBsdfPrincipled")
    node.inputs[0].default_value = (0.8, 0.8, 0.8, 1.0)
    node.inputs[7].default_value = 0.6 # Roughness (Reference render: https://gltf-viewer.donmccurdy.com/)

    node_output = nodes.new(type="ShaderNodeOutputMaterial")

    links = mat.node_tree.links
    links.new(node.outputs[0], node_output.inputs[0])

    if texture_path != "":
        image = bpy.data.images.load(texture_path)
        node_texture = nodes.new(type="ShaderNodeTexImage")
        node_texture.image = image
        links.new(node_texture.outputs[0], node.inputs[0])
    return

######################################################################
# Create armature (skeletal rig)
######################################################################
def create_armature(model, gender):

    betas = torch.tensor([[0.0] * model.num_betas])
    joints = blender_joints_from_model(model, betas)

    # Create armature
    bpy.ops.object.armature_add()
    armature_object = bpy.context.selected_objects[0]
#    bpy.context.scene.collection.objects.link(armature_object)
    armature_object.name = "SMPLX-" + gender
    armature_object.data.name = "SMPLX-armature-" + gender
    armature_object.location = (0, 0, 0)
    armature = armature_object.data
    armature.bones[0].name = "root"

    # Add new joints
    num_joints = len(joints)
    print("Creating armature. Number of joints: %d" % (num_joints))

    bpy.ops.object.mode_set(mode="EDIT")
    for index in range(0, num_joints):
        joint_name = JOINT_NAMES[index]
        bpy.ops.armature.bone_primitive_add(name=joint_name)

    # Ensure that all bones are initially starting at origin
    for bone in armature.edit_bones:
        bone.head = (0.0, 0.0, 0.0)
        bone.tail = (0.0, 0.0, 0.1)

    # Setup armature bone hierarchy
    for index in range(len(model.parents)):
        
        if index == 0:
            parent_index = -1 # pelvis is child of root
        else:
            parent_index = model.parents[index].item() #model.kintree_table[0][index]
                    
        # pelvis is bone index 1 since we also have a root bone        
        armature.edit_bones[index + 1].parent = armature.edit_bones[parent_index + 1]

        # Set bone positions
        bone_start = Vector(joints[index])
        armature.edit_bones[JOINT_NAMES[index]].translate(bone_start)

    bpy.ops.object.mode_set(mode="OBJECT")

    return armature_object

# Get Blender mesh data from model for given betas and expression
def blender_mesh_from_model(model, betas, expression):
    
    output = model(betas=betas, expression=expression, return_verts=True)
    vertices = output.vertices.detach().cpu().numpy().squeeze()    
    faces = model.faces

    # Convert model coordinates to Blender coordinates
    # Model coordinates: OpenGL with face looking along z axis
    vertices_blender = []
    faces_blender = []
    for v in vertices:
        vertices_blender.append((v[0], -v[2], v[1]))

    for f in faces:
        faces_blender.append((f[0], f[1], f[2]))

    return (vertices_blender, faces_blender)

# Get Blender mesh data from model for given posedir index
def blender_mesh_from_posedir(model, vertices_rest, index):
    #vertices_rest = model.r
    #vertices = vertices_rest + model.posedirs.T.r[index].T
    
    vertices = vertices_rest + model.posedirs[index].view(-1, 3).numpy()

    faces = model.faces

    # Convert model coordinates to Blender coordinates
    # Model coordinates: OpenGL with face looking along z axis
    vertices_blender = []
    faces_blender = []
    for v in vertices:
        vertices_blender.append((v[0], -v[2], v[1]))

    for f in faces:
        faces_blender.append((f[0], f[1], f[2]))

    return (vertices_blender, faces_blender)


# Get Blender joint locations from model for given betas
def blender_joints_from_model(model, betas):

    output = model(betas=betas, return_verts=True)
    joints = output.joints.detach().cpu().numpy().squeeze()

    # Use only joints 0-54, 55+ are virtual joints which are not needed
    num_joints = model.J_regressor.shape[0]

    joints_blender = []
    for joint_index in range(num_joints):
        j = joints[joint_index]
        joints_blender.append((j[0], -j[2], j[1]))
    return joints_blender

######################################################################
# Get absolute path to current working directory
######################################################################
def cwd():
    # Get absolute path to current working directory
    # Fix path if we are running script from within Blender to point to parent directory of .blend file
    cwd = os.path.split(__file__)[0]
    if cwd.endswith('.blend'):
        cwd = os.path.split(cwd)[0]
    return cwd


######################################################################
# Main
######################################################################
if __name__ == "__main__":
    if bpy.app.background:
        parser = argparse.ArgumentParser(description="SMPL-X Model")

        parser.add_argument("--model-folder", required=True, type=str,
                            help="The path to the SMPL-X model folder")
        parser.add_argument("--gender", type=str, default="male",
                            help="The gender of the model (female|male)")

        args = parser.parse_args()

        model_folder = osp.expanduser(osp.expandvars(args.model_folder))
        gender = args.gender
        main(model_folder, gender, single_shapekeys=True)
    else:
        model_folder = os.path.join(cwd(), "models")

        main(model_folder, "female", single_shapekeys=True)
        main(model_folder, "male", single_shapekeys=True)
        main(model_folder, "neutral", single_shapekeys=True)
