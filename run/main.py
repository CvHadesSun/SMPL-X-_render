'''
Author: cvhades
Date: 2021-11-09 17:12:57
LastEditTime: 2021-11-16 12:01:45
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


from config import cfg
# update the  root_dir;
cfg.Engine.dir.root_dir = root_dir

# from .pipeline import PipeLine


# cfg, name, num_model, genders=None, bg_img=None, textures=None, shape=None

# genders=['female']
name='debug'
num_model=1
# render=PipeLine(cfg,cfg, name, num_model, genders=['female'],bg_img='bg_img.jpg',textures=['test.jpg'])
