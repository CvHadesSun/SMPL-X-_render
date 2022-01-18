'''
Date: 2022-01-18 17:16:59
LastEditors: cvhadessun
LastEditTime: 2022-01-18 17:55:21
FilePath: /PG-engine/src/tools/light.py
'''
import numpy as np
import bpy

def random_light():
    # Random light
    sh_coeffs = 0.7 * (2 * np.random.rand(9) - 1)
    # Ambient light (first coeff) needs a minimum  is ambient. Rest is uniformly distributed, higher means brighter.
    sh_coeffs[0] = 0.5 + 0.9 * np.random.rand()
    sh_coeffs[1] = -0.7 * np.random.rand()
    return sh_coeffs


def new_light(r,h):
    # remove default light    
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete(use_global=False)

    r -=1
    locations=[[r,0,h],[-r,0,h],[0,r,h],[0,-r,h]]
    for i in range(4): # new 4 point light
        # Create new light
        lamp_data = bpy.data.lights.new(name="Lamp{}".format(i), type='POINT')
        lamp_data.energy = 1000
        lamp_object = bpy.data.objects.new(name="Lamp{}".format(i), object_data=lamp_data)
        bpy.context.collection.objects.link(lamp_object)
        lamp_object.location = locations[i]