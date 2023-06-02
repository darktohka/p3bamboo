"""
  P3BAMBOO
  Panda3D BAM file library

  Author: Disyer
  Date: 2020/10/16
"""

class BAMException(Exception):
    pass

### BAM object codes
BOC_push = 0
BOC_pop = 1
BOC_adjunct = 2
BOC_remove = 3
BOC_file_data = 4
### BAM object codes

def read_vec2(di):
    return (di.get_float32(), di.get_float32())

def read_vec3(di):
    return (di.get_float32(), di.get_float32(), di.get_float32())

def read_vec4(di):
    return (di.get_float32(), di.get_float32(), di.get_float32(), di.get_float32())

def write_vec(dg, vec):
    for i in vec:
        dg.add_float32(i)

def write_ushort_arr(dg, arr):
    num = len(arr)
    dg.add_uint32(num)

    for element in arr:
        dg.add_uint16(element)

def write_int_arr(dg, arr):
    num = len(arr)
    dg.add_uint32(num)

    for element in arr:
        dg.add_uint32(element)

def write_vec_arr(dg, arr):
    num = len(arr)
    dg.add_uint32(num)

    for element in arr:
        write_vec(dg, obj)
