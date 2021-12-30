'''
Date: 2021-12-28 10:24:52
LastEditors: cvhadessun
LastEditTime: 2021-12-30 17:54:17
FilePath: /PG-engine/run/demo/demo_smplx.py
'''

# for smplx model

# pipeline of datageneration

import os
import sys
import json
# import cv2

cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(cur_dir,'../..')
sys.path.insert(0,os.path.join(root_dir,'src'))
sys.path.insert(0,os.path.join(root_dir,'run'))
from data.vibe_utils import *
from config import cfg

from tools.file_op import mkdir_safe
# update the  root_dir;
cfg.Engine.root_dir = root_dir
from tools.cam import set_camera
from pipeline import PipeLine

from toolkits import multi_view_render,multi_view_info_generator,load_pose_from_pare

if not os.path.exists(cfg.Engine.output_dir):
    cfg.Engine.output_dir =os.path.join(cfg.Engine.root_dir,cfg.Engine.output_dir)
    mkdir_safe(cfg.Engine.output_dir)

# two class hand pose : flat and relaxed.
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

name="smplx_debug"
num_model=1

# config modle type
cfg.Engine.Model.selected = "SMPLX"
render=PipeLine(cfg,'debug',name, num_model,
                genders=['female'])

# load pose and other paramters
smplx_dir=cfg.Engine.Model.SMPLX.smplx_dir
with open(os.path.join(smplx_dir,"data/smplx_params.json"))as fp:
    data=json.load(fp)

Rhs=np.array(data['Rh']).reshape(-1,3)
Ths=np.array(data['Th']).reshape(-1,3)
poses=np.array(data['poses']).reshape(-1,87)
expressions=np.array(data['expressions'])
shapes=np.array(data['shapes'])


# pose [22*3,12,3*3]
num_body_joints=22*3
num_hand_joints=6*2
num_face_joints=3*3

id=0

for i in range(3):
    pose=np.zeros([1,55*3])
    pose[:,:num_body_joints]=poses[i][:num_body_joints] # body
    pose[:,num_body_joints:num_body_joints+num_face_joints] = poses[i][num_body_joints+num_hand_joints:] # face
    pose[:,num_body_joints+num_face_joints:]=hand_pose['relaxed'].reshape(-1) # left hand and right hand
    # t=Ths[i].reshape(-1,3)
    # r=Rhs[i].reshape(-1,3)
    t=np.zeros([1,3])
    r=np.zeros([1,3])
    pose[:,:3]=0
    
    shape=shapes[i].reshape(-1,10)
    expression=expressions[i].reshape(-1,10)
    cam_ob=set_camera(cam_dist=7, cam_height=0, zrot_euler=180)
    render.apply_input(pose=pose,trans=t,cam=cam_ob,shape=shape,orient=r,expression=expression)

render.render()