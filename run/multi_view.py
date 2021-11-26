

import argparse
import os
from pickle import load
import sys

from numpy import PINF

cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(cur_dir,'..')
sys.path.insert(0,os.path.join(root_dir,'src'))
sys.path.insert(0,os.path.join(root_dir,'run'))
from data.vibe_utils import *
from config import cfg
import scipy.io as sio

from toolkits import single_view_render
from pipeline  import PipeLine
from tools.file_op import mkdir_safe

cfg.Engine.root_dir = root_dir

if not os.path.exists(cfg.Engine.output_dir):
    cfg.Engine.output_dir =os.path.join(cfg.Engine.root_dir,cfg.Engine.output_dir)
    mkdir_safe(cfg.Engine.output_dir)


def load_tmp_info(mat_file):

    data=sio.loadmat(mat_file)

    return data




def parser_upate():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--name',  type=str, default='test',
                    help='the all view data name for mkdir.')
    parser.add_argument('--view_id',  type=int, default=0,
                    help='the view id.')
    parser.add_argument('--cam_height',  type=float, default=1.0,
                    help='the cam height.')
    parser.add_argument('--cam_dist',  type=float, default=8.0,
                    help='the cam dist.')
    parser.add_argument('--zrot',  type=float, default=0,
                    help='the cam height.')
    parser.add_argument('--label',  type=str, default='multi_view/data.mat',
                    help='the render need data input file.')
    parser.add_argument('--fskip',  type=int, default=1,
                    help='the number of skip frames')
    
    tmp=sys.argv[sys.argv.index("--") + 1 :]
    return parser.parse_args(tmp[1:])



if __name__=="__main__":

    args=parser_upate()
    print(args.view_id)

    data=load_tmp_info(args.label)
    cam=[args.cam_height,args.cam_dist,args.zrot]
    view_name = 'camera_{:04d}'.format(args.view_id)

    # print(data['light'])
    
    renderer=PipeLine(cfg,args.name,
                        view_name,
                        data['num_model'][0][0],
                        genders=data['genders'],
                        bg_img=data['bg_img'][0],
                        textures=data['textures'],
                        shape=data['shape'],
                        sh_coeffs=data['light'][0])

    single_view_render(renderer,data['pose'],data['trans'],cfg,cam_obs=cam,fskip=args.fskip)





