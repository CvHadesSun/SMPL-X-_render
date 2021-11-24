'''
Author: cvhades
Date: 2021-11-10 15:24:11
LastEditTime: 2021-11-24 11:57:53
LastEditors: Please set LastEditors
FilePath: /PG-engine/src/lib/Render/output_info.py
'''
from os.path import join
import numpy as np
import json
import scipy.io as sio
import cv2


# to output the gt data.
class Label:
    def __init__(self,cfg,name,num_object,
                gender=None,
                shape=None,
                bg=None,
                cloth_img=None,
                source=None,
                zrot_euler=None,
                light=None,
                cam_height=None,
                cam_dist=None) -> None:

        self.cfg = cfg
        self.dict_info={}
        self.output_name=cfg.Engine.output.labels.output_name
        self.output_path=join(cfg.Engine.output.output_path,self.output_name)
        
        # self.format=self.cfg.Engine.output.labels.format
        # set the num object
        self.dict_info["num_object"]=num_object
        self.num_obj=num_object
        # set output 
        if 'mat' in self.cfg.Engine.output.labels.format:
            self.output_file=join(self.output_path,name+'.mat')

            if self.cfg.Engine.output.labels.bg and bg:
                self.dict_info['bg'] = cv2.imread(bg)
            if self.cfg.Engine.output.labels.cloth and cloth_img:
                self.dict_info['cloth']=cv2.imread(cloth_img)

            if self.cfg.Engine.output.labels.gender and gender:
                self.dict_info['gender']=gender

            if self.cfg.Engine.output.labels.pose:
                self.dict_info['pose']=[]
        
            if self.cfg.Engine.output.labels.shape:
                self.dict_info['shape']=[]

            if self.cfg.Engine.output.labels.pose:
                self.dict_info['pose']=[]

            if self.cfg.Engine.output.labels.source and source:
                self.dict_info['source']=source

            if self.cfg.Engine.output.labels.zrot_euler and zrot_euler:
                self.dict_info['zrot_euler']=zrot_euler
            
            if self.cfg.Engine.output.labels.light and light:
                self.dict_info['light']=light

            if self.cfg.Engine.output.labels.cam_height and cam_height:
                self.dict_info['cam_height']=cam_height
            
            if self.cfg.Engine.output.labels.cam_dist and cam_dist:
                self.dict_info['cam_dist']=cam_dist

            if self.cfg.Engine.output.labels.joints2D:
                self.dict_info['joints2D']=[]

            if self.cfg.Engine.output.labels.joints3D:
                self.dict_info['joints3D']=[]
        elif 'json' in self.cfg.Engine.output.labels.format:

            self.output_file=join(self.output_path,name+'.json')
            if self.cfg.Engine.output.labels.bg and bg:
                self.dict_info['bg'] = bg
            if self.cfg.Engine.output.labels.cloth and cloth_img:
                self.dict_info['cloth']=cloth_img

            if self.cfg.Engine.output.labels.gender and gender:
                self.dict_info['gender']=gender

            if self.cfg.Engine.output.labels.pose:
                self.dict_info['pose']=[]

            if self.cfg.Engine.output.labels.shape:
                self.dict_info['shape']=[]

            if self.cfg.Engine.output.labels.pose:
                self.dict_info['pose']=[]

            if self.cfg.Engine.output.labels.source and source:
                self.dict_info['source']=source

            if self.cfg.Engine.output.labels.zrot_euler and zrot_euler:
                self.dict_info['zrot_euler']=zrot_euler
                
            if self.cfg.Engine.output.labels.light and light:
                self.dict_info['light']=light

            if self.cfg.Engine.output.labels.cam_height and cam_height:
                self.dict_info['cam_height']=cam_height
            
            if self.cfg.Engine.output.labels.cam_dist and cam_dist:
                self.dict_info['cam_dist']=cam_dist

            if self.cfg.Engine.output.labels.joints2D:
                self.dict_info['joints2D']=[]

            if self.cfg.Engine.output.labels.joints3D:
                self.dict_info['joints3D']=[]
        else:
            raise('Not support %sformat'%self.cfg.Engine.output.labels.format)

        # if self.cfg.Engine.output.labels.shape and shape:
        #     self.dict_info['shape']=shape  # shape:[[10],[10],...[10]]

    def add_info(self,joints2d=None,joints3d=None,pose=None):
        # pre frame.
        # joints2d:[[2,24],[2,24],...[2,24]]  len=num people. [N,2,24]
        # joints3d:[[3,24],[3,24],...[3,24]]
        # pose:[[72],[72],...[72]]
        
        if joints2d:
            self.dict_info['joints2D'].append(joints2d)
        if joints3d:
            self.dict_info['joints3D'].append(joints3d)

        if pose:
            self.dict_info['pose'].append(pose)


    def save_info(self):
        if 'mat' in self.cfg.Engine.output.labels.format:
            pass
        elif 'json' in self.cfg.Engine.output.labels.format:
            pass

        else:
            raise('Not support %sformat'%self.cfg.Engine.output.labels.format)

    def mat_save(self):
        # to save .mat format file 

        joints_2d=np.array(self.dict_info['joints2D']).reshape(-1,self.num_obj,2,24)  #[num_frames,num_obj,2,24]
        joints_3d=np.array(self.dict_info['joints3D']).reshape(-1,self.num_obj,3,24)
        pose=np.array(self.dict_info['pose']).reshape(-1,self.num_obj,72)  

        self.dict_info['joints2D']=joints_2d
        self.dict_info['joints3D']=joints_3d
        self.dict_info['pose']=pose

        sio.savemat(self.output_file, self.dict_info, do_compression=True)


    def json_save(self):
        # to save .json format file.
        

        
        
        
    