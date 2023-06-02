from p3bamboo.BamGlobals import BAMException
from p3bamboo.StructDatagram import StructDatagram, StructDatagramIterator
import logging

"""
  P3BAMBOO
  Panda3D BAM file library

  Author: Disyer
  Date: 2020/10/16
"""
class BamObject(object):

    def __init__(self, bam_file, bam_version):
        self.bam_file = bam_file
        self.bam_version = bam_version
        self.extra_data = None
        self.obj_id = -1

    def to_binary(self, write_version=None):
        if write_version is None:
            write_version = self.bam_version

        dg = StructDatagram()
        self.write(write_version, dg)

        if self.extra_data:
            dg.append_data(self.extra_data)

        return dg.get_message()

    def save(self, write_version=None):
        if self.obj_id == -1:
            raise BAMException('Cannot save: object ID has not been set.')

        self.bam_file.objects[self.obj_id]['data'] = self.to_binary(write_version)

    def load_object(self, obj):
        self.obj_id = obj['obj_id']

        di = StructDatagramIterator(obj['data'])
        self.load(di)

        if di.get_remaining_size() > 0:
            self.extra_data = di.get_remaining_bytes()

            if self.bam_file.warn_truncated_data:
                logging.warning('Warning! Loading truncated data for {0}.'.format(obj['handle_name']))

    def load_type(self, type_constructor, di):
        obj = type_constructor(self.bam_file, self.bam_version)
        obj.load(di)
        return obj

    def load(self, di):
        pass

    def write(self, write_version, dg):
        pass
