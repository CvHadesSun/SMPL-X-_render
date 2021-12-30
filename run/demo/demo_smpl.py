
'''
Author: cvhades
Date: 2021-11-09 17:12:57
LastEditTime: 2021-12-28 10:24:27
LastEditors: cvhadessun
FilePath: /PG-engine/run/demo/demo.py
'''

# for smpl model

# pipeline of datageneration

import os
import sys

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

name='debug1'
num_model=1

shape=[ 0.63876534, -2.0000112 ,  0.8837963 ,  1.6021069 ,  2.2627835 ,  0.43532476,
 -0.10485663,  1.0975921  , 0.7018652 ,  1.5833994 ]


render=PipeLine(cfg,'debug',name, num_model,
                genders=['female'],
                shape=[shape])

            
def load_input(name,smpl_result_path):

    hmmr_body_data = []
    num_tracks, all_track_list = count_tracks(
    name=name, smpl_result_path=smpl_result_path, datasetname='ntu'
    )
    for tid in all_track_list:
        hmmr_body_data.append(
            load_smpl_body_data(
                name=name,
                smpl_result_path=smpl_result_path,
                track_id=tid,
                with_trans=1,
                use_pose_smooth=1,
                datasetname='ntu'
            )
        )
    pose_data = [data["poses"] for data in hmmr_body_data]
    trans_data = [data["trans"] for data in hmmr_body_data]
    trans_data = center_people(trans_data)

    return pose_data,trans_data

pose,trans=load_input('S014C003P037R002A044','/home/swh/work_space/smpl-data/data/ntu/vibe/test')
pose=np.array(pose)
trans=np.array(trans)   

id=0

for i in range(3):
    p=pose[id][i:i+2].reshape(-1,72)
    # t=trans[id][i:i+2].reshape(-1,3)
    t=np.array([[-1,0,-0],[0,0,0]])
    cam_ob=set_camera(cam_dist=8, cam_height=0, zrot_euler=0)
    render.apply_input(pose=p,trans=t,cam=cam_ob)

render.render()



