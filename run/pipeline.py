'''
Author: cvhades
Date: 2021-11-10 17:12:09
LastEditTime: 2021-11-11 15:23:50
LastEditors: Please set LastEditors
FilePath: /PG-engine/run/pipeline.py
'''

import os
import sys


cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(cur_dir,'..')
sys.path.insert(0,os.path.join(root_dir,'src'))

from tools.file_op import mkdir_safe


# TODO: the pipeline of data generation

class PipeLine:
    def __init__(self,cfg) -> None:
        self.cfg=cfg
        self.online=cfg.Engine.Model.SMPL.online

        # set the output path
        if cfg.Engine.output.output is not None:
            self.output_path=cfg.Engine.output.output
        else:
            self.output_path=os.path.join(root_dir,'output')
        
        mkdir_safe(self.output_path)
        # mdkir tmp path
        # self.tmp_path=os.path.join(self.output_path,'experiment')
        # mkdir_safe(self.tmp_path)


    def _pose_shape_gen(self):
        if self.online:
            print('need to implement.')
        else:
            # input the pose and shape data info.
            pass

    def get_input(self,name):
        pass
        
        
