'''
Date: 2021-12-30 14:43:40
LastEditors: cvhadessun
LastEditTime: 2021-12-30 14:53:43
FilePath: /PG-engine/src/tools/model_params_process.py
'''


import pickle as pkl
import os


def extract_J_regressor(male_pkl=None,neutal_pkl=None,female_pkl=None,output_path=None):
    # 
    J_regressor={}
    if not isinstance(male_pkl,type(None)):
        model_m = pkl.load(
            open(male_pkl, "rb"),
            encoding="latin1",
        )
        J_regressor['J_regressor_male']=model_m["J_regressor"]
    if not isinstance(neutal_pkl,type(None)):
        model_n = pkl.load(
            open(male_pkl, "rb"),
            encoding="latin1",
        )
        J_regressor['J_regressor_neutral']=model_n["J_regressor"]
    if not isinstance(female_pkl,type(None)):
        model_f = pkl.load(
            open(male_pkl, "rb"),
            encoding="latin1",
        )
        J_regressor['J_regressor_female']=model_f["J_regressor"]
    

    if not isinstance(output_path,type(None)):
        pkl.dump(J_regressor, open(output_path, "wb"))



root_path='/home/swh/work_space/smpl-data/smplx/data/smplx'
male=os.path.join(root_path,'SMPLX_MALE.pkl')
female=os.path.join(root_path,'SMPLX_FEMALE.pkl')
neutral=os.path.join(root_path,'SMPLX_NEUTRAL.pkl')
extract_J_regressor(male,neutral,female,os.path.join(root_path,"../joint_regressors.pkl"))