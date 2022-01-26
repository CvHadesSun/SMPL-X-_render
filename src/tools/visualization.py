'''
Date: 2022-01-26 15:50:36
LastEditors: cvhadessun
LastEditTime: 2022-01-26 16:41:41
FilePath: /PG-engine/src/tools/visualization.py
'''
import cv2
import numpy as np
import os

def vis_2d_joints(img,joints2d):
    h,w,_=img.shape
    color = (0, 255, 0) 
    for i in range(joints2d.shape[0]):
        x,y = joints2d[i]
        y = h-y
        cv2.circle(img,[int(x),int(y)],2,color,-1)

    return img



def read_labelInfo(label_info_npz):
    # 
    '''
    key:
        base_info
        joints_label
    '''
    with np.load(label_info_npz,allow_pickle=True) as data:
        joints2d = data['joints2D']
        # joints_label = data['joints_label']
    return joints2d



# frame_id = 1
# obj_id = 0
# img_path = '../../output/debug/RGB/Camera.009'
# img_name = 'Image{:04d}.png'.format(frame_id)

# joints= {}
# joints2d= read_labelInfo('../../output/debug/labelInfo/Camera.009_label.npz')

# img = cv2.imread(os.path.join(img_path,img_name))

# img=vis_2d_joints(img,joints2d[obj_id,frame_id,:,:])

# cv2.imwrite('./test.png',img)