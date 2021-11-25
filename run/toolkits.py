


from types import new_class
from numpy import not_equal
from tqdm import tqdm 
import os
import numpy as np 

from tools.cam import set_camera
from tools.random_utils import pick_cam
from pipeline import PipeLine
from tools.light import random_light
import bpy

from tools.random_utils import (pick_shape_whole,
gender_generator,pick_background,pick_texture)

def sing_view_render(renderer,
                    pose_data,
                    trans_data,
                    cfg,
                    cam_obs=None,
                    fskip=1):

    '''
    renderer: the render engine.
    pose_data: the objects' animation pose data
    trans_data: the object's location data.
    
    '''
    
    # pose_data [N,num_frames,72]
    # trans_data [N,num_frames,3]

    assert pose_data.shape[0]==trans_data.shape[0]
    assert pose_data.shape[1]==trans_data.shape[1]

    num_object=renderer.num_object
    assert num_object <=pose_data.shape[0]

    num_frame=pose_data.shape[1]

    if not  isinstance(cam_obs,type(None)):
        # random generate camera parameters
        # random cam dist
        # random cam height
        # random zrot
        # cam_height,cam_dist,cam_zrot = pick_cam(cfg.Engine.Renderer.camera.cam_height_range,
        #                                         cfg.Engine.Renderer.camera.cam_dist_range)
        cam_height,cam_dist,cam_zrot = cam_obs
        cam_obs = set_camera(cam_dist=cam_dist, cam_height=cam_height, zrot_euler=cam_zrot)

    # transpose
    pose_data = pose_data.transpose(1,0,2)  # [num_frames,N,72]
    trans_data = trans_data.transpose(1,0,2) # [num_frames,N,3]

    for frame in tqdm(range(0,num_frame,fskip)):
        p=pose_data[frame]
        t=trans_data[frame]
        renderer.apply_input(pose=p,trans=t,cam=cam_obs)
    renderer.render()


    

def multi_view_render(num_view,
                    num_models,
                    name,
                    pose_data,
                    trans_data,
                    cfg,
                    cam_obs=None,
                    genders=None,
                    bg_img=None,
                    textures=None,
                    shape=None,
                    lights=None,
                    fskip=1):
    
    # pose_data [N,num_frames,72]
    # trans_data [N,num_frames,3]
    

    # >>>>> init <<<<<<<<

    assert pose_data.shape[0]==trans_data.shape[0]
    assert pose_data.shape[1]==trans_data.shape[1]

    # num_object=renderer.num_object
    assert num_models <=pose_data.shape[0]

    num_frame=pose_data.shape[1]

    
    if  isinstance(cam_obs,type(None)):
        # random generate camera parameters
        # random cam dist
        # random cam height
        # random zrot
        cam_obs=[]
        for i in range(num_view):
            cam_height,cam_dist,cam_zrot = pick_cam(cfg.Engine.Renderer.camera.cam_height_range,
                                                    cfg.Engine.Renderer.camera.cam_dist_range)

            # ob = set_camera(cam_dist=cam_dist, cam_height=cam_height, zrot_euler=cam_zrot)
            cam_obs.append([cam_height,cam_dist,cam_zrot])

    # need input lights parameters
    init_lights=[]
    if not lights:
        init_lights=random_light()
    else:
        init_lights=lights

    # need to input genders.
    init_genders=[]
    if not genders:
        init_genders=gender_generator(num_models)
    else:
        init_genders=genders

    # need to input smpl model shape
    init_shape=[]
    if not shape:
        smpl_data = np.load(os.path.join(cfg.Engine.Model.SMPL.smpl_dir,
                            cfg.Engine.Model.SMPL.smpl_data_filename))

        for id in range(num_models):
            init_shape.append(pick_shape_whole(smpl_data,init_genders[id]))  
    else:
        init_shape=shape
    


    # need to input bg_img
    init_bg_img=None
    if not bg_img:
        init_bg_img = pick_background(cfg.Engine.input.bg_images.dir,
                                          cfg.Engine.input.bg_images.txt)  # image dir/image_name.
    else:
        init_bg_img=bg_img

    # need to input textures
    init_textures=[]
    if not init_textures:

        for id in range(num_models):
            init_textures.append(
                     pick_texture(cfg.Engine.input.uv_textures.clothing_option,
                                       cfg.Engine.input.uv_textures.dir,
                                       cfg.Engine.input.uv_textures.txt)
            )




    # <<<<<<<<init end >>>>>>>>>>

    for view in range(num_view):
        view_name = 'camera_{:04d}'.format(view)
        cam = cam_obs[view]
        renderer = PipeLine(cfg,name,view_name,num_models,
                    genders=init_genders,bg_img=init_bg_img,
                    textures=init_textures,shape=init_shape,sh_coeffs=init_lights)


        sing_view_render(renderer,pose_data,trans_data,cfg,cam_obs=cam,fskip=fskip)
        bpy.ops.object.select_all(action='DESELECT')
    # <<<<<<<<<<< render over >>>>>>>>>>

    



    
