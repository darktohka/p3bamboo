from panda3d.core import Datagram, DatagramIterator
from collections import OrderedDict
from p3bamboo.BamFactory import BamFactory
from p3bamboo.BamGlobals import InvalidBAMException
from p3bamboo import BamGlobals
import os

"""
  P3BAMBOO
  Panda3D BAM file library

  Author: Disyer
  Date: 2020/10/16
"""

class BamFile(object):
    HEADER = b'pbj\x00\n\r'

    def __init__(self):
        self.header_size = -1
        self.bam_major_ver = -1
        self.bam_minor_ver = -1
        self.file_endian = -1
        self.stdfloat_double = -1
        self.nesting_level = -1
        self.type_handles = {}
        self.objects = OrderedDict()
        self.file_datas = []
        self.filename = None
        self.write_long_pointers = False
        self.read_long_pointers = False
        self.warn_truncated_data = False
        self.unknown_handles = []
        self.object_map = {}
        self.pta_map = {}

    def set_filename(self, filename):
        self.filename = os.path.abspath(filename)

    def get_filename(self):
        return self.filename

    def get_object(self, object_id):
        return self.object_map.get(object_id)

    def get_handle_id_by_name(self, handle_name):
        if not isinstance(handle_name, str):
            return handle_name

        for handle_id, handle in self.type_handles.items():
            if handle['name'] == handle_name:
                return handle_id

    def find_parent(self, handle_id, parent_id):
        handle = self.type_handles[handle_id]
        parents = list(handle['parent_classes'])

        if parent_id in parents:
            return True

        for parent_class in parents:
            if self.find_parent(parent_class, parent_id):
                return True

        return False

    def find_children(self, parent_id):
        return [handle_id for handle_id in self.type_handles.keys() if self.find_parent(handle_id, parent_id)]

    def find_related(self, parent_id):
        parent_id = self.get_handle_id_by_name(parent_id)

        if parent_id is None:
            return []

        children = self.find_children(parent_id)

        if parent_id not in children:
            children.append(parent_id)

        return children

    def get_objects_of_type(self, type_name):
        type_id = self.get_handle_id_by_name(type_name)

        for obj_id, obj in self.objects.items():
            if obj['handle_id'] == type_id and obj_id in self.object_map:
                yield self.object_map[obj_id]

    def load(self, f):
        if f.read(len(self.HEADER)) != self.HEADER:
            raise InvalidBAMException('Invalid BAM header.')

        dg = Datagram(f.read())
        di = DatagramIterator(dg)
        self.header_size = di.get_uint32()
        self.bam_major_ver = di.get_uint16()
        self.bam_minor_ver = di.get_uint16()
        self.version = (self.bam_major_ver, self.bam_minor_ver)
        self.read_long_pointers = False
        self.type_handles = {}
        self.file_datas = []
        self.objects.clear()

        if self.version >= (5, 0):
            self.file_endian = di.get_uint8()
        else:
            self.file_endian = 1

        if self.version >= (6, 27):
            self.stdfloat_double = di.get_bool()
        else:
            self.stdfloat_double = False

        self.nesting_level = 0
        self.unknown_handles = []
        self.object_map = {}
        self.pta_map = {}

        # New object stream format: read object hierarchy
        while di.getRemainingSize() > 0:
            self.read_object_code(di)

    def read_stdfloat(self, di):
        if self.stdfloat_double:
            return di.get_float64()
        else:
            return di.get_float32()

    def write_stdfloat(self, dg, value):
        if self.stdfloat_double:
            dg.add_float64(value)
        else:
            dg.add_float32(value)

    def read_ushort_array(self, di):
        return self.read_array(di, lambda di: di.get_uint16())

    def read_int_array(self, di):
        return self.read_array(di, lambda di: di.get_uint32())

    def read_vec2_array(self, di):
        return self.read_array(di, BamGlobals.read_vec2)

    def read_vec3_array(self, di):
        return self.read_array(di, BamGlobals.read_vec3)

    def read_vec4_array(self, di):
        return self.read_array(di, BamGlobals.read_vec4)

    def read_array(self, di, reader):
        ipd_pointer = di.get_uint16()

        if ipd_pointer == 0:
            if di.get_uint32() != 0:
                raise Exception('Expected zero length IPD array.')

            return []

        if ipd_pointer not in self.pta_map:
            self.pta_map[ipd_pointer] = [reader(di) for i in range(di.get_uint32())]

        return self.pta_map[ipd_pointer]

    def read_pointer(self, di):
        if self.read_long_pointers:
            return di.get_uint32()

        pointer = di.get_uint16()

        if pointer == 0xFFFF:
            self.read_long_pointers = True

        return pointer

    def read_pointer_uint32_list(self, di):
        return [self.read_pointer(di) for i in range(di.get_uint32())]

    def read_pointer_int32_list(self, di):
        return [self.read_pointer(di) for i in range(di.get_int32())]

    def write_pointer_uint32_list(self, dg, pointers):
        dg.add_uint32(len(pointers))

        for pointer in pointers:
            self.write_pointer(dg, pointer)

    def write_pointer_int32_list(self, dg, pointers):
        dg.add_int32(len(pointers))

        for pointer in pointers:
            self.write_pointer(dg, pointer)

    def write_pointer(self, dg, pointer):
        if self.write_long_pointers:
            return dg.add_uint32(pointer)

        if pointer == 0xFFFF:
            self.write_long_pointers = True

        return dg.add_uint16(pointer)

    def dump_handles(self):
        dump = []

        for handle_id, handle in self.type_handles.items():
            dump.append(f'{handle_id}: {handle}')

        return '\n'.join(dump)

    def dump_objects(self):
        dump = []

        for obj_id, obj in self.objects.keys():
            actual_obj = self.get_object(obj_id)

            if actual_obj is None:
                dump.append(f'{obj_id}: data, {obj}')
            else:
                dump.append(f'{obj_id}: {actual_obj}')

        return '\n'.join(dump)

    def read_datagram(self, di):
        num_bytes = di.get_uint32()
        data = di.extractBytes(num_bytes)
        dg = Datagram(data)
        return dg

    def read_handle(self, di, parent=None):
        handle_id = di.get_uint16()

        if handle_id == 0:
            return handle_id

        if handle_id not in self.type_handles:
            # Registering a new handle!
            # Let's read the type information.
            name = di.get_string()
            num_parent_classes = di.get_uint8()
            parent_classes = []

            for _ in range(num_parent_classes):
                parent_classes.append(self.read_handle(di))

            self.type_handles[handle_id] = {'name': name, 'parent_classes': parent_classes}

        return handle_id

    def read_freed_object_codes(self, di):
        obj_ids = []

        while di.get_remaining_size() > 0:
            obj_ids.append(self.read_pointer(di))

        return obj_ids

    def read_file_data(self, di):
        num_bytes = di.get_uint32()

        # (uint32_t) -1
        if num_bytes == 0xFFFFFFFF:
            num_bytes = di.get_uint64()

        return di.extractBytes(num_bytes)

    def read_object_code(self, di):
        dg = self.read_datagram(di)
        dgi = DatagramIterator(dg)

        if self.version >= (6, 21):
            opcode = dgi.get_uint8()
        else:
            opcode = BamGlobals.BOC_adjunct

        if opcode == BamGlobals.BOC_push:
            self.nesting_level += 1
            return self.read_object(dgi)
        elif opcode == BamGlobals.BOC_pop:
            self.nesting_level -= 1
        elif opcode == BamGlobals.BOC_adjunct:
            return self.read_object(dgi)
        elif opcode == BamGlobals.BOC_remove:
            self.read_freed_object_codes(dgi)
            return self.read_object_code(di)
        elif opcode == BamGlobals.BOC_file_data:
            self.file_datas.append(self.read_file_data(dgi))
            return self.read_object_code(di)

    def read_object_from_dg(self, di):
        dg = self.read_datagram(di)
        dgi = DatagramIterator(dg)
        return self.read_object(dgi)

    def read_object(self, dgi):
        handle_id = self.read_handle(dgi)
        obj_id = self.read_pointer(dgi)
        data = dgi.extract_bytes(dgi.get_remaining_size())

        handle_name = self.type_handles[handle_id]['name']

        obj = {'handle_id': handle_id, 'handle_name': handle_name, 'obj_id': obj_id, 'data': data}
        node = BamFactory.create(self, self.version, handle_name)

        if node is not None:
            node.load_object(obj)
            self.object_map[obj_id] = node
        elif handle_name not in self.unknown_handles:
            self.unknown_handles.append(handle_name)

        if obj_id in self.objects:
            raise InvalidBAMException(f'Object ID {obj_id} ({handle_name}) was encountered twice in the BAM stream!')

        self.objects[obj_id] = obj

    def write_handle(self, dg, handle_id, written_handles):
        dg.add_uint16(handle_id)

        if handle_id == 0:
            # Panda does not read any further information for handle_id == 0
            return
        if handle_id in written_handles:
            # We've already written this handle, we don't have to do it again.
            return

        # We haven't written any handles yet...
        handle = self.type_handles[handle_id]
        parent_classes = handle['parent_classes']

        written_handles.append(handle_id)

        dg.add_string(handle['name'])
        dg.add_uint8(len(parent_classes))

        for handle_id in parent_classes:
            # Write all of our parent handles.
            self.write_handle(dg, handle_id, written_handles)

    def write_file_data(self, dg, data):
        num_bytes = len(data)

        if num_bytes >= 0xFFFFFFFF:
            dg.add_uint32(0xFFFFFFFF)
            dg.add_uint64(num_bytes)
        else:
            dg.add_uint32(num_bytes)

        dg.append_data(data)

    def write_object(self, dg, opcode, obj=None, written_handles=None):
        obj_dg = Datagram()

        if self.version >= (6, 21):
            obj_dg.add_uint8(opcode)

        if obj is not None:
            obj_id = obj['obj_id']
            instance = self.object_map.get(obj_id)

            self.write_handle(obj_dg, obj['handle_id'], written_handles)
            self.write_pointer(obj_dg, obj_id)

            if instance:
                instance.write_object(self.version, obj)

            obj_dg.appendData(obj['data'])

        self.write_datagram(obj_dg, dg)

    def write_datagram(self, dg, target_dg):
        msg = dg.getMessage()

        target_dg.add_uint32(len(msg))
        target_dg.append_data(msg)

    def write(self, f):
        dg = Datagram()
        dg.appendData(self.HEADER)

        if self.version >= (6, 27):
            header_size = 6
        elif self.version >= (5, 0):
            header_size = 5
        else:
            header_size = 4

        bam_major_ver, bam_minor_ver = self.version
        dg.add_uint32(header_size)
        dg.add_uint16(bam_major_ver)
        dg.add_uint16(bam_minor_ver)

        if header_size >= 5:
            dg.add_uint8(self.file_endian)

        if header_size >= 6:
            dg.add_bool(self.stdfloat_double)

        self.written_handles = []
        self.write_long_pointers = False

        if self.objects:
            objects = list(self.objects.values())
            self.write_object(dg, BamGlobals.BOC_push, objects[0], self.written_handles)

            for obj in objects[1:]:
                self.write_object(dg, BamGlobals.BOC_adjunct, obj, self.written_handles)

        for data in self.file_datas:
            self.write_file_data(dg, data)

        if self.version >= (6, 21):
            self.write_object(dg, BamGlobals.BOC_pop)

        f.write(dg.getMessage())

    def __str__(self):
        return 'Panda3D BAM file version {0}.{1} ({2}, {3})'.format(
            self.bam_major_ver, self.bam_minor_ver,
            'Big-endian' if self.file_endian == 0 else 'Little-endian',
            '64-bit' if self.stdfloat_double else '32-bit'
        )
