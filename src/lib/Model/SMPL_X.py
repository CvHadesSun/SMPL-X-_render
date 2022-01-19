'''
Date: 2021-12-23 15:59:44
LastEditors: cvhadessun
LastEditTime: 2022-01-19 16:58:30
FilePath: /PG-engine/src/lib/Model/SMPL_X.py
'''


from webbrowser import get
from yaml.events import NodeEvent
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Quaternion
import numpy as np
import pickle as pkl
import os

from tools.geometryutils import rodrigues2bshapes,set_pose_from_rodrigues,Rodrigues


hand_pose={}
hand_pose['flat']= np.zeros([90]).reshape(2,-1)
hand_pose['relaxed'] = np.array(
                        [[ 0.11167871,  0.04289218, -0.41644183,  0.10881133, -0.06598568,
                        -0.75622   , -0.09639297, -0.09091566, -0.18845929, -0.11809504,
                        0.05094385, -0.5295845 , -0.14369841,  0.0552417 , -0.7048571 ,
                        -0.01918292, -0.09233685, -0.3379135 , -0.45703298, -0.19628395,
                        -0.6254575 , -0.21465237, -0.06599829, -0.50689423, -0.36972436,
                        -0.06034463, -0.07949023, -0.1418697 , -0.08585263, -0.63552827,
                        -0.3033416 , -0.05788098, -0.6313892 , -0.17612089, -0.13209307,
                        -0.37335458,  0.8509643 ,  0.27692273, -0.09154807, -0.49983943,
                        0.02655647,  0.05288088,  0.5355592 ,  0.04596104, -0.27735803],
                        [0.11167871, -0.04289218,  0.41644183,  0.10881133,  0.06598568,
                        0.75622   , -0.09639297,  0.09091566,  0.18845929, -0.11809504,
                        -0.05094385,  0.5295845 , -0.14369841, -0.0552417 ,  0.7048571 ,
                        -0.01918292,  0.09233685,  0.3379135 , -0.45703298,  0.19628395,
                        0.6254575 , -0.21465237,  0.06599829,  0.50689423, -0.36972436,
                        0.06034463,  0.07949023, -0.1418697 ,  0.08585263,  0.63552827,
                        -0.3033416 ,  0.05788098,  0.6313892 , -0.17612089,  0.13209307,
                        0.37335458,  0.8509643 , -0.27692273,  0.09154807, -0.49983943,
                        -0.02655647, -0.05288088,  0.5355592 , -0.04596104,  0.27735803]])

