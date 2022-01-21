'''
Date: 2022-01-21 16:54:30
LastEditors: cvhadessun
LastEditTime: 2022-01-21 18:00:59
FilePath: /PG-engine/run/video_render.py
'''

import os
from os.path import join
import argparse
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(cur_dir,'..')
sys.path.insert(0,os.path.join(root_dir,'src'))
sys.path.insert(0,os.path.join(root_dir,'run'))

from tools.file_op import mkdir_safe

def parser_upate():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--images_folder', '-f', type=str, default='test',
                    help='the images folders to convert to video.')
    parser.add_argument('--extend','-e',  type=str, default='mp4',
                    help='the output video format.')
    parser.add_argument('--output_path','-o',  type=str, default='test',
                    help='the output video path.')
    # tmp=sys.argv[sys.argv.index("--") + 1 :]
    return parser.parse_args()


data_dir='../output/debug/experimental/Camera.009/00000_fg'

cam_name='camera_0000'

if __name__=="__main__":
    # args=parser_upate()

    output_video=os.path.join(os.path.dirname(data_dir),'videos')
    mkdir_safe(output_video)

    for i in range(1):
        print(i)
        # dir=os.path.join(data_dir,str(i),cam_name)
        dir = data_dir
        video_name='{:02d}'.format(i)+'.mp4'
        fg_mp4_path=os.path.join(output_video,video_name)
        # 
        # imgs=os.listdir(os.path.join(dir,'experimental','00000_fg'))
        # imgs=sorted(imgs,key=lambda x: int(x.split('.')[0][5:]))

        cmd_ffmpeg_fg = (
            "ffmpeg  -loglevel panic -y -r 30 -i "
            "{}"
            " -c:v h264 -pix_fmt yuv420p -crf 23 "
            "{}"
            "".format(join(dir, "Image%04d.png"), fg_mp4_path)
        )
        print(dir)
        print(os.path.exists(join(dir, "Image0001.png")))
        os.system(cmd_ffmpeg_fg)

    


