
###
 # @Author: your name
 # @Date: 2021-12-07 11:37:47
 # @LastEditTime: 2021-12-07 15:53:06
 # @LastEditors: Please set LastEditors
 # @Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 # @FilePath: /PG-engine/run/single_view.sh
### 

#env
BLENDER_PATH=/home/hades/workspace/surreact/blender-2.92.0-linux64
CODE_PATH=/scratch/shared/beegfs/gul/surreact_project/surreact


# cam
cam_height=1.0
cam_dist=8.0
# zrot="0 45 90 135 180 225 270 315"
zrot="0"

skip=1
# JOB_PARAMS=${1:-'
#     --view_id 0
#     --name debug
#     --cam_height ${cam_height}
#     --cam_dist ${cam_dist}
#     --zrot ${zrot[i]}
#     --label multi_tmp/data.mat
#     --fskip 20'}

for i in $(seq 0 49) 
do
for v in ${zrot}
do
#     # ./run.sh '--view_id ${i} \
#     #         --name ${name} \
#     #         --cam_height ${cam_height} \
#     #         --cam_dist ${cam_dist} \
#     #         --zrot ${zrot[i]} \
#     #         --label multi_tmp/data.mat\
#     #         --fskip 20'

    JOB_PARAMS={1:-"
    --view_id  ${v}
    --name ${i}
    --cam_height ${cam_height}
    --cam_dist ${cam_dist}
    --zrot ${v}
    --label ../label_info/data.mat
    --fskip ${skip}"
    # --fskip ${skip}"}
    $BLENDER_PATH/blender -b  -P single_view.py -- ${JOB_PARAMS}
echo ${v}

    
done
done




