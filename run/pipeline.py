'''
Author: cvhades
Date: 2021-11-10 17:12:09
LastEditTime: 2021-11-12 11:25:44
LastEditors: Please set LastEditors
FilePath: /PG-engine/run/pipeline.py
'''

import os
import sys


cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(cur_dir,'..')
sys.path.insert(0,os.path.join(root_dir,'src'))

from tools.file_op import mkdir_safe
import random

# TODO: the pipeline of data generation

class PipeLine:
    def __init__(self,cfg,bg_img=None,cloth_imgs=None) -> None:
        # bg_img 
        # cloth_imgs
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

        # random get the bg img and cloth img for model.
        self._set_bg(bg_img)
        self._set_obj_cloth_imgs()


    def _set_bg(self,bg_img):
        if not bg_img: 
            # random select from bg map
            pass
        else:
            self.bg=bg_img

    def _set_obj_cloth_imgs(self,cloth_imgs):
        if not cloth_imgs:
            # random select from dataset
            pass
        else:
            self.textures=cloth_imgs



    # def _pose_shape_gen(self):
    #     if self.online:
    #         print('need to implement.')
    #     else:
    #         # input the pose and shape data info.
    #         pass

    def apply_input(self,name):
        pass
        

    
        
