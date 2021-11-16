'''
Author: cvhades
Date: 2021-11-09 17:12:57
LastEditTime: 2021-11-16 15:14:41
LastEditors: Please set LastEditors
FilePath: /PG-engine/run/main.py
'''


# pipeline of datageneration

import os
import sys

from numpy import number

cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(cur_dir,'..')
sys.path.insert(0,os.path.join(root_dir,'src'))
sys.path.insert(0,os.path.join(root_dir,'run'))
from data.vibe_utils import *
from config import cfg
# update the  root_dir;
cfg.Engine.root_dir = root_dir

from pipeline import PipeLine


name='debug'
num_model=1
render=PipeLine(cfg,name, num_model, 
                genders=['female'],
                bg_img='/home/hades/workspace/data/pg-engine/bg_imgs/backgrounds/train/S001C002P001R002A009_0.jpg',
                textures=['/home/hades/workspace/surreact/datageneration/smpl_data/textures/female/nongrey_female_0120.jpg']
                )



# input pose and shape for render.

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
                with_trans=0,
                use_pose_smooth=1,
                datasetname='ntu'
            )
        )
    pose_data = [data["poses"] for data in hmmr_body_data]
    trans_data = [data["trans"] for data in hmmr_body_data]
    trans_data = center_people(trans_data)

    return pose_data,trans_data


pose,trans=load_input('S001C001P001R002A003','/home/hades/workspace/surreact/datageneration/data/ntu/vibe/train')

id=0

for i in range(5):
    p=pose[id][i].reshape(1,-1)
    t=trans[id][i].reshape(1,-1)
    render.apply_input(pose=p,trans=t)


render.render()