
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


data_dir='../test_knn'

cam_name='camera_0000'

if __name__=="__main__":
    # args=parser_upate()

    mkdir_safe(os.path.join(data_dir,'videos'))

    output_video=os.path.join(os.path.join(data_dir,'videos'))

    for i in range(2):
        dir=os.path.join(data_dir,str(i),cam_name)
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
            "".format(join(dir,'experimental/00000_fg', "Image%04d.png"), fg_mp4_path)
        )

        os.system(cmd_ffmpeg_fg)

    


