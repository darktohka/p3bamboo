from panda3d.core import Datagram, DatagramIterator
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
        self.extra_data = b''

    def load_object(self, obj):
        dg = Datagram(obj['data'])
        di = DatagramIterator(dg)
        self.load(di)

        if di.get_remaining_size() > 0:
            self.extra_data = di.get_remaining_bytes()

            if self.bam_file.warn_truncated_data:
                logger.warning('Warning! Loading truncated data for {0}.'.format(obj['handle_name']))

    def write_object(self, write_version, obj):
        dg = Datagram()
        self.write(write_version, dg)

        if self.extra_data:
            dg.append_data(self.extra_data)

            if self.bam_file.warn_truncated_data:
                logger.warning('Warning! Saving truncated data for {0}.'.format(obj['handle_name']))

        obj['data'] = dg.get_message()

    def load_type(self, type_constructor, di):
        obj = type_constructor(self.bam_file, self.bam_version)
        obj.load(di)
        return obj

    def load(self, di):
        pass

    def write(self, write_version, dg):
        pass
