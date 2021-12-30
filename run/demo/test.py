'''
Date: 2021-12-28 14:23:51
LastEditors: cvhadessun
LastEditTime: 2021-12-29 10:26:29
FilePath: /PG-engine/run/demo/test.py
'''
import json
import os
import numpy as np 

path="/home/swh/work_space/smpl-data/smplx/data"
file="smplx_betas_to_joints_male.json"

with open(os.path.join(path,file)) as fp:
    data=json.load(fp)

print(data.keys())
beta_J=np.array(data['betasJ_regr'])
template_I=np.array(data['template_J'])

print("beta_J shape:",beta_J.shape) #[55,3,10]
print("template_J shape:",template_I.shape) #[55,3]
