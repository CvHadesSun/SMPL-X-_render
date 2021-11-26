
#env
BLENDER_PATH=/home/hades/workspace/surreact/blender-2.92.0-linux64
CODE_PATH=/scratch/shared/beegfs/gul/surreact_project/surreact


# cam
cam_height=1.0
cam_dist=8.0
zrot="0 45 90 135 180 225 270 315"
name=debug
skip=20
# JOB_PARAMS=${1:-'
#     --view_id 0
#     --name debug
#     --cam_height ${cam_height}
#     --cam_dist ${cam_dist}
#     --zrot ${zrot[i]}
#     --label multi_tmp/data.mat
#     --fskip 20'}
i=0
for v in ${zrot}
do
    # ./run.sh '--view_id ${i} \
    #         --name ${name} \
    #         --cam_height ${cam_height} \
    #         --cam_dist ${cam_dist} \
    #         --zrot ${zrot[i]} \
    #         --label multi_tmp/data.mat\
    #         --fskip 20'

    JOB_PARAMS={1:-"
    --view_id  ${v}
    --name debug
    --cam_height ${cam_height}
    --cam_dist ${cam_dist}
    --zrot ${v}
    --label multi_tmp/data.mat
    --fskip ${skip}"
    # --fskip ${skip}"}
    $BLENDER_PATH/blender -b  -P multi_view.py -- ${JOB_PARAMS}

    
done




