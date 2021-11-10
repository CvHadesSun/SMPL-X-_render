'''
Author: cvhades
Date: 2021-11-10 17:12:09
LastEditTime: 2021-11-10 17:30:53
LastEditors: Please set LastEditors
FilePath: /PG-engine/run/pipeline.py
'''

import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(cur_dir,'..')
sys.path.insert(0,os.path.join(root_dir,'src'))


# TODO: the pipeline of data generation

class PipeLine:
    def __init__(self,cfg) -> None:
        self.cfg=cfg
        self.online=cfg.Engine.Model.SMPL.online


    def _pose_shape_gen(self):
        if self.online:
            print('need to implement.')
        else:
            # input the pose and shape data info.
            pass
