'''
Author: cvhades
Date: 2021-11-09 17:12:57
LastEditTime: 2021-11-09 17:56:13
LastEditors: Please set LastEditors
FilePath: /PG-engine/run/main.py
'''


# pipeline of datageneration

import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(cur_dir,'..')
sys.path.insert(0,os.path.join(root_dir,'src'))


# from config import cfg
# from lib.Scene.scene import Scene 
# # update the  root_dir;
# cfg.Engine.dir.root_dir = root_dir

# # print(cfg.Engine.dir.root_dir)

# s=Scene(cfg)

# import lib.Model.SMPL 