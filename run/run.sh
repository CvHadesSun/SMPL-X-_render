
###
 # @Author: your name
 # @Date: 2021-11-16 14:19:16
 # @LastEditTime: 2022-01-21 17:27:41
 # @LastEditors: cvhadessun
 # @Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 # @FilePath: /PG-engine/run/run.sh
### 
BLENDER_PATH=/home/swh/tools/blender-2.93.3-linux-x64


# JOB_PARAMS=${1:-'
#     --view_id ${1}
#     --name debug
#     --cam_height ${cam_height}
#     --cam_dist ${cam_dist}
#     --zrot ${zrot[i]}
#     --label multi_tmp/data.mat
#     --fskip 20'}

# $BLENDER_PATH/blender -b -t 1 -P main.py

# $BLENDER_PATH/blender -b  -P multi_view.py -- ${JOB_PARAMS}

$BLENDER_PATH/blender -b  -t 1 -P demo/demo_smplx_new.py