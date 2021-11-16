'''
Author: your name
Date: 2021-11-09 16:55:01
LastEditTime: 2021-11-09 16:56:17
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /PG-engine/src/config/__init__.py
'''

from .yac import CfgNode as CN
import os
import sys

cfg = CN()

current_dir = os.path.dirname(__file__)
cfg = CN()
cfg.merge_from_file(os.path.join(current_dir,'cfg.yml'))