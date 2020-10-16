"""
  P3BABMBOO
  Panda3D BAM file library

  Author: Disyer
  Date: 2020/10/16
"""
class BamFactory(object):
    types = {}

    @staticmethod
    def register_type(handle_name, handle_type):
        if handle_name in self.types:
            raise Exception('Type {0} has already been registered.'.format(handle_name))

        self.types[handle_name] = handle_type

    @staticmethod
    def unregister_type(handle_name):
        if handle_name not in self.types:
            raise Exception('Type {0} has not been registered yet.'.format(handle_name))

        del self.types[handle_name]

    @staticmethod
    def create(bam_file, version, *handle_names):
        for handle_name in self.handle_names:
            if handle_name in self.types:
                return self.types[handle_name](bam_file, version)