class SMPLX_Body:
    '''
    smplx-dir:
        |__models
        |__data
            |__joint_regressors.pkl
            |__segm_per_v_overlap.pkl
    '''
    def __init__(self,cfg,gender='female',person_no=0) -> None:
        # load fbx model
        smpl_data_folder=cfg.Engine.Model.SMPLX.smplx_dir
        self.cfg=cfg
        bpy.ops.import_scene.fbx(
            filepath=os.path.join(
                smpl_data_folder,
                'models',
                "{}_smplx.fbx".format(gender),
            ),
            axis_forward="Y",
            axis_up="Z",
            global_scale=1,
        )
        J_regressors = pkl.load(
            open(os.path.join(smpl_data_folder, "data/joint_regressors.pkl"), "rb"))
        self.joint_regressor = J_regressors["J_regressor_{}".format(gender)]
        
        armature_name = "Armature_{}".format(person_no)

        bpy.context.active_object.name = armature_name   # rename

        
        for mesh in bpy.data.objects.keys():
            if mesh == 'SMPLX-mesh-male':
                self.ob = bpy.data.objects[mesh]

            if mesh == 'SMPLX-mesh-female':
                self.ob = bpy.data.objects[mesh]

            if mesh == 'SMPLX-mesh-neutral':
                self.ob = bpy.data.objects[mesh]


        # 
        self.ob.data.use_auto_smooth = False 
        self.ob.active_material = bpy.data.materials["Material_{}".format(person_no)]
        self.ob.data.shape_keys.animation_data_clear() 
        self.arm_ob = bpy.data.objects[armature_name]   
        self.arm_ob.animation_data_clear()
        #
        self.setState0()
        self.ob.select_set(True)
        bpy.context.view_layer.objects.active = self.ob
        self.materials = self.create_segmentation(bpy.data.materials["Material_{}".format(person_no)])

        # unblocking both the pose and the blendshape limits
        for k in self.ob.data.shape_keys.key_blocks.keys():
            bpy.data.shape_keys["Key"].key_blocks[k].slider_min = -10
            bpy.data.shape_keys["Key"].key_blocks[k].slider_max = 10
        
        bpy.context.view_layer.objects.active = self.arm_ob



        self.original=np.array([0,0,0])
        self.minz = 0
        
        # bones name
        self.part_match={ 
            'root': 'root', 'bone_00':  'pelvis', 'bone_01':  'left_hip', 'bone_02':  'right_hip', 
            'bone_03':  'spine1', 'bone_04':  'left_knee', 'bone_05':  'right_knee', 'bone_06':  'spine2', 
            'bone_07':  'left_ankle', 'bone_08':  'right_ankle', 'bone_09':  'spine3', 'bone_10':  'left_foot', 
            'bone_11':  'right_foot', 'bone_12':  'neck', 'bone_13':  'left_collar', 'bone_14':  'right_collar', 
            'bone_15':  'head', 'bone_16':  'left_shoulder', 'bone_17':  'right_shoulder', 'bone_18':  'left_elbow', 
            'bone_19':  'right_elbow', 'bone_20':  'left_wrist', 'bone_21':  'right_wrist', 'bone_22':  'jaw', 
            'bone_23':  'left_eye_smplhf', 'bone_24':  'right_eye_smplhf', 
            'bone_25':  'left_index1', 'bone_26':  'left_index2', 'bone_27':  'left_index3', 
            'bone_28':  'left_middle1', 'bone_29':  'left_middle2', 'bone_30':  'left_middle3', 
            'bone_31':  'left_pinky1', 'bone_32':  'left_pinky2', 'bone_33':  'left_pinky3', 
            'bone_34':  'left_ring1', 'bone_35':  'left_ring2', 'bone_36':  'left_ring3', 
            'bone_37':  'left_thumb1', 'bone_38':  'left_thumb2', 'bone_39':  'left_thumb3', 
            'bone_40':  'right_index1', 'bone_41':  'right_index2', 'bone_42':  'right_index3', 
            'bone_43':  'right_middle1', 'bone_44':  'right_middle2', 'bone_45':  'right_middle3', 
            'bone_46':  'right_pinky1', 'bone_47':  'right_pinky2', 'bone_48':  'right_pinky3', 
            'bone_49':  'right_ring1', 'bone_50':  'right_ring2', 'bone_51':  'right_ring3', 
            'bone_52':  'right_thumb1', 'bone_53':  'right_thumb2', 'bone_54':  'right_thumb3'
            }

    def setState0(self):
        for ob in bpy.data.objects.values():
            # ob.select = False  # blender < 2.8x
            ob.select_set(False)
        # bpy.context.scene.objects.active = None  # blender < 2.8x
        bpy.context.view_layer.objects.active = None

    def create_segmentation(self, material):
        print("Creating materials segmentation")
        sorted_parts = [
            "hips",
            "leftUpLeg",
            "rightUpLeg",
            "spine",
            "leftLeg",
            "rightLeg",
            "spine1",
            "leftFoot",
            "rightFoot",
            "spine2",
            "leftToeBase",
            "rightToeBase",
            "neck",
            "leftShoulder",
            "rightShoulder",
            "head",
            "leftArm",
            "rightArm",
            "leftForeArm",
            "rightForeArm",
            "leftHand",
            "rightHand",
            "leftHandIndex1",
            "rightHandIndex1",
        ]
        part2num = {part: (ipart + 1) for ipart, part in enumerate(sorted_parts)}
        materials = {}
        vgroups = {}
        segm_path=os.path.join(self.cfg.Engine.Model.SMPLX.smplx_dir,'data',self.cfg.Engine.Model.SMPLX.segm_overlap)
        with open(segm_path, "rb") as f:
            vsegm = pkl.load(f)
        bpy.ops.object.material_slot_remove()
        parts = sorted(vsegm.keys())
        for part in parts:
            vs = vsegm[part]
            # vgroups[part] = self.ob.vertex_groups.new(part)  # blender < 2.8x
            vgroups[part] = self.ob.vertex_groups.new(name=part)
            vgroups[part].add(vs, 1.0, "ADD")
            bpy.ops.object.vertex_group_set_active(group=part)
            materials[part] = material.copy()
            materials[part].pass_index = part2num[part]
            bpy.ops.object.material_slot_add()
            self.ob.material_slots[-1].material = materials[part]
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.object.vertex_group_select()
            bpy.ops.object.material_slot_assign()
            bpy.ops.object.mode_set(mode="OBJECT")
        return materials

    def apply_trans_pose_shape(self,trans,pose,shape,expression,original=np.array([0,0,0]),frame=None):
        """
        Apply trans pose and shape to character
        """

        # set global orientation
        # set_pose_from_rodrigues(self.arm_ob,'pelvis',orient)
        rot = np.array(self.cfg.Engine.Model.rot)
        set_pose_from_rodrigues(self.arm_ob,'root',rot)  

        # transform pose into rotation matrices (for pose) and pose blendshapes            
        mrots, bsh = rodrigues2bshapes(pose)

        rot_mat=Rodrigues(rot)
        if frame == 0:
            self.original = self.original - trans
        delta_ori = np.dot(rot_mat,original)
        trans=np.dot(rot_mat,trans)+delta_ori

        # set the location of the first bone to the translation parameter

        if frame is not None:
            # self.arm_ob.pose.bones['pelvis'].location = trans
            self.arm_ob.pose.bones['root'].location = trans
            self.arm_ob.pose.bones['root'].keyframe_insert('location', frame=frame)

        # set the pose of each bone to the quaternion specified by pose
        for ibone, mrot in enumerate(mrots):
            bone = self.arm_ob.pose.bones[self.part_match['bone_%02d' % ibone]]
            bone.rotation_quaternion = Matrix(mrot).to_quaternion()
            if frame is not None:
                bone.keyframe_insert('rotation_quaternion', frame=frame)
                bone.keyframe_insert('location', frame=frame)

        # apply pose blendshapes
        for ibshape, bshape in enumerate(bsh):
            self.ob.data.shape_keys.key_blocks['Pose%03d' % ibshape].value = bshape
            if frame is not None:
                self.ob.data.shape_keys.key_blocks['Pose%03d' % ibshape].keyframe_insert(
                    'value', index=-1, frame=frame)
        # apply shape blendshapes
        for ibshape, shape_elem in enumerate(shape):
            self.ob.data.shape_keys.key_blocks['Shape%03d' % ibshape].value = shape_elem
            if frame is not None:
                self.ob.data.shape_keys.key_blocks['Shape%03d' % ibshape].keyframe_insert(
                    'value', index=-1, frame=frame)

        # apply face shape blendshapes
        if isinstance(expression,type(None)):
            expression=[0.0]*10
        for ibshape, shape_elem in enumerate(expression):
            self.ob.data.shape_keys.key_blocks['Exp%03d' % ibshape].value = shape_elem
            if frame is not None:
                self.ob.data.shape_keys.key_blocks['Exp%03d' % ibshape].keyframe_insert(
                    'value', index=-1, frame=frame)

        if frame==1:
            self.minz = get_minz()

    def reset_pose(self):
        self.arm_ob.pose.bones[
            "root"
            ].rotation_quaternion = Quaternion((1, 0, 0, 0))

    def reset_joint_positions(self, shape):
        """
        Reset the joint positions of the character according to its new shape
        """
        orig_trans = np.asarray(
            self.arm_ob.pose.bones["pelvis"].location).copy()
        # zero the pose and trans to obtain joint positions in zero pose
        self.apply_trans_pose_shape(orig_trans, np.zeros(55*3), shape,np.zeros(10))

        # obtain a mesh after applying modifiers
        bpy.ops.wm.memory_statistics()
        # me holds the vertices after applying the shape blendshapes
        # me = self.ob.to_mesh(scene, True, 'PREVIEW')  # blender < 2.8x
        depsgraph = bpy.context.evaluated_depsgraph_get()
        me = self.ob.evaluated_get(depsgraph).to_mesh()

        num_vertices = len(me.vertices)  
        reg_vs = np.empty((num_vertices, 3))
        for iiv in range(num_vertices):
            reg_vs[iiv] = me.vertices[iiv].co
        # bpy.data.meshes.remove(me)  # blender < 2.8x
        self.ob.evaluated_get(depsgraph).to_mesh_clear()

        # regress joint positions in rest pose
        joint_xyz = self.joint_regressor.dot(reg_vs)
        # adapt joint positions in rest pose
        # self.arm_ob.hide = False
        # Added this line
        # bpy.context.scene.objects.active = self.arm_ob  # blender < 2.8x
        bpy.context.view_layer.objects.active = self.arm_ob
        bpy.ops.object.mode_set(mode="EDIT")
        # self.arm_ob.hide = True
        for ibone in range(55):
            bb = self.arm_ob.data.edit_bones[
                self.part_match["bone_{:02d}".format(ibone)]
            ]
            bboffset = bb.tail - bb.head
            bb.head = joint_xyz[ibone]
            bb.tail = bb.head + bboffset
        bpy.ops.object.mode_set(mode="OBJECT")



def get_minz():
    obj = bpy.context.object.children[0]

    depsgraph = bpy.context.evaluated_depsgraph_get()

    eval_obj_graph=obj.evaluated_get(depsgraph)

    vertices_world = [vertex.co for vertex in eval_obj_graph.data.vertices]

    z_min = (min(vertices_world, key=lambda item: item.z)).z

    return z_min