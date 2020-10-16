"""
  P3BABMBOO
  Panda3D BAM file library

  Author: Disyer
  Date: 2020/10/16
"""

from panda3d.core import LVecBase2f, LVecBase3f, LVecBase4f

class InvalidBAMException(Exception):
    pass

READ_UINT32 = False
WRITE_UINT32 = False

### BAM object codes
BOC_push = 0
BOC_pop = 1
BOC_adjunct = 2
BOC_remove = 3
BOC_file_data = 4
### BAM object codes

def read_pointer(di):
    global READ_UINT32

    if READ_UINT32:
        return di.get_uint32()

    pointer = di.get_uint16()

    if pointer == 65535:
        READ_UINT32 = True

    return pointer

def write_pointer(dg, pointer):
    global WRITE_UINT32

    if WRITE_UINT32:
        dg.add_uint32(pointer)
        return

    dg.add_uint16(pointer)

    if pointer == 65535:
        WRITE_UINT32 = True

def read_vec2(di):
    return LVecBase2f(di.get_float32(), di.get_float32())

def read_vec3(di):
    return LVecBase3f(di.get_float32(), di.get_float32(), di.get_float32())

def read_vec4(di):
    return LVecBase4f(di.get_float32(), di.get_float32(), di.get_float32(), di.get_float32())

def write_vec(dg, vec):
    for i in vec:
        dg.add_float32(i)

def write_ushort_arr(dg, arr):
    num = len(arr)
    dg.add_uint32(num)

    for i in range(num):
        dg.add_uint16(arr[i])

def write_int_arr(dg, arr):
    num = len(arr)
    dg.add_uint32(num)

    for i in range(num):
        dg.add_uint32(arr[i])

def write_vec_arr(dg, arr):
    num = len(arr)
    dg.add_uint32(num)

    for obj in arr:
        write_vec(dg, obj)
