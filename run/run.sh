
###
 # @Author: your name
 # @Date: 2021-11-16 14:19:16
 # @LastEditTime: 2021-11-26 15:27:32
 # @LastEditors: Please set LastEditors
 # @Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 # @FilePath: /PG-engine/run/run.sh
### 
BLENDER_PATH=/home/hades/workspace/surreact/blender-2.92.0-linux64
CODE_PATH=/scratch/shared/beegfs/gul/surreact_project/surreact

# JOB_PARAMS=${1:-'
#     --view_id ${1}
#     --name debug
#     --cam_height ${cam_height}
#     --cam_dist ${cam_dist}
#     --zrot ${zrot[i]}
#     --label multi_tmp/data.mat
#     --fskip 20'}

$BLENDER_PATH/blender -b -t 1 -P main.py
# $BLENDER_PATH/blender -b  -P multi_view.py -- ${JOB_PARAMS}