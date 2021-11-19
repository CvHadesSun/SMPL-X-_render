

from tqdm import tqdm 

def sing_view_render(renderer,pose_data,trans_data,fskip=1):
    
    # pose_data [N,num_frames,72]
    # trans_data [N,num_frames,3]

    assert pose_data.shape[0]==trans_data.shape[0]
    assert pose_data.shape[1]==trans_data.shape[1]

    num_object=renderer.num_object
    assert num_object <=pose_data.shape[0]

    num_frame=pose_data.shape[1]

    for obj in num_object:
        for frame in tqdm(range(0,num_frame,fskip)):
            p=pose_data[id][frame].reshape(1,-1)
            t=trans_data[id][frame].reshape(1,-1)
            renderer.apply_input(pose=p,trans=t)
    renderer.render()


    