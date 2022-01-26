'''
Date: 2022-01-25 17:20:12
LastEditors: cvhadessun
LastEditTime: 2022-01-25 18:53:59
FilePath: /PG-engine/src/tools/image_transform.py
'''

import OpenEXR
import Imath
import array
import numpy as np 
import cv2

FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
# depth
path = '/home/swh/workspace/PG-engine/output/debug/experimental/Camera.009/00000_normal/Image0001.exr'
exr_file = OpenEXR.InputFile(path)


def exr_2_png_depth(exr_path,save_path,resx=640,resy=480):
    exr_file = OpenEXR.InputFile(exr_path)
    r = array.array("f", exr_file.channel('R', FLOAT)).tolist()
    r_img = np.array(r).reshape(resy,resx)
    img = np.zeros([resy,resx,3]).astype(np.uint16)
    img = np.zeros([resy,resx,3]).astype(np.uint16)
    img[:,:,0] = r_img
    img[:,:,1] = r_img
    img[:,:,2] = r_img
    cv2.imwrite(save_path,img,[int(cv2.IMWRITE_PNG_COMPRESSION), 0])
    # ori_img = cv2.imread(save_path,-1)

    
def get_normal_from_exr(exr_path,resx=640,resy=480):
    exr_file = OpenEXR.InputFile(exr_path)
    r = array.array("f", exr_file.channel('R', FLOAT)).tolist()
    g = array.array("f", exr_file.channel('G', FLOAT)).tolist()
    b = array.array("f", exr_file.channel('B', FLOAT)).tolist()
    r = np.array(r).reshape(resy,resx)
    g = np.array(g).reshape(resy,resx)
    b = np.array(b).reshape(resy,resx)
    return [r,g,b]

